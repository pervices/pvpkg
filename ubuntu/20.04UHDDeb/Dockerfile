FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 
WORKDIR /home
RUN pwd && ls && pwd && ls && apt-get update && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04UHDDeb && \ 
mv uhdpv_3.13.0.orig.tar.gz uhdpv_3.13.0-1.debian.tar.xz uhdpv_3.13.0-1.dsc /home
WORKDIR /home
RUN dpkg-source -x --no-check uhdpv_3.13.0-1.dsc && \
cd uhdpv-3.13.0/debian && \
mk-build-deps -i -r --tool 'apt-get -f --yes' control
RUN cd uhdpv-3.13.0 && dpkg-buildpackage --pre-clean --post-clean -i -us -uc


