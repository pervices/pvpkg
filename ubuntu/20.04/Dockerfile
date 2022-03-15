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
apt update && apt install -y gcc-10 g++-10
RUN update-alternatives --remove-all cpp && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9 --slave /usr/bin/gcov gcov /usr/bin/gcov-9 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-9 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-9  --slave /usr/bin/cpp cpp /usr/bin/cpp-9 && \
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 110 --slave /usr/bin/g++ g++ /usr/bin/g++-10 --slave /usr/bin/gcov gcov /usr/bin/gcov-10 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-10 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-10  --slave /usr/bin/cpp cpp /usr/bin/cpp-10 && \
gcc --version && \
apt-get -y install python3-pip && \
#using pip to install recent versions of packages not yet in repos
pip3 install Cheetah3 pygccxml && \
# clone pvpkg repo to get uhd and gnuradio Debian directories, as well as modified cmake and uhd_types files to patch
git clone https://github.com/pervices/pvpkg.git && \
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
#rm uhd/host/lib/rfnoc/radio_control_impl.cpp && \
#rm uhd/host/lib/include/uhdlib/rfnoc/radio_control_impl.hpp && \
#mv /home/notroot/pvpkg/ubuntu/20.04/modified/radio_control_impl.cpp uhd/host/lib/rfnoc && \
#mv /home/notroot/pvpkg/ubuntu/20.04/modified/radio_control_impl.hpp uhd/host/lib/include/uhdlib/rfnoc && \
cd debian && \
mk-build-deps -i --tool 'apt-get -f --yes' control
WORKDIR /home/notroot/uhd
RUN tar -czvf uhdpv_3.13.0.orig.tar.gz uhd && \
mv debian uhd && \
cd uhd && \
dpkg-buildpackage -us -uc -b && \
cd .. && \
dpkg -i uhd*.deb
WORKDIR /home/notroot/gnuradio
# clone gnuradio 3.9 from github, replace Cmake and uhd types files from Github with those from pvpkg to allow for successful build
RUN git clone -b maint-3.10 https://github.com/gnuradio/gnuradio.git && \
#rm /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
#rm /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
#mv /home/notroot/pvpkg/ubuntu/20.04/modified/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio && \
#mv /home/notroot/gnuradio/gnuradio/CMakeLists_mod.txt /home/notroot/gnuradio/gnuradio/CMakeLists.txt && \
#mv /home/notroot/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings && \
#mv /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python_mod.cc /home/notroot/gnuradio/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
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
mkdir gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv libgnuradio*.deb gnuradio*.deb gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf gnuradiopv_$(git describe --abbrev=8 --always --long)_$(date "+%F").tar.gz gnuradiopv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv gnuradio*.tar.gz /home/artifacts
WORKDIR /home/notroot/uhd
# move uhd deb file to artifact directory and tagging it for deployment
RUN mv uhd*.deb /home/notroot/uhd/uhd && \
cd uhd && \
mv uhd*.deb uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").deb && \
mv uhd*.deb /home/artifacts
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 





