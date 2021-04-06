FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install dpkg-dev sudo dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-dev python3-pip libboost1.67-all-dev doxygen libusb-1.0-0-dev liborc-0.4-dev && \
pip3 install mako Cheetah3 requests numpy pybind11 docutils ruamel.yaml setuptools
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
RUN  ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd && \
cd 20.04notsource && \
mv gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz gnuradio_3.8.1.0~rc1-2build2.dsc gnuradio_3.8.1.0~rc1.orig.tar.xz /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN dpkg-source -x --no-check gnuradio_3.8.1.0~rc1-2build2.dsc && \
#tar -xf gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz && \ 
#xz -d -v gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz && \ 
cd gnuradio-3.8.1.0~rc1/debian && \
mk-build-deps -i -r --tool 'apt-get --yes' control 
RUN cd gnuradio-3.8.1.0~rc1 && dpkg-buildpackage --pre-clean --post-clean -i -us -uc
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
ldconfig && \
./test-only.sh
