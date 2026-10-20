#!/usr/bin/env python3
"""
network_debug.py - snapshot netstat -i and ethtool -S counters for the
interfaces that route to a fixed set of IPs, then diff against a later
snapshot.

Usage:
    from network_debug import NetworkDebug
    nd = NetworkDebug()      # takes the baseline snapshot
    ...                      # run your test
    nd.compare_to_present()  # prints what changed

Or run directly: it takes a baseline, waits for Enter, then compares.

Requires: iproute2 (ip), net-tools (netstat), ethtool. ethtool -S may need
root on some drivers.
"""

import subprocess
import sys


def _run(cmd):
    """Run a command (list of args, like execvp's argv) and return stdout as
    a string. Raises subprocess.CalledProcessError on non-zero exit."""
    # check=True -> raise on non-zero exit; text=True -> decode bytes to str.
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


class NetworkDebug:
    # Class-level constant (like a static const member in C++).
    TARGET_IPS = ["10.10.10.10", "10.10.11.10", "10.10.12.10", "10.10.13.10"]

    @staticmethod
    def get_interface_for_ip(ip):
        """Return the name of the interface the kernel would use to reach
        `ip`, or None if there is no route."""
        try:
            out = _run(["ip", "route", "get", ip])
        except subprocess.CalledProcessError:
            return None

        # Output looks like:
        #   10.10.10.10 dev eth0 src 10.10.10.1 uid 0
        # The interface name is the token following "dev".
        tokens = out.split()
        if "dev" in tokens:
            idx = tokens.index("dev")
            if idx + 1 < len(tokens):
                return tokens[idx + 1]
        return None

    def __init__(self):
        # Resolve each IP to an interface, dropping duplicates while keeping
        # the original order (a set alone would lose the order).
        self.interfaces = []
        for ip in self.TARGET_IPS:
            iface = self.get_interface_for_ip(ip)
            if iface is None:
                print(f"Warning: no route to {ip}, skipping", file=sys.stderr)
                continue
            if iface not in self.interfaces:
                self.interfaces.append(iface)

        # Each list is index-aligned with self.interfaces: element i holds a
        # dict of {counter_name: value} for self.interfaces[i].
        self.netstat_stats = self._collect_netstat()
        self.ethtool_stats = self._collect_ethtool()

    # ---- collection -------------------------------------------------------

    @staticmethod
    def _parse_netstat_i():
        """Run `netstat -i` once and return {iface: {column: value}}."""
        out = _run(["netstat", "-i"])
        lines = out.splitlines()

        # Skip the "Kernel Interface table" banner; find the header row.
        header = None
        table = {}
        for line in lines:
            fields = line.split()
            if not fields:
                continue
            if fields[0] == "Iface":
                header = fields
                continue
            if header is None:
                continue
            # zip() pairs header[k] with fields[k], like walking two arrays
            # in lockstep; dict() turns those pairs into a map.
            table[fields[0]] = dict(zip(header[1:], fields[1:]))
        return table

    def _collect_netstat(self):
        """Return a list (one entry per interface) of netstat -i rows."""
        table = self._parse_netstat_i()
        stats = []
        for iface in self.interfaces:
            # netstat -i truncates long names; .get() returns {} instead of
            # throwing if the interface isn't found.
            row = table.get(iface)
            if row is None:
                print(f"Warning: {iface} not found in netstat -i output",
                      file=sys.stderr)
                row = {}
            stats.append(row)
        return stats

    @staticmethod
    def _parse_ethtool_s(iface):
        """Run `ethtool -S iface` and return {counter: value}."""
        try:
            out = _run(["ethtool", "-S", iface])
        except subprocess.CalledProcessError as e:
            print(f"Warning: ethtool -S {iface} failed: {e.stderr.strip()}",
                  file=sys.stderr)
            return {}

        # Output looks like:
        #   NIC statistics:
        #        rx_packets: 12345
        stats = {}
        for line in out.splitlines()[1:]:
            # rpartition splits on the LAST ':' -> (before, ':', after), so
            # counter names that themselves contain ':' still parse.
            name, sep, value = line.rpartition(":")
            if sep:
                stats[name.strip()] = value.strip()
        return stats

    def _collect_ethtool(self):
        """Return a list (one entry per interface) of ethtool -S counters."""
        return [self._parse_ethtool_s(iface) for iface in self.interfaces]

    # ---- comparison -------------------------------------------------------

    @staticmethod
    def _diff(old, new):
        """Return a list of (key, old_value, new_value) for keys whose value
        differs or that appear in only one snapshot (missing -> None)."""
        changes = []
        # sorted(set | set) = union of keys from both dicts, in stable order.
        for key in sorted(set(old) | set(new)):
            a = old.get(key)
            b = new.get(key)
            if a != b:
                changes.append((key, a, b))
        return changes

    @staticmethod
    def _format_change(key, a, b):
        """Format one change, adding the numeric delta when both are ints."""
        try:
            delta = int(b) - int(a)
            return f"  {key}: {a} -> {b} ({delta:+d})"
        except (TypeError, ValueError):
            return f"  {key}: {a} -> {b}"

    def _report(self, label, old_list, new_list):
        any_change = False
        for iface, old, new in zip(self.interfaces, old_list, new_list):
            changes = self._diff(old, new)
            if changes:
                any_change = True
                print(f"{label} changes on {iface}:")
                for key, a, b in changes:
                    print(self._format_change(key, a, b))
        if not any_change:
            print(f"No change in {label}")

    def compare_to_present(self):
        """Take a new snapshot and print differences from the baseline taken
        in the constructor. The baseline is not updated."""
        new_netstat = self._collect_netstat()
        new_ethtool = self._collect_ethtool()
        self._report("netstat -i", self.netstat_stats, new_netstat)
        self._report("ethtool -S", self.ethtool_stats, new_ethtool)


# Equivalent of main(): only runs when executed directly, not when imported.
if __name__ == "__main__":
    nd = NetworkDebug()
    print("Interfaces:", ", ".join(nd.interfaces) or "(none)")
    input("Baseline captured. Press Enter to compare...")
    nd.compare_to_present()
