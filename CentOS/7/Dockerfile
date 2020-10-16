FROM centos:7

RUN yum update
RUN yum -y install git 
RUN yum -y install cmake
RUN yum -y install gcc gcc-c++ make glibc-devel
RUN yum -y install python
RUN rpm -iUvh http://springdale.princeton.edu/data/springdale/7/x86_64/os/Computational/boost160-1.60.0-7.sdl7.3.x86_64.rpm
RUN yum -y install python-mako
RUN yum -y install libusb libusbx
RUN yum -y install orc
RUN yum -y install python-cheetah


WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
RUN mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake \
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
