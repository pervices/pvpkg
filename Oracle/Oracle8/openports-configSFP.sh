#!/bin/bash

# This script configures network interfaces and firewall rules for
# fiber optic connections on Red Hat Enterprise Linux 8.10.
# It makes persistent changes using NetworkManager's nmcli tool.

#TODO: Ensure this command works safely, with the following

set -Eeuo pipefail

# #Set flags
# # -e : Exit immediately on command failure
# # -o pipefail : propagate exit codes on pipes to right most.
# # -u : treat unset variables as an error
# # -x : print each command prior to executing it.
# # -E : ensure that errors are caught and cleaned up.

# trap "echo Trap was triggered" cleanup SIGINT SIGTERM ERR EXIT

#Synopsis Help:

function help_synopsis {
    echo -e "SYNOPSIS"
    echo -e "\t $0 [ help | <iface_name> <cyan_qSFP_nbr> ]"
    echo -e "Where:"
    echo -e "\t iface_name"
    echo -e "\t\t Interface name to configure."
    echo -e "\t cyan_qSFP_nbr [0|1|2|3]"
    echo -e "\t\t Cyan qSFP port number connected to <iface_name>,"
    echo -e "\t\t with Cyan qSFP+ port A corresponding to 0, Cyan qSFP+ D to 4."
    echo -e ""
    echo -e "For detailed help and example invocations, run:"
    echo -e "\t $0 help"
    exit 1
}

#Detailed Help;
function help_detailed {
    echo -e "USAGE"
    echo -e "\t $0 help"
    echo -e "\t\t Display this detailed help message."
    echo -e ""
    echo -e "\t $0 <InterfaceName> <ChannelNumber>"
    echo -e "\t\t Configure interface for use with Cyan qSFP+ channel number"
    echo -e "Where:\n"
    echo -e "<InterfaceName>"
    echo -e "\t Device name of the network interface you wish to configure."
    echo -e "\t To list all available interfaces, run:"
    echo -e "\t\t ip link show"
    echo -e ""
    echo -e "<ChannelNumber> [0|1|2|3]"
    echo -e "\t The number corresponding to the Cyan SFP+ port connected to"
    echo -e "\t the specified <InterfaceName>, where:"
    echo -e "\t\t Cyan qSFP+ A = 0"
    echo -e "\t\t Cyan qSFP+ B = 1"
    echo -e "\t\t Cyan qSFP+ C = 2"
    echo -e "\t\t Cyan qSFP+ D = 3"
    echo -e ""
    echo -e "EXAMPLES:"
    echo -e "\t After physically connecting the interface \"enp1s0f1\" to the"
    echo -e "\t Cyan qSFP+ port A, run:"
    echo -e "\t\t  $0 enp1s0f1 0"
    echo -e "\t After physically connecting the interface \"enp0s31f6\" to the"
    echo -e "\t Cyan qSFP+ port D, run:"
    echo -e "\t\t  $0 enp0s31f6 3"
    exit 1
}


# If the first argument is help, display detailed help:
if [ "$#" -eq 1 ] && [ "$1" == 'help' ]; then
    help_detailed;
fi

# Display an error if run with incorrect number of arguments:
if [ "$#" -ne 2 ]; then
    echo "ERROR: Invalid Number of Arguments"
    help_synopsis;
fi

##
# Runtime environment checks
##

# Program requires root privileges to configure interfaces and firewall.
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run this program as the root user."
    exit 1
fi


##
# Parse arguments
##

# Assign the first argument to IFACE_NAME
IFACE_NAME=$1
# Assign the second argument to SDR_PORT
SDR_PORT=$2

##
# Core program arguments
##

# Define command shortcuts for easier use and debugging.
CMD_NM=nmcli
CMD_FW=firewall-cmd

#DEBUG:
#CMD_NM="echo nmcli"
#CMD_FW="echo firewall-cmd"

# Main script execution block.
if [ "$#" -eq 2 ]; then
    # --- Network Interface Configuration ---

    # Define the static IP address and gateway based on the provided Cyan port number.
    # The IP address for the host will be 10.10.1<port>.10/24.
    # The gateway is assumed to follow the pattern 10.10.1<port>.1.
    IP_ADDR="10.10.1${SDR_PORT}.10/24"
    GATEWAY="10.10.1${SDR_PORT}.1"

    echo -e "\nConfiguring interface '$IFACE_NAME' with persistent settings..."

    # Use a single, efficient nmcli command to modify all connection properties.
    # This makes the configuration persistent across system reboots.
    $CMD_NM connection modify "$IFACE_NAME" \
        ipv4.method manual \
        ipv4.addresses "$IP_ADDR" \
        ipv4.gateway "$GATEWAY" \
        802-3-ethernet.mtu 9000 \
        ethtool.ring-rx 4096 \
        ethtool.ring-tx 4096 \
        connection.autoconnect yes # This ensures the connection is activated on boot.

    # Bring the connection up to apply the new configuration immediately.
    echo -e "Applying new network configuration to '$IFACE_NAME'..."
    $CMD_NM connection up "$IFACE_NAME"

    # --- Firewall Configuration ---

    # A list of UDP ports that need to be opened in the firewall.
    ports='42836 42837 42838 42839 42840 42841 42842 42843 42809 42810 42811 42812 42799'
    echo -e "\nOpening required firewall ports..."

    # Loop through the list of ports and add a permanent firewall rule for each one.
    for port in $ports
    do
        $CMD_FW --zone=trusted --permanent --add-port=$port/udp
    done

    echo -e "Assigning interface and source IP to the 'trusted' firewall zone..."
    # Add the network interface to the 'trusted' zone permanently.
    $CMD_FW --zone=trusted --permanent --change-interface=$IFACE_NAME

    # Add the corresponding SDR IP address to the 'trusted' zone to allow all traffic from it.
    # This assumes the device at .2 is a trusted source.
    $CMD_FW --zone=trusted --permanent --add-source=10.10.1$SDR_PORT.2

    # Reload the firewall to apply all permanent changes immediately.
    echo "Reloading firewall rules..."
    $CMD_FW --reload

    echo -e "\nConfiguration for '$IFACE_NAME' is complete.\n"
    exit 0
else
    # Fallback to detailed help if argument validation somehow fails.
    help_detailed
    exit 1
fi
