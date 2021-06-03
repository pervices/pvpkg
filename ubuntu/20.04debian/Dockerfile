FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /home/notroot
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 && \
ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04Debian && \
mv gnuradio uhd /home/notroot
RUN apt-get update
WORKDIR /home/notroot/uhd
RUN git clone -b master https://github.com/pervices/uhd.git && \
cd debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control
RUN tar -czvf uhdpv_3.13.0.orig.tar.gz /home/notroot/uhd/uhd && \
mv debian /home/notroot/uhd/uhd && \
cd uhd && \
dpkg-buildpackage -us -uc -b && \
sleep 10000 
# tar uhd source
# run dpkg-buildpackage
# dpkg-i uhd





#dh_auto_clean: error: invalid or non-existing path to the source directory: host




#cp test.txt test_$(git rev-parse --short HEAD)_$(date +%d%b%Y).txt



