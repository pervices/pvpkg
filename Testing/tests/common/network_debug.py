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

Requires: iproute2 (ip), net-tools (netstat), ethtool. ethtool -S may need
root on some drivers.
"""

import subprocess
import sys


def _run(cmd):
    """Run a command (list of args) and return stdout as
    a string. On non-zero exit, prints the failing command and exit code,
    then re-raises subprocess.CalledProcessError."""
    try:
        # check=True -> raise on non-zero exit
        # text=True -> decode bytes to str.
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # " ".join(list) concatenates the list cmd with " " between it's elements
        print(f'"{" ".join(cmd)}" failed with exit code "{e.returncode}"', file=sys.stderr)
        # Reraise the error so the caller needs to handle it
        raise
    return result.stdout


# Per-queue statistics have the queue number in their name (rx-11.packets).
# Queues numbered at or above this are not in the ignore list, so they print.
_MAX_QUEUES = 256


def _build_ignored_stats():
    """Return the set of statistic names that only measure traffic volume.
    A name must match an entry exactly to be ignored; anything not listed,
    including counters added by a new driver or firmware, is always printed."""
    ignored = set()

    # netstat -i statistics to ignore ----------

    # packets transferred successfully.
    ignored.update(["RX-OK", "TX-OK"])

    # ethtool -S statistics to ignore ----------

    # ethtool -S totals, shared by most drivers. "port." versions are the
    # ice driver's physical-port totals.

    # "" is the stats for the logical interface seen by the kernel
    # port is from the ice driver and refers to physical port
    for prefix in ["", "port."]:
        for direction in ["rx", "tx"]:
            # bytes: how many bytes were in successfully sent packets
            # packets: how many packets were successfull sent
            # unicats: how many packets were addressed to a specific MAC address
            # multicast: how many packets were addressed to a multicast group MAX address
            # broadcast: how many packets were addressed to every host on the segment
            for kind in ["bytes", "packets", "unicast", "multicast", "broadcast"]:
                ignored.add(f"{prefix}{direction}_{kind}")

    # How many ethernet frames were received/sent by the ice driver where size[n-1] < x <= size[n].
    for direction in ["rx", "tx"]:
        for size in ["64", "127", "255", "511", "1023", "1522", "big"]:
            ignored.add(f"port.{direction}_size_{size}")

    # Duplicate of rx_bytes on 64 bit systems.
    ignored.add("rx_long_byte_count")

    # Number of receive buffers recycled in the ice driver
    ignored.add("rx_cache_reuse")

    # Per-queue byte/packet totals.
    for n in range(_MAX_QUEUES):
        for direction in ["rx", "tx"]:
            for kind in ["bytes", "packets"]:
                ignored.add(f"{direction}-{n}.{kind}")          # ice
                ignored.add(f"{direction}_queue_{n}_{kind}")    # igb

    # frozenset is an immutable set, so the list can't be modified by accident.
    return frozenset(ignored)


class NetworkDebug:
    # Constant list of IPs/netmasks to check
    TARGET_IPS = ["192.168.10.0/24", "192.168.11.0/24", "10.10.10.0/24", "10.10.11.0/24", "10.10.12.0/24", "10.10.13.0/24"]

    # Statistics whose changes are expected during a test and are not printed.
    IGNORED_STATS = _build_ignored_stats()

    @staticmethod
    def get_interface_for_ip(ip):
        """Return the name of the interface on this host that has `ip`
        assigned, or None if no interface has it."""
        # `ip -o addr show to <ip>` lists only interfaces that own ip, not IPs reachable through it
        try:
            out = _run(["ip", "-o", "addr", "show", "to", ip])
        except subprocess.CalledProcessError:
            return None

        # Output of ip -o addr show to 10.10.10.10 looks like:
        #   3: eth0    inet 10.10.10.10/24 brd 10.10.10.255 scope global eth0 ...
        # The interface name is the second whitespace-separated field (eth0).

        # Create a list of devices with the target IP.
        devs = []
        for line in out.splitlines():
            fields = line.split()
            if len(fields) >= 2:
                # VLAN/macvlan names show as "eth0.100@eth0";
                # Keep the part before '@' which is the name ethtool/netstat expect.
                # For most interfaces the split does nothing.
                devs.append(fields[1].split("@")[0])

        # No matching network interfaces found.
        if not devs:
            return None

        # Multiple devices have the target IP, which indicates a configuration error.
        if len(devs) > 1:
            #
            raise RuntimeError(
                f"ERROR: multiple devices ({', '.join(devs)}) own {ip}. "
                "IPs should not be owned by multiple network interfaces.")
        return devs[0]


    def __init__(self):
        self.interfaces = []
        for ip in self.TARGET_IPS:
            # Get the interface
            iface = self.get_interface_for_ip(ip)
            if iface is None:
                print(f"No interface on this host has an address matching {ip}, skipping.")
                continue
            # Add interface to the list of interfaces to check if it is not already in the list (avoid duplicates)
            if iface not in self.interfaces:
                self.interfaces.append(iface)

        # Print a warning if no interfaces are detected, otherwise the output would look clean
        if not self.interfaces:
            print("Warning: none of the target IPs are assigned on this host; "
                  "no interfaces will be checked.", file=sys.stderr)

        # Store initial netstat -i info
        self.netstat_stats = self._collect_netstat()
        # Store initial ethtool -S info
        self.ethtool_stats = self._collect_ethtool()

    # ---- collection -------------------------------------------------------

    @staticmethod
    def _parse_netstat_i():
        """Run `netstat -i` once and return a nested dict of {iface: {column: value}}."""
        out = _run(["netstat", "-i"])
        lines = out.splitlines()

        # Column titles
        header = None

        table = {}
        for line in lines:
            # The current line
            fields = line.split()
            # Skip blank lines
            if not fields:
                continue
            # Get the column title
            if fields[0] == "Iface":
                header = fields
                continue
            # Skip every line before the column titles are set. (Skip the line "Kernel Interface table")
            if header is None:
                continue
            # Add an entry to the dict for fields[0] (the interfact name) containing tuples (column_name[n], value[n]);
            # zip converts the column name slice (header[1:]) and value (fields[1:]) to tuples
            table[fields[0]] = dict(zip(header[1:], fields[1:]))
        return table

    def _collect_netstat(self):
        """Return a list of dicts {column: value} from netstat -i containing the relevant interfaces."""
        # Get netstat -i for all interfaces
        table = self._parse_netstat_i()
        stats = []
        # For every relevant interface
        for iface in self.interfaces:
            # Get the values returns by netstat for the given relevant interface.
            row = table.get(iface)
            if row is None:
                print(f"Warning: {iface} not found in netstat -i output", file=sys.stderr)
                row = {}
            # Add the stats for the relevant interface to the dict to return.
            stats.append(row)
        return stats

    @staticmethod
    def _parse_ethtool_s(iface):
        """Run `ethtool -S iface` and return a dict {statistic: value}."""
        try:
            out = _run(["ethtool", "-S", iface])
        except subprocess.CalledProcessError:
            print(f"ERROR: unable to run ethtool for {iface}.", file=sys.stderr)
            # Treat failed ethtool -S as if the interface does not support any statistics.
            return {}

        # Output of ethtool -S looks like:
        #   NIC statistics:
        #        rx_packets: 12345
        stats = {}
        # For every line except the first line since the first line just contains "NIC statistics:".
        for line in out.splitlines()[1:]:
            # Extract the name and value of the stat in this line
            name, sep, value = line.rpartition(":")
            # If the value was extracted successfully
            if sep:
                # Add an entry to the dict with whitespace removed
                stats[name.strip()] = value.strip()

        # ethtool succeeded but reported no parsable statistics
        # Print a warning to avoid looking clean
        if not stats:
            print(f"Warning: ethtool -S {iface} returned no statistics", file=sys.stderr)
        return stats

    def _collect_ethtool(self):
        """Return a list (one entry per interface) of dicts containing ethtool -S's statistics."""
        stats = []
        for iface in self.interfaces:
            stats.append(self._parse_ethtool_s(iface))
        return stats

    # ---- comparison -------------------------------------------------------

    @staticmethod
    def _diff(old, new):
        """Return a list of tuples (key, old_value, new_value) for keys whose value
        differs or that appear in only one snapshot (missing -> None).
        old and new are dicts of key/value for an interface.
        Not to be confused with the list that contains the dicts for each interface."""
        changes = []
        # For every key in either old or new
        for key in sorted(set(old) | set(new)):
            old_value = old.get(key)
            new_value = new.get(key)
            # If the value changed add it to the list of changes
            if old_value != new_value:
                changes.append((key, old_value, new_value))
        return changes

    @staticmethod
    def _format_change(key, a, b):
        """Create string for future printing to show the comparison between the new and old value.
        Include the difference if applicable."""
        try:
            delta = int(b) - int(a)
            # Example output: TX-DRP: 560 -> 566 (+6)
            return f"  {key}: {a} -> {b} ({delta:+d})"
        except (TypeError, ValueError):
            return f"  {key}: {a} -> {b}"

    def _report(self, label, old_list, new_list):
        """Print changes between old_list and new_list, except for statistics
        in IGNORED_STATS. label is the source of the list. (i.e. netstat)
        Returns a tuple (total changes, unexpected changes printed)."""
        total_changes = 0
        unexpected_changes = 0

        for iface, old, new in zip(self.interfaces, old_list, new_list):
            # Get the difference's for this interface's dict.
            changes = self._diff(old, new)
            total_changes += len(changes)

            # Keep only the changes that aren't known traffic-volume stats.
            unexpected = []
            for key, a, b in changes:
                if key not in self.IGNORED_STATS:
                    unexpected.append((key, a, b))

            # Print changes that might indicate something going wrong
            if unexpected:
                unexpected_changes += len(unexpected)
                print(f"{label} changes on {iface}:")
                for key, a, b in unexpected:
                    print(self._format_change(key, a, b))

        return total_changes, unexpected_changes

    def compare_to_present(self):
        """Print the differences between the original values returned by netstat -i ethtool -S and
        their current value, skipping expected traffic-volume statistics."""

        # Print a warning no matching network interfaces were found to avoid looking clean
        if not self.interfaces:
            print("Warning: network statistics not compared; no interfaces to check", file=sys.stderr)
            return

        # Get the new values of netstat -i and ethtool -S
        new_netstat = self._collect_netstat()
        new_ethtool = self._collect_ethtool()
        # Print the comparison
        netstat_total, netstat_unexpected = self._report("netstat -i", self.netstat_stats, new_netstat)
        ethtool_total, ethtool_unexpected = self._report("ethtool -S", self.ethtool_stats, new_ethtool)

        # Nothing changed at all, not even traffic counters: no traffic reached
        # these interfaces, so a clean result would be meaningless.
        if netstat_total + ethtool_total == 0:
            print("Warning: no network statistics changed on any interface; "
                  "no traffic was detected", file=sys.stderr)

        if netstat_unexpected + ethtool_unexpected == 0:
            print("No unexpected changes in network statistics detected")


# If this script is called directly
if __name__ == "__main__":
    # Capture initial values
    nd = NetworkDebug()
    print("Interfaces:", ", ".join(nd.interfaces) or "(none)")
    # Wait for the user to hit enter
    input("Baseline captured. Press Enter to compare...")
    # Check the new values and print them if they differ
    nd.compare_to_present()