FROM centos:8
# install necessary packages for UHD; necessary to enable powertools repo for some components, as well as pip installing python-related components
RUN yum -y update && \
 dnf -y --enablerepo=powertools install boost-python3-devel && \
dnf -y --enablerepo=powertools install doxygen python3-sphinx SDL-devel && \
 yum -y install git && \
 yum -y install cmake && \
 yum -y install epel-release && \
 yum -y install gcc-c++ make && \
 yum -y install python3-pip  python36-devel && \
 yum -y install libusb libusbx && \
 yum -y install orc && \
 pip3 install mako && \
 pip3 install Cheetah3 && \
 pip3 install numpy && \
pip3 install requests 

# install UHD using cmake, with Python 3 enabled
WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
WORKDIR /home/notroot/libuhd
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
make install && \
ldconfig

# install necessary packages for GnuRadio; ensure version of PyQt5 is set to 5.13.2 to prevent issues; specify LIBRARYPATH and PYTHONPATH as follows
RUN yum -y install gmp-devel swig \
python3-lxml fftw-devel \
gsl-devel qwt-qt5-devel \
#python3-pyqt5-sip \
log4cpp-devel zeromq czmq python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gobject gobject-introspection gtk3 swig && \
pip3 install git+https://github.com/pyqtgraph/pyqtgraph@develop && \
pip3 install scipy && \
pip3 install PyQt5==5.13.2 && \
echo 'export PYTHONPATH=/usr/local/lib/python3.6/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc && \
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc && \
echo 'export PYTHONPATH=/usr/local/lib/python3.6/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.profile && \
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.profile 

# build GnuRadio from Github
WORKDIR /home
RUN git clone --recursive https://github.com/gnuradio/gnuradio
WORKDIR gnuradio
RUN git checkout maint-3.8 && \
mkdir build
WORKDIR build
RUN git pull --recurse-submodules=on && \
git submodule update --init && \
cmake \
 .. && \
make -j4 && \
make install && \
ldconfig
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 
RUN ping 192.168.10.2 -c 5 && \
ping 10.10.10.2 -c 5 && \
ping 10.10.11.2 -c 5 && \
./test-only.sh && \
./test-only.sh







