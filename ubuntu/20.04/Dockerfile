FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
apt-get -y install git && \
apt-get -y install cmake && \
apt-get -y install build-essential && \
 apt-get -y install python3-dev python3-pip && \
 apt-get -y install libboost1.67-all-dev  && \
apt-get -y install doxygen && \
pip3 install mako && \
 apt-get -y install libusb-1.0-0-dev && \
 apt-get -y install liborc-0.4-0 && \
pip3  install Cheetah3 && \
pip3  install  requests && \
pip3  install numpy && \
#pip3 install pybind11 && \
pip3 install docutils && \
pip3 install ruamel.yaml && \
pip3 install setuptools && \
find -name "*.py" -or -name '*.py.in' | xargs sed -i "s|#!/usr/bin/env python$|#!/usr/bin/env python3|" 
#WORKDIR /usr/lib/x86_64-linux-gnu
#RUN ls

WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git && \
mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/ \
-D Boost_NO_BOOST_CMAKE:BOOL=0 \
           -DENABLE_PYTHON3=ON \
           -DBOOST_PYTHON_COMPONENT=python38 \
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

RUN apt -y install libgmp-dev swig  \
 python3-sphinx python3-lxml libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 \
liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0  python3-pybind11 libsndfile1-dev
WORKDIR /home
RUN git clone --recursive https://github.com/gnuradio/volk.git
WORKDIR volk
RUN mkdir build
WORKDIR build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make -j4 && \
make install
WORKDIR /home
RUN git clone https://github.com/gnuradio/gnuradio.git
WORKDIR gnuradio
RUN mkdir build
WORKDIR build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make -j4 && \
make install
RUN gnuradio-config-info --version

