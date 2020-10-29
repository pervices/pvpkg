FROM centos:8

RUN yum -y update && \
 yum -y install git && \
 yum -y install cmake && \
 yum -y install gcc gcc-c++ make glibc-devel && \
 yum -y install python2-pip && \
yum -y install boost-devel && \
 yum -y install libusb libusbx && \
 yum -y install orc && \
 pip2 install mako && \
 pip2 install cheetah && \
 pip2 install numpy && \
pip2 install requests && \
pip2 install gps

WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git && \
mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake \
-DPYTHON_INCLUDE_DIR=usr/bin/python2.7\
-DPYTHON_EXECUTABLE=usr/bin/python2.7 \
    -DCMAKE_INSTALL_PREFIX=/usr/ \
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
