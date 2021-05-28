FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /home/notroot
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04Debian && \
mv gnuradio uhd /home/notroot
RUN apt-get update
WORKDIR /home/notroot/uhd
Run sleep 10000 && \
RUN git clone https://github.com/pervices/gnuradio/archive/refs/heads/maint-3.9.tar.gz && \
cp test.txt test_$(git rev-parse --short HEAD)_$(date +%d%b%Y).txt


