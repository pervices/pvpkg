FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c", "-x"]
WORKDIR /home/notroot
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 && \
ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04/20.04testing && \
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
rm /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
rm /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
mv /home/notroot/pvpkg/ubuntu/20.04/modified/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio && \
mv /home/notroot/gnuradio/gnuradio/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
mv /home/notroot/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings && \
mv /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
#RUN diff -u /home/notroot/pvpkg/ubuntu/20.04/modified/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio/CMakeLists.txt > CMakeLists.patch
#RUN diff -u /home/notroot/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc > uhd_types_python.patch
#RUN patch -R  /home/notroot/gnuradio/gnuradio/CMakeLists.txt CMakeLists.patch && \
#RUN patch -R /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc uhd_types_python.patch && \
tar -czvf gnuradio_3.9.orig.tar.gz /home/notroot/gnuradio/gnuradio && \
mv debian /home/notroot/gnuradio/gnuradio && \
cd gnuradio/debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control && \
cd .. && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i libgnuradio*.deb && \
dpkg -i gnuradio*.deb 
# adding gnuradio.deb files to directory and tarring it for deployment
RUN mv libgnuradio*.deb gnuradio*.deb /home/notroot/gnuradio/gnuradio && \
cd gnuradio && \
mkdir gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv libgnuradio*.deb gnuradio*.deb gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf gnuradio_$(git describe --abbrev=8 --always --long)_$(date "+%F").tar.gz /home/notroot/gnuradio/gnuradio/gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv gnuradio*.tar.gz /home
# adding uhd.deb files to directory and tarring it for deployment
WORKDIR /home/notroot/uhd
RUN mv uhd*.deb /home/notroot/uhd/uhd && \
cd uhd && \
mv uhd*.deb uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
tar -czvf uhdpv_$(git describe --abbrev=8 --always --long)_$(date "+%F").tar.gz uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv uhd*.tar.gz /home







#cp test.txt test_$(git rev-parse --short HEAD)_$(date +%d%b%Y).txt
#cp test.txt test_$(git describe --abbrev=8 --always --long)_$(date "+%F").txt


