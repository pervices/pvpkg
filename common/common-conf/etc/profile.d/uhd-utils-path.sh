# shellcheck shell=sh

# Expand $PATH to include the directory where uhd example programs are;
uhd_path_utils="/lib/uhd/utils"
if [ -n "${PATH##*${uhd_path_utils}}" ] && [ -n "${PATH##*${uhd_path_utils}:*}" ]; then
    export PATH="$PATH:${uhd_path_utils}"
fi

