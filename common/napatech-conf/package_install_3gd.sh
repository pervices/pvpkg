#!/usr/bin/env bash
#
# package_install_3gd.sh
#

# Default install path
INSTALL_PATH=/opt/napatech3

# Default install options
OPT_INSTALL_ACTION=""
OPT_INSTALL_NOPROMPT=0
OPT_INSTALL_NOX11=0
OPT_INSTALL_PCAP_VER=
OPT_INSTALL_NOROOTCHECK=0

# Misc. options
do_pcap=0

# Available pcap versions
pcap_vers[1]=1.10.0
pcap_vers[2]=1.9.1
pcap_vers[3]=1.8.1

#
# show_usage
#
show_usage()
{
cat << EOB
Usage: ${SCRIPTNAME} [OPTIONS]

Options:
   --help         : This help text
   --noprompt     : Do not prompt during install - this implies that an existing
                    installation is updated and that no pcap is installed.
                    The Napatech Software Suite is covered by the Napatech Software
                    license agreement as described in "NP-0405 Napatech Software
                    license agreement.pdf" By installing any part of the software
                    suite you accept the license agreement.
   --pcap <ver>   : Specify pcap version to install (${pcap_vers[@]})
   --del          : Delete existing installation
   --upd          : Update existing installation
   --nox11        : Do not spawn a X11 terminal
   --norootcheck  : Do not check if install runs as root

EOB
    exit
}

#
# initial checks
#
perform_checks()
{
# check bash
if test -z "${BASH_VERSION}"; then
    echo "You need bash for this script"
    exit 1
fi

# Get platform
PLATFORM=`uname | tr "[A-Z]" "[a-z]"`


# Set platform defaults
case $PLATFORM in
  linux)
    CMD_STAT=lsmod
    ;;
  freebsd)
    CMD_STAT=kldstat
    ;;
  *)
    echo "Platform [$PLATFORM] is not supported. We can only run on Linux and FreeBSD."
    exit 1
esac

# check if driver has already been loaded
if [ "`$CMD_STAT | grep -c nt3gd`" != "0" ]; then
    echo "Napatech driver already loaded. Please unload the driver before running this script."
    exit 1
fi

}

#
# perform install
#
perform_install()
{
  if [ ${OPT_INSTALL_NOPROMPT} != 1 ]; then
    echo
    echo "The Napatech Software Suite is covered by the Napatech Software license"
    echo "agreement as described in \"NP-0405 Napatech Software license agreement.pdf\""
    echo "By installing any part of the software suite you accept the license agreement."
    echo

    while [ 1 ]; do
      echo -n "I accept the license [Y]es/[N]o: "
      read S
      echo
      S=`echo -n $S | tr "[A-Z]" "[a-z]" | cut -c1-1`
      case $S in
        y)
          break
          ;;
        n)
          echo "You need to accept the license to install the software."
          exit 0
          ;;
        *)
          echo "Invalid option"
          ;;
      esac
    done
  fi



# Only show delete option for complete packages
if [ -d software ] && [ -d tools ]; then
    SHOW_DELETE=1
else
    SHOW_DELETE=0
fi

# Check for previous installation
if [ -d ${INSTALL_PATH} ]; then
    echo "An existing Napatech driver installation has been detected."

    if [ ${OPT_INSTALL_NOPROMPT} != 0 -a x"${OPT_INSTALL_ACTION}" = x ]; then
        echo
        echo "The Napatech Software Suite is covered by the Napatech Software license"
        echo "agreement as described in \"NP-0405 Napatech Software license agreement.pdf\""
        echo "By installing any part of the software suite you accept the license agreement."
        echo
        echo "NOTE: 'noprompt' option is enabled - existing Napatech driver installation will be updated."
        echo
        OPT_INSTALL_ACTION="u"
    fi
fi

if [ -d ${INSTALL_PATH} -a ${OPT_INSTALL_NOPROMPT} = 0 -a x"${OPT_INSTALL_ACTION}" = x ]; then
    echo
    echo "How do you wish to proceed?:"
    echo "  Update : This will update the previous installation. (Recommended)"
    if [ $SHOW_DELETE -eq 1 ]; then
        echo "  Delete : This will delete the previous installation entirely before"
        echo "           commencing the new installation."
    fi
    echo "  Quit   : Quit installation."

    while [ 1 ]; do
        if [ $SHOW_DELETE -eq 1 ]; then
            echo -n "Answer ([U]pdate/[D]elete/[Q]uit): "
        else
            echo -n "Answer ([U]pdate/[Q]uit): "
        fi

        read S
        echo
        S=`echo -n $S | tr "[A-Z]" "[a-z]"`
        case $S in
            u)
                OPT_INSTALL_ACTION="u"
                break
                ;;
            d)
                if [ $SHOW_DELETE -eq 1 ]; then
                    OPT_INSTALL_ACTION="d"
                    break
                else
                    echo "Invalid option"
                fi
                ;;
            q)
                exit 0
                ;;
            *)
                echo "Invalid option"
                ;;
        esac
    done
fi

# Get or check pcap options
pcap_valid=0
setup_ini=0
if [ -d pcap -a ${OPT_INSTALL_NOPROMPT} = 0 -a x${OPT_INSTALL_PCAP_VER} = x  ]; then
    echo "[ Extract, compile and install Napatech libpcap ]"
    echo "Select libpcap version to install:"
    echo "1) libpcap-1.10.0"
    echo "2) libpcap-1.9.1"
    echo "3) libpcap-1.8.1"
    echo "4) Don't install libpcap"

    while [ 1 ]; do
        read S
        echo
        case "$S" in
            1|2|3)
                OPT_INSTALL_PCAP_VER=${pcap_vers[$S]}
                do_pcap=1
                break
                ;;
            4)
                break
                ;;
            *)
                echo -en "Please select 1-4\nAnswer:"
                ;;
        esac
    done
fi
for v in ${pcap_vers[@]}; do
    if [ "$v" = "$OPT_INSTALL_PCAP_VER" ]; then
        OPT_INSTALL_PCAP_VER=libpcap-$OPT_INSTALL_PCAP_VER
        pcap_valid=1
        do_pcap=1
        break
    fi
done
if [ $do_pcap = 1 -a $pcap_valid = 0 ]; then
    echo "Wrong libpcap version requested"
    exit 1
fi

if [ x"$OPT_INSTALL_ACTION" = x"d" ]; then
    echo "Deleting previous installation"
    rm -rf ${INSTALL_PATH}
fi

# Install documentation
if [ -d documentation ]; then
    echo "[ Install documentation ]"
    mkdir -p ${INSTALL_PATH}/doc
    cd documentation
    files=$(ls * 2> /dev/null | wc -l)
    if [ "$files" != "0" ]; then
        cp -f -R * ${INSTALL_PATH}/doc/.
    fi
    cd ..
fi

# Build makeself options
MAKESELF_OPTIONS=""
if test ${OPT_INSTALL_NOX11} -ne 0; then
    MAKESELF_OPTIONS="--nox11"
fi
# Build tools and driver install options
INSTALL_OPTIONS="--yestoall"
if test ${OPT_INSTALL_NOROOTCHECK} -ne 0; then
    INSTALL_OPTIONS+=" --norootcheck"
fi

# Install tools
if [ -d tools ]; then
    echo "[ Extract and install tools ]"
    cd tools
    ./nt_tools*.run ${MAKESELF_OPTIONS} -- ${INSTALL_OPTIONS}
    if [ $? -ne 0 ]; then
        echo "Tools installation failed. Aborting installation."
        exit 1
    fi
    cd ..
fi

# Install driver
if [ -d software ]; then
    echo "[ Extract and build driver ]"
    cd software
    for filename in nt_driver_*.run; do
        ./${filename} ${MAKESELF_OPTIONS} -- ${INSTALL_OPTIONS}
    done
    if [ $? -ne 0 ]; then
        echo "Driver installation failed. Aborting installation."
        exit 1
    fi
    cd ..
fi

# Install imgctrl
if [ -d imgctrl ]; then
    echo "[ Install the Image control application ]"
    cd imgctrl
    mkdir -p ${INSTALL_PATH}/bin
    cp -f imgctrl ${INSTALL_PATH}/bin
    cd ..
fi

# Install Test Tools
if [ -d testtools ]; then
    echo "[ Extract and install the Test Tools ]"
    cd testtools
    mkdir -p build
    cd build
    tar xvfz ../nt_testtools_*.tar.gz
    cd bin
    mkdir -p ${INSTALL_PATH}/tbin
    files=$(ls -1 nt_testtool_* 2> /dev/null | wc -l)
    if [ "${files}" != "0" ]; then
        cp -f nt_testtool_* ${INSTALL_PATH}/tbin
    fi
    cd ..
    cd ..
    cd ..
fi

# Install images
if [ -d images ]; then
    echo "[ Install FPGA images ]"
    cd images
    mkdir -p ${INSTALL_PATH}/images
    files=$(ls * 2> /dev/null | wc -l)
    if [ "$files" != "0" ]; then
        cp -R -f * ${INSTALL_PATH}/images
    fi
    cd ..
fi

# Install libpcap
if [ "$do_pcap" -eq "1" ]; then
    echo "[ Install libpcap ]"
    cd pcap
    mkdir -p build
    cd build
    cp  -R -f ../libpcap-* .
    cd ${OPT_INSTALL_PCAP_VER}
    rm -f ${INSTALL_PATH}/lib/libpcap*
    ./configure --prefix=${INSTALL_PATH} napatech3g_root=${INSTALL_PATH}
    if [[ "$PLATFORM" != "linux" ]]; then
        gmake shared install install-shared
        ldconfig -m ${INSTALL_PATH}/lib
    else
        make shared install install-shared
        ldconfig -f /etc/ld.so.conf
    fi
    if [ ! -f "${INSTALL_PATH}/config/ntpcap.ini" ]; then
      # If ntpcap.ini does not exsists then copy it
      cp ./ntpcap.ini ${INSTALL_PATH}/config
    fi
    cd ..
    rm -rf build
    cd ..
fi

if [ $PLATFORM == "linux" ]; then
    RESTORECON=`which restorecon 2>/dev/null`
    if [ $? -eq 0 ]; then
        $RESTORECON -RF $INSTALL_PATH 2>/dev/null

        if [ $? -ne 0 ]; then
            echo "Error setting SELinux labels"
        fi
    fi
fi


echo "[ Package installation done... ]"

}

#
# parse options
#
parse_options()
{
    #Parse the script parameters
    i=0
    while test -n "$1"; do
        nocasearg=`echo -n $1 | tr "[A-Z]" "[a-z]"`
        shift
        i=$((i+1))
        case $nocasearg in
            -h|--help|-help)
                show_usage
                exit 0
                ;;
            --noprompt)
                OPT_INSTALL_UPDATE=1
                OPT_INSTALL_NOPROMPT=1
                ;;
            --pcap)
                OPT_INSTALL_PCAP_VER=${pcap_vers[1]}
                do_pcap=1
                if [[ "$1" =~ ^[0-9].* ]]; then
                  OPT_INSTALL_PCAP_VER=$1
                  shift
                fi
                ;;
            --upd)
                if [ x"$OPT_INSTALL_ACTION" != x ]; then
                    echo "Error: multiple install actions not allowed"
                    exit 1
                fi
                OPT_INSTALL_ACTION="u"
                ;;
            --del)
                if [ x"$OPT_INSTALL_ACTION" != x ]; then
                    echo "Error: multiple install actions not allowed"
                    exit 1
                fi
                OPT_INSTALL_ACTION="d"
                ;;
            --nox11)
                OPT_INSTALL_NOX11=1
                ;;
            --norootcheck)
                OPT_INSTALL_NOROOTCHECK=1
                ;;
            *)
                echo -e "\nParameter $i is unknown: $nocasearg\n"
                show_usage
                exit 1
                ;;
        esac
    done
}

#
# check_options
#
check_options()
{
    return 0
}

###############################################################################
###################### Main Script Execution Point ############################
###############################################################################

SCRIPTNAME=${0##*/}

# Parse command line options
parse_options "${@}"

# check options
check_options

# perform initial checks
perform_checks

# perform installation
perform_install

#
# EOF
#
