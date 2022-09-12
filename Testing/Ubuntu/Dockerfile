FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c", "-x"]
WORKDIR /home/artifacts
WORKDIR /home/notroot/testing
WORKDIR /home/notroot
# installing basic essential packages to container to allow for rest of build to occur
RUN apt-get update && \ 
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
add-apt-repository ppa:ubuntu-toolchain-r/test && \
apt update && apt install -y gcc-11 g++-11
RUN update-alternatives --remove-all cpp && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9 --slave /usr/bin/gcov gcov /usr/bin/gcov-9 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-9 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-9  --slave /usr/bin/cpp cpp /usr/bin/cpp-9 && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110 --slave /usr/bin/g++ g++ /usr/bin/g++-11 --slave /usr/bin/gcov gcov /usr/bin/gcov-11 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-11 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-11  --slave /usr/bin/cpp cpp /usr/bin/cpp-11 && \
apt-get -y install python3-pip && \
#using pip to install recent versions of packages not yet in repos
pip3 install pygccxml && \
# clone pvpkg repo to get uhd and gnuradio Debian directories, as well as modified cmake and uhd_types files to patch
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Testing && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
mv test-only.sh /home/notroot/testing
RUN apt-get update
WORKDIR /home/notroot/uhd
# build latest UHD debian package from fileserver
RUN wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/ubuntu20.04/uhd/ && \
tar -xvzf uhd*.tar.gz && \
dpkg -i uhd*.deb || true && \
apt --fix-broken install
WORKDIR /home/notroot/volk
RUN git clone --branch v2.4.1 --recursive https://github.com/gnuradio/volk.git && \
cd volk && \
mkdir build && cd build && \
cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make && make install
WORKDIR /home/notroot/gnuradio
# build latest gnuradio debian package from fileserver
RUN wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/ubuntu20.04/gnuradio/ && \
tar -xvzf gnuradio*.tar.gz && \
dpkg -i libgnuradio*.deb || true && \
apt --fix-broken install && \
dpkg -i gnuradio*.deb || true && \
apt --fix-broken install
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
./test-only.sh





