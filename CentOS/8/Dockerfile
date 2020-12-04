FROM centos:8

RUN yum -y update && \
 dnf -y --enablerepo=PowerTools install boost-python3-devel && \
dnf -y --enablerepo=PowerTools install doxygen python3-sphinx SDL-devel && \
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

RUN yum -y install gmp-devel swig \
python3-lxml fftw-devel \
gsl-devel qwt-qt5-devel python3-pyqt5-sip \
log4cpp-devel zeromq czmq python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gobject gobject-introspection gtk3 && \
pip3 install git+https://github.com/pyqtgraph/pyqtgraph@develop && \
pip3 install scipy 
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.profile
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.profile
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
make install
RUN ping 192.168.10.2 -c 5 && \
ping 10.10.10.2 -c 5 && \
ping 10.10.11.2 -c 5 && \ 
gnuradio-config-info -v && \
gnuradio-config-info --prefix && \
python --version && \
echo $PYTHONPATH



