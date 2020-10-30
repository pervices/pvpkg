FROM centos:7

RUN yum update && \
 yum -y install git  && \
 yum -y install cmake  && \
 yum -y install gcc gcc-c++ make glibc-devel  && \
 yum -y install epel-release && \
 yum -y install python3-devel.x86_64 &&\
 yum -y install http://repo.okay.com.mx/centos/7/x86_64/release/okay-release-1-1.noarch.rpm  && \
 yum -y install yum install boost166-devel  && \
 yum -y install libusb libusbx  && \
 yum -y install orc  && \
 python3 -m pip install Cheetah3  && \
 python3 -m pip install Mako && \
 python3 -m pip install pybind11 &&\
 yum -y install doxygen && \
 yum -y install boost-python && \
 python3 -m pip install numpy && \
python3 -m pip install requests 




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
        #-DPYTHON_EXECUTABLE=/usr/bin/python3 \
        #-DRUNTIME_PYTHON_EXECUTABLE=/usr/bin/python3 \
         /home/uhd/host && \
make -j4 && \
 make install
