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
# clone pvpkg repo to get uhd  Debian directory.
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04 && \
mv InstallInstructionsUbuntu /home/notroot && \
cd testing && \
mv uhd /home/notroot
RUN apt-get update
WORKDIR /home/notroot/uhd
# clone latest pervices uhd version, tar repo as orig.tar.gz, and build debian package
RUN git clone -b  ops/dwil/serial_get_buffer_level https://github.com/pervices/uhd.git && \
cd debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control
WORKDIR /home/notroot/uhd
RUN tar -czvf uhdpv_3.13.0.orig.tar.gz uhd && \
mv debian uhd && \
cd uhd && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i uhd*.deb
WORKDIR /home/notroot
RUN mv InstallInstructionsUbuntu /home/notroot/uhd/uhd
WORKDIR /home/notroot/uhd
# move uhd deb file to artifact directory and tagging it for deployment
RUN mv uhd*.deb /home/notroot/uhd/uhd && \
cd uhd && \
mv uhd*.deb uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mkdir uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv uhd*.deb InstallInstructionsUbuntu uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").tar.gz uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv uhd*.tar.gz /home/artifacts






