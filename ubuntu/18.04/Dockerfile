FROM ubuntu:18.04

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

ENV DEBIAN_FRONTEND=noninteractive
RUN apt -y install libgmp-dev swig python3-sphinx python3-lxml libfftw3-dev libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev \
 python3-pyqt5 liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins python3-zmq python3-scipy python3-gi-cairo gir1.2-pango-1.0 libgtk-3-dev && \
pip3 install git+https://github.com/pyqtgraph/pyqtgraph@develop && \
pip3 install scipy 
#echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc
#echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
#echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.profile
#echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.profile
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
make install
RUN 
uhd_find_devices --args="type=usrp1"
