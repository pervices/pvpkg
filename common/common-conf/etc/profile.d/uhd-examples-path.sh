# shellcheck shell=sh

# Expand $PATH to include the directory where uhd example programs are;
uhd_path_examples="/lib/uhd/examples"
if [ -n "${PATH##*${uhd_path_examples}}" ] && [ -n "${PATH##*${uhd_path_examples}:*}" ]; then
    export PATH="$PATH:${uhd_path_examples}"
fi

