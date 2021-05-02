FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 
WORKDIR /home/notroot/gnuradio
WORKDIR /home/notroot/testing
WORKDIR /home/notroot/libuhd
WORKDIR /home/notroot
RUN ls && ls && pwd && apt-get update && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/testing && \
cd 20.04UHDDeb && \ 
mv uhdpv_3.13.0.orig.tar.gz uhdpv_3.13.0-1.debian.tar.xz uhdpv_3.13.0-1.dsc /home/notroot/libuhd && \
cd ../20.04notsource2 && \
mv gnuradio_3.8.1.0~rc1.orig.tar.xz gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz gnuradio_3.8.1.0~rc1-2build2.dsc /home/notroot/gnuradio
#cd ../20.04notsource && \
#mv gnuradio_3.10.0.orig.tar.gz gnuradio_3.10.0-1.debian.tar.xz gnuradio_3.10.0-1.dsc /home/notroot/gnuradio
WORKDIR /home/notroot/libuhd
RUN dpkg-source -x --no-check uhdpv_3.13.0-1.dsc && \
cd uhdpv-3.13.0/debian && \
mk-build-deps -i -r --tool 'apt-get -f --yes' control
RUN cd uhdpv-3.13.0 && dpkg-buildpackage --pre-clean --post-clean -us -uc && \
cd .. && \
dpkg -i uhdpv_3.13.0-1_amd64.deb
WORKDIR /home/notroot/gnuradio
RUN dpkg-source -x --no-check gnuradio_3.8.1.0~rc1-2build2.dsc && \
#RUN dpkg-source -x --no-check gnuradio_3.10.0-1.dsc && \
cd gnuradio-3.8.1.0~rc1/debian && \
#cd gnuradio-3.10.0/debian && \
mk-build-deps -i -r --tool 'apt-get -f --yes' control
RUN cd gnuradio-3.8.1.0~rc1 && dpkg-buildpackage --pre-clean --post-clean -i -us -uc && \ 
#RUN rm -rf home/notroot/pvpkg
#RUN cd gnuradio-3.10.0 && dpkg-buildpackage --pre-clean --post-clean -us -uc && \ 
cd .. && \
sleep 10000 && \
dpkg -i libgnuradio*.deb && \  
#apt -y --fix-broken install && \
dpkg -i gnuradio_3.8.1.0~rc1-2build2_amd64.deb
#dpkg -i gnuradio_3.10.0-1_amd64.deb
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
ldconfig && \
./test-only.sh
