FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
apt-get -y install sudo dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential
WORKDIR /home/notroot/libuhd
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd && \
cd 20.04notsource && \
mv gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz gnuradio_3.8.1.0~rc1-2build2.dsc gnuradio_3.8.1.0~rc1.orig.tar.xz /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN tar -xf gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz && \ 
xz -d -v gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz && \ 
cd debian && \
mk-build-deps -i --tool 'apt-get --yes' control 
RUN cd .. && dpkg-source -b /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
ldconfig && \
./test-only.sh
