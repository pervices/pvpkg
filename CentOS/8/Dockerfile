FROM centos:8

#RUN yum -y update && \
 #dnf -y --enablerepo=PowerTools install boost-python3-devel && \
#dnf -y --enablerepo=PowerTools install doxygen && \
 #yum -y install git && \
 #yum -y install cmake && \
 RUN yum -y install epel-release && \
 #yum -y install gcc-c++ make && \
 #yum -y install python3-pip  python36-devel && \
 #yum -y install libusb libusbx && \
 #yum -y install orc && \
 #pip3 install mako && \
 #pip3 install Cheetah3 && \
 #pip3 install numpy && \
#pip3 install requests 


WORKDIR /home
#RUN git clone https://github.com/pervices/uhd.git && \
#mkdir uhdlib
#WORKDIR /home/uhdlib
#RUN cmake \
   # -DCMAKE_INSTALL_PREFIX=/usr/ \
 #          -DENABLE_PYTHON3=ON \
  #         -DENABLE_EXAMPLES=ON \
 #          -DENABLE_UTILS=ON \
 #          -DENABLE_TESTS=OFF \
  #         -DENABLE_E100=OFF \
#	   -DENABLE_N230=OFF \
#	   -DENABLE_N300=OFF \
#	   -DENABLE_E320=OFF \
#	   -DENABLE_USRP1=OFF \
#	   -DENABLE_USER2=OFF \
#	   -DENABLE_B200=OFF \
#	   -DENABLE_X300=OFF \
#       -DENABLE_CRIMSON_TNG=ON \
#       -DENABLE_CYAN_16T=OFF \
#       -DENABLE_CYAN_64T=OFF \
#	   -DENABLE_OCTOCLOCK=OFF \
#	   -DENABLE_DOXYGEN=OFF \
#	   -DENABLE_USB=OFF \
 #        /home/uhd/host && \
 #make -j4 && \
 #make install

RUN yum -y install git cmake g++ libboost-all-dev libgmp-dev swig python3-numpy \
python3-mako python3-sphinx python3-lxml doxygen libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 \
liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0
