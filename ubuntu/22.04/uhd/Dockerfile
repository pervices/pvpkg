FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c", "-x"]
WORKDIR /home/artifacts
WORKDIR /home/notroot/testing
WORKDIR /home/notroot
# installing basic essential packages to container to allow for rest of build to occur
RUN apt-get update && \ 
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
add-apt-repository ppa:ubuntu-toolchain-r/test && \
apt update && apt-get -y install python3-pip && \
#using pip to install recent versions of packages not yet in repos
pip3 install pygccxml && \
# clone pvpkg repo to get uhd and gnuradio Debian directories, as well as modified cmake and uhd_types files to patch
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/22.04 && \
mv gnuradio uhd InstallInstructionsUbuntu /home/notroot && \
cd ../../Testing && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
mv test-only.sh /home/notroot/testing
RUN apt-get update
WORKDIR /home/notroot/uhd
# clone latest pervices uhd version, tar repo as orig.tar.gz, and build debian package
RUN git clone -b master https://github.com/pervices/uhd.git && \
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
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 





