FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 && \
sleep 10000
