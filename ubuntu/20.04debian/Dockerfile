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
cd .. && \
dpkg -i uhd*.deb
WORKDIR /home/notroot/gnuradio
RUN git clone -b maint-3.9 https://github.com/pervices/gnuradio.git && \
diff -u /home/notroot/pvpkg/ubuntu/20.04/modified/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio/CMakeLists.txt > CMakeLists.patch && \
diff -u /home/notroot/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc > uhd_types_python.patch && \
patch -R  /home/notroot/gnuradio/gnuradio/CMakeLists.txt CMakeLists.patch && \
patch -R /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc uhd_types_python.patch && \
tar -czvf gnuradio_3.9.orig.tar.gz /home/notroot/gnuradio/gnuradio && \
mv debian /home/notroot/gnuradio/gnuradio && \
cd gnuradio/debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control && \
cd .. && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i libgnuradio*.deb && \
dpkg -i gnuradio*.deb





#cp test.txt test_$(git rev-parse --short HEAD)_$(date +%d%b%Y).txt



