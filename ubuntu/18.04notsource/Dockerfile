FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install sudo iputils-ping net-tools software-properties-common cmake git coreutils build-essential python3.6 python3-pip libboost-all-dev doxygen libusb-1.0-0-dev liborc-0.4-dev && \
pip3  install Cheetah3 && \
pip3  install  requests && \
pip3  install -U numpy && \
pip3  install -U scipy && \
pip3 install pybind11 && \
pip3 install docutils && \
pip3 install ruamel.yaml && \
pip3 install setuptools && \
pip3 install mako && \
pip3 install retrying 
WORKDIR /home
RUN apt-get update && \
add-apt-repository ppa:gnuradio/gnuradio-releases-3.8 && \
apt-get update && \
apt-get -y install gnuradio
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
ldconfig && \
./test-only.sh
