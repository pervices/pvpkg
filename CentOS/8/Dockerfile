FROM centos:8

RUN yum -y update
RUN yum -y install git 
RUN yum -y install cmake
RUN yum -y install gcc gcc-c++ make glibc-devel
RUN yum -y install python2-pip
RUN yum -y install boost-devel
RUN yum -y install libusb libusbx
RUN yum -y install orc
# RUN yum -y install python3-cheetah
RUN pip2 install mako
RUN pip2 install cheetah
RUN pip2 install numpy
RUN pip2 install requests
RUN pip2 install gps

WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
RUN mkdir uhdlib
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
         /home/uhd/host
RUN make -j4
RUN make install
