###################
##### TESTING #####
###################

V_TEST_NAMES=("TX/RX Fundamental Frequency" "TX Trigger" "TX/RX Gain" "Tx/Rx Long Phase Coherency Test" "GPIO Stack Test" "RX Stack Test 1"  "RX Stack Test 2"  "TX Stack Test" "TX/RX Stacked Commands" "UHD Tx Manual Tuning Test" "UHD Rx Manual Tuning Test", "Channel Alignment Test")
V_TEST_FILES=(test_tx_rx_fundamental_frequency test_tx_trigger test_tx_rx_gain test_tx_rx_phase test_gpio_stack test_rx_stack test_rx_stack_2 test_tx_stack test_tx_rx_stacked_commands test_tx_uhd_tuning test_rx_uhd_tuning test_channel_alignment)

T_TEST_NAMES=("TX/RX Fundamental Frequency" "TX Trigger" "TX/RX Gain" "Tx/Rx Long Phase Coherency Test" "GPIO Stack Test" "RX Stack Test 1"  "RX Stack Test 2"  "TX Stack Test" "TX/RX Stacked Commands" "UHD Tx Manual Tuning Test" "UHD Rx Manual Tuning Test", "Channel Alignment Test")
T_TEST_FILES=(test_tx_rx_fundamental_frequency test_tx_trigger test_tx_rx_gain test_tx_rx_phase test_gpio_stack test_rx_stack test_rx_stack_2 test_tx_stack test_tx_rx_stacked_commands test_tx_uhd_tuning test_rx_uhd_tuning, test_channel_alignment)

FTP_USER=img
FTP_PW=img
FTP_ADD=korbin.pv
FTP_UPLOAD_DIR=ftp/ci/report
SSL_CERT="set ssl:verify-certificate no"

