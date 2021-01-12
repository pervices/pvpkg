FROM ubuntu:18.04
# install necessary components for UHD; install some Python components using pip
RUN apt update && \
 apt-get -y install git && \
 apt-get -y install cmake && \
 apt-get -y install build-essential && \
 apt-get -y install python3.6 python3-pip && \
 apt-get -y install libboost-all-dev && \
 pip3 install mako && \
 apt-get -y install libusb-1.0-0-dev && \
 apt-get -y install liborc-0.4-0 && \
 apt-get -y install doxygen && \
pip3 install Cheetah3 && \
pip3 install numpy && \
pip3 install requests
 #find -name "*.py" -or -name '*.py.in' | xargs sed -i "s|#!/usr/bin/env python$|#!/usr/bin/env python2|"

# install UHD using cmake, specifying Python3 in options
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
make test && \
 make install && \
ldconfig

# set environemnt to non-interactive to stop input prompts that occurred on certain instructions
ENV DEBIAN_FRONTEND=noninteractive

# install necessary packages for GnuRadio; specify LIBRARYPATH and PYTHONPATH as follows
RUN apt -y install libgmp-dev swig python3-sphinx python3-lxml libfftw3-dev libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev \
 python3-pyqt5 liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins python3-zmq python3-scipy python3-gi-cairo gir1.2-pango-1.0 libgtk-3-dev && \
pip3 install git+https://github.com/pyqtgraph/pyqtgraph@develop && \
pip3 install scipy 


# build GnuRadio from Github
WORKDIR /home
RUN git clone --recursive https://github.com/gnuradio/gnuradio
WORKDIR gnuradio
RUN git checkout maint-3.8 && \
mkdir build
WORKDIR build
RUN git pull --recurse-submodules=on && \
git submodule update --init && \
cmake .. && \
make -j $(nproc --all) && \
make install && \
uhd_find_devices --args="addr=192.168.10.2" && \
uhd_usrp_probe --args=name= FPGA




