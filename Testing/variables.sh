###################
##### TESTING #####
###################

V_TEST_NAMES=("Passband Flatness" "TX/RX Fundamental Frequency" "TX Trigger" "TX/RX Gain" "TX/RX Phase Short" "GPIO Stack Test" "RX Stack Test 1"  "RX Stack Test 2"  "TX Stack Test" "TX/RX Stacked Commands" "Tx/Rx Long Phase Coherency Test" "UHD Tx Manual Tuning Test" "UHD Rx Manual Tuning Test" "TX/RX Rate" "RX Rate" "TX Rate")
V_TEST_FILES=(test_passband_flatness test_tx_rx_fundamental_frequency test_tx_trigger test_tx_rx_gain test_tx_rx_phase test_gpio_stack test_rx_stack test_rx_stack_2 test_tx_stack test_tx_rx_stacked_commands test_tx_rx_phase_2 test_tx_uhd_tuning test_rx_uhd_tuning test_tx_rx_rate test_rx_rate test_tx_rate)

L_TEST_NAMES=("Passband Flatness" "TX/RX Fundamental Frequency" "TX Trigger" "TX/RX Gain" "TX/RX Phase Short" "RX Stack Test 1"  "RX Stack Test 2"  "TX Stack Test" "TX/RX Stacked Commands" "Tx/Rx Long Phase Coherency Test" "UHD Tx Manual Tuning Test" "UHD Rx Manual Tuning Test" "TX/RX Rate" "RX Rate" "TX Rate")
L_TEST_FILES=(test_passband_flatness test_tx_rx_fundamental_frequency test_tx_trigger test_tx_rx_gain test_tx_rx_phase test_rx_stack test_rx_stack_2 test_tx_stack test_tx_rx_stacked_commands test_tx_rx_phase_2 test_tx_uhd_tuning test_rx_uhd_tuning test_tx_rx_rate test_rx_rate test_tx_rate)

# Currently we run the same list of tests on Crimson and Cyan
T_TEST_NAMES=("${V_TEST_NAMES[@]}")
T_TEST_FILES=("${V_TEST_FILES[@]}")

