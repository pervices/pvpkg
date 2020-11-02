FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
apt-get -y install git && \
apt-get -y install cmake && \
apt-get -y install build-essential && \
 apt-get -y install python3.6 python3-pip && \
 apt-get -y install libboost-all-dev && \
apt-get -y install doxygen && \
pip3 install mako && \
 apt-get -y install libusb-1.0-0-dev && \
 apt-get -y install liborc-0.4-0 && \
pip3  install Cheetah3 && \
pip3  install  requests && \
pip3  install numpy
#find -name "*.py" -or -name '*.py.in' | xargs sed -i "s|#!/usr/bin/env python$|#!/usr/bin/env python2|"


WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git && \
mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/ \
           -DENABLE_PYTHON3=ON \
           -DENABLE_EXAMPLES=ON \
           -DENABLE_UTILS=ON \
           -DENABLE_TESTS=OFF \
           -DENABLE_E100=OFF \
	   -DENABLE_N230=OFF \
	   -DENABLE_N300=OFF \
	   -DENABLE_E320=OFF \
	   -DENABLE_USRP1=OFF \
	   -DENABLE_USER2=OFF \
	   -DENABLE_B200=OFF \
	   -DENABLE_X300=OFF \
       -DENABLE_CRIMSON_TNG=ON \
       -DENABLE_CYAN_16T=OFF \
       -DENABLE_CYAN_64T=OFF \
	   -DENABLE_OCTOCLOCK=OFF \
	   -DENABLE_DOXYGEN=OFF \
	   -DENABLE_USB=OFF \
         /home/uhd/host && \
make -j4 && \
make install
