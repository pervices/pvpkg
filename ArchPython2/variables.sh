###########################
##### NAMING UTILITIES #####
############################

PROJECT="crimson"                       # Change this line when changing systems
PROJECT_INT="vaunt"                     # Change this line when changing systems
ARCH="cortexa9hf_vfp_neon"
YOCTO_BUILD_DIR="v_curr_build"

ALL_COMPONENTS="mcu fpga firmware website"

MCU_RPM_NAME="$PROJECT-mcu-1.0-r0.0.$ARCH.rpm"
FPGA_RPM_NAME="$PROJECT-fpga-1.1-r0.0.$ARCH.rpm"
FIRMWARE_RPM_NAME="$PROJECT-firmware-1.0-r0.0.$ARCH.rpm"
WEBSITE_RPM_NAME="$PROJECT-website-1.0-r0.0.$ARCH.rpm"

MCU_VERSION_NAME="MCU"
FPGA_VERSION_NAME="FPGA"
FIRMWARE_VERSION_NAME="FIRMWARE"
WEBSITE_VERSION_NAME="WEB"

MCU_VERSION_LENGTH=8
FPGA_VERSION_LENGTH=9
FIRMWARE_VERSION_LENGTH=8
WEBSITE_VERSION_LENGTH=40

###################
##### TESTING #####
###################

NUM_TESTS=6
TEST_NAMES=("TX Trigger" "TX/RX Gain" "TX/RX Fundamental Frequency" "TX/RX Phase" "TX/RX Stacked Commands" "TX/RX Channels In-Phase")
TEST_FILES=(test_tx_trigger test_tx_rx_gain test_tx_rx_fundamental_frequency test_tx_rx_phase test_tx_rx_stacked_commands test_tx_rx_channels_in_phase)

##########################
##### FILE LOCATIONS #####
##########################

TESTS=/home/$HOST_USER/ci-tests

FTP_DUMP_NAME='/tmp/rebuild-$PROJECT-$COMPONENT-$DATE'

UPDATE_DIR_NAME='/tmp/update-$PROJECT-$COMPONENT-$DATE'
UPDATE_NAME=$PROJECT\_update_$DATE

WORK_DIR_NAME='/tmp/$COMPONENT-test-latest-$DATE'
WORK_DIR_STABLE_NAME='/tmp/$COMPONENT-test-stable-$DATE'

TRANSFER_DIR_NAME='/tmp/$COMPONENT-buildtohost-transfer-$DATE'

