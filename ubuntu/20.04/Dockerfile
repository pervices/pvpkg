FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c", "-x"]
WORKDIR /home/artifacts
WORKDIR /home/notroot
WORKDIR /home/notroot/testing
WORKDIR /home/notroot
# installing basic essential packages to container to allow for rest of build to occur
RUN apt-get update && \
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
apt-get -y install python3-pip && \
pip3 install Cheetah3 && \
# clone pvpkg repo to get uhd and gnuradio Debian directories, as well as modified cmake and uhd_types files to patch
ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04 && \
mv gnuradio uhd /home/notroot && \
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
RUN tar -czvf uhdpv_3.13.0.orig.tar.gz /home/notroot/uhd/uhd && \
mv debian /home/notroot/uhd/uhd && \
cd uhd && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i uhd*.deb
WORKDIR /home/notroot/gnuradio
# clone gnuradio 3.9 from github, replace Cmake and uhd types files from Github with those from pvpkg to allow for successful build
RUN git clone -b maint-3.9 https://github.com/pervices/gnuradio.git && \
rm /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
rm /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
mv /home/notroot/pvpkg/ubuntu/20.04/modified/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio && \
mv /home/notroot/gnuradio/gnuradio/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
mv /home/notroot/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings && \
mv /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
# create orig.tar.gz of gnuradio repo nad build debian package
tar -czvf gnuradio_3.9.orig.tar.gz /home/notroot/gnuradio/gnuradio && \
mv debian /home/notroot/gnuradio/gnuradio && \
cd gnuradio/debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control && \
cd .. && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i libgnuradio*.deb && \
dpkg -i gnuradio*.deb 
# adding gnuradio.deb files to directory and tarring it for deployment; changing names of generated .debs to match relevant git tag and versioning info
RUN mv libgnuradio*.deb gnuradio*.deb /home/notroot/gnuradio/gnuradio && \
cd gnuradio && \
mv gnuradio-dev*.deb gnuradio-dev-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv gnuradio-doc*.deb "gnuradio-doc-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb" && \
mv gnuradio*amd64.deb gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-analog*.deb libgnuradio-analog-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-audio*.deb libgnuradio-audio-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-blocks*.deb libgnuradio-blocks-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-channels*.deb libgnuradio-channels-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-digital*.deb libgnuradio-digital-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-dtv*.deb libgnuradio-dtv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-fec*.deb libgnuradio-fec-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-fft*.deb libgnuradio-fft-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-filter*.deb libgnuradio-filter-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-network*.deb libgnuradio-network-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-pmt*.deb libgnuradio-pmt-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-qtgui*.deb libgnuradio-qtgui-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-runtime*.deb libgnuradio-runtime-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-trellis*.deb libgnuradio-trellis-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-uhd*.deb libgnuradio-uhd-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-video-sdl*.deb libgnuradio-video-sdl-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-vocoder*.deb libgnuradio-vocoder-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-wavelet*.deb libgnuradio-wavelet-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradio-zeromq*.deb libgnuradio-zeromq-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mkdir gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv libgnuradio*.deb gnuradio*.deb gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf gnuradio_$(git describe --abbrev=8 --always --long)_$(date "+%F").tar.gz /home/notroot/gnuradio/gnuradio/gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv gnuradio*.tar.gz /home/artifacts
WORKDIR /home/notroot/uhd
# move uhd deb file to artifact directory and tagging it for deployment
RUN mv uhd*.deb /home/notroot/uhd/uhd && \
cd uhd && \
mv uhd*.deb uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv uhd*.deb /home/artiacts
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
./test-only.sh





