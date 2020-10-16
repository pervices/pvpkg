FROM centos:7

RUN yum update
RUN yum -y install git 
RUN yum -y install cmake
RUN yum -y install gcc gcc-c++ make glibc-devel
RUN yum -y install python
RUN yum -y install http://repo.okay.com.mx/centos/7/x86_64/release/okay-release-1-1.noarch.rpm
RUN yum -y install yum install boost166-devel
RUN yum -y install libusb libusbx
RUN yum -y install orc
RUN yum -y install python-cheetah
RUN yum -y install python-mako


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
