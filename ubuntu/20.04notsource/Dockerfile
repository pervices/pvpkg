FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /home/notroot/libuhd
RUN apt-get update && \
apt-get -y install software-properties-common cmake git coreutils build-essential python3-dev python3-pip libboost1.67-all-dev doxygen libusb-1.0-0-dev liborc-0.4-dev && \
pip3  install Cheetah3 && \
pip3  install  requests && \
pip3  install numpy && \
pip3 install pybind11 && \
pip3 install docutils && \
pip3 install ruamel.yaml && \
pip3 install setuptools && \
pip3 install mako && \
git clone https://github.com/pervices/uhd.git
RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/ \
-D Boost_NO_BOOST_CMAKE:BOOL=0 \
           -DENABLE_PYTHON3=ON \
           -DBOOST_PYTHON_COMPONENT=python38 \
        -DPYTHON_INCLUDE_DIR=$(echo /usr/include/python3*) \
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
         /.. && \
make -j4 && \
make install
#add-apt-repository ppa:ettusresearch/uhd && \
#apt-get update && \
#apt-get -y install libuhd-dev libuhd3.15.0 uhd-host && \
RUN add-apt-repository ppa:gnuradio/gnuradio-releases && \
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
