FROM centos:8
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
RUN dnf -y install gnuradio
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
./test-only.sh 
