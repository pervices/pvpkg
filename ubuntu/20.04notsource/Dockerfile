FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install dpkg-dev sudo dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \ 
apt-get -y install python3-dev python3-pip libboost1.67-all-dev doxygen libusb-1.0-0-dev liborc-0.4-dev && \
pip3 install mako Cheetah3 requests numpy docutils ruamel.yaml setuptools
WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git && \
mkdir uhdlib
WORKDIR /home/notroot/libuhd
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
         /home/uhd/host && \
make -j4 && \
make install
WORKDIR /home/notroot/libuhd
RUN apt-get update && \
apt-get -y -f install libgmp-dev swig python3-pybind11  \
 python3-sphinx python3-lxml libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev  \
liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0 libsndfile1-dev && \
pip3 install pyqt5 && \
pip3 install --user --upgrade construct requests

# install volk and gnuradio separately, as is required for the most recent Ubuntu 20.04 version; specify Python3 in cmake as shown
WORKDIR /home
RUN git clone --recursive https://github.com/gnuradio/volk.git
WORKDIR volk
RUN mkdir build
WORKDIR build
RUN  ls && cmake \
 -DCMAKE_BUILD_TYPE=Release \
 -DPYTHON_EXECUTABLE=/usr/bin/python3 \
 -DPYTHON_INCLUDE_DIR=$(echo /usr/include/python3*) \
 -DPYTHON_LIBRARY=$(echo /usr/lib/libpython3.*.so) \
../ && \
make -j4 && \
make install
WORKDIR /home
RUN git clone https://github.com/gnuradio/gnuradio.git
WORKDIR gnuradio
RUN mkdir build
WORKDIR build
RUN ls && cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make -j4 && \
make install
RUN ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
apt-get -y install sudo && \
apt-get -y install net-tools iputils-ping && \ 
ldconfig && \
gnuradio-config-info --prefix && \
find /usr/local -name gnuradio | grep "packages" && \
echo "export PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH" >> ~/.bashrc && \
echo "export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH" >> ~/.bashrc && \
echo "export PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH" >> ~/.profile && \
echo "export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH" >> ~/.profile 
RUN ldconfig && \
python3 -m site --user-site && \
python3 --version && \ 
sleep 10000 && \
./test-only.sh 
