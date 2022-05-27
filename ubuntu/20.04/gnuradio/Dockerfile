FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c", "-x"]
WORKDIR /home/artifacts
WORKDIR /home/notroot/testing
WORKDIR /home/notroot
# installing basic essential packages to container to allow for rest of build to occur
RUN apt-get update && \ 
apt-get -y install dpkg-dev sudo apt-utils dh-make bzr-builddeb equivs xz-utils iputils-ping net-tools software-properties-common cmake git coreutils build-essential && \
add-apt-repository ppa:ubuntu-toolchain-r/test && \
apt update && apt install -y gcc-11 g++-11
RUN update-alternatives --remove-all cpp && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9 --slave /usr/bin/gcov gcov /usr/bin/gcov-9 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-9 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-9  --slave /usr/bin/cpp cpp /usr/bin/cpp-9 && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110 --slave /usr/bin/g++ g++ /usr/bin/g++-11 --slave /usr/bin/gcov gcov /usr/bin/gcov-11 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-11 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-11  --slave /usr/bin/cpp cpp /usr/bin/cpp-11 && \
apt-get -y install python3-pip && \
#using pip to install recent versions of packages not yet in repos
pip3 install pygccxml && \
# clone pvpkg repo to get uhd and gnuradio Debian directories, as well as modified cmake and uhd_types files to patch
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/ubuntu/20.04 && \
mv gnuradio uhd volk InstallInstructionsUbuntu /home/notroot && \
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
WORKDIR /home/notroot/volk
RUN git clone --branch v2.4.1 --recursive https://github.com/gnuradio/volk.git && \
#cd debian && \
#mk-build-deps -i --tool 'apt-get -f --yes' control
#RUN ls && tar -czvf volkpv_2.4.1.orig.tar.gz volk && \
#mv debian volk && \
#cd volk && \
#dpkg-buildpackage -us -uc -b && \
#cd .. && \
#ls && dpkg -i volk*.deb
cd volk && \
mkdir build && cd build && \
cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make && make install
WORKDIR /home/notroot/gnuradio
# clone gnuradio 3.9 from github, replace Cmake and uhd types files from Github with those from pvpkg to allow for successful build
RUN git clone -b maint-3.10 https://github.com/gnuradio/gnuradio.git && \
# create orig.tar.gz of gnuradio repo nad build debian package
tar -czvf gnuradiopv_3.10.orig.tar.gz gnuradio && \
mv debian gnuradio && \
cd gnuradio/debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control && \
cd .. && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i libgnuradio*.deb && \
dpkg -i gnuradio*.deb 
# adding gnuradio.deb files to directory and tarring it for deployment; changing names of generated .debs to match relevant git tag and versioning info
RUN mv libgnuradio*.deb gnuradio*.deb gnuradio && \
cd gnuradio && \
mv gnuradiopv-dev*.deb gnuradiopv-dev-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv gnuradiopv-doc*.deb gnuradiopv-doc-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv gnuradio*amd64.deb gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-analog*.deb libgnuradiopv-analog-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-audio*.deb libgnuradiopv-audio-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-blocks*.deb libgnuradiopv-blocks-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-channels*.deb libgnuradiopv-channels-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-digital*.deb libgnuradiopv-digital-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-dtv*.deb libgnuradiopv-dtv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-fec*.deb libgnuradiopv-fec-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-fft*.deb libgnuradiopv-fft-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-filter*.deb libgnuradiopv-filter-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-network*.deb libgnuradiopv-network-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-pmt*.deb libgnuradiopv-pmt-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-qtgui*.deb libgnuradiopv-qtgui-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-runtime*.deb libgnuradiopv-runtime-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-trellis*.deb libgnuradiopv-trellis-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-uhd*.deb libgnuradiopv-uhd-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-video-sdl*.deb libgnuradiopv-video-sdl-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-vocoder*.deb libgnuradiopv-vocoder-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-wavelet*.deb libgnuradiopv-wavelet-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-zeromq*.deb libgnuradiopv-zeromq-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-soapy*.deb libgnuradiopv-soapy-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-pdu*.deb libgnuradiopv-pdu-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv libgnuradiopv-iio*.deb libgnuradiopv-iio-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mkdir gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv libgnuradio*.deb gnuradio*.deb gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf gnuradiopv_$(git describe --abbrev=8 --always --long)_$(date "+%F").tar.gz gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv gnuradio*.tar.gz /home/artifacts
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





