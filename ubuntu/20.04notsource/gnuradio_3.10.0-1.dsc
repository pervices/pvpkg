Format: 3.0 (quilt)
Source: gnuradio
Binary: gnuradio, gnuradio-doc, gnuradio-dev, libgnuradio-analog3.8.1, libgnuradio-audio3.8.1, libgnuradio-blocks3.8.1, libgnuradio-channels3.8.1, libgnuradio-digital3.8.1, libgnuradio-dtv3.8.1, libgnuradio-fec3.8.1, libgnuradio-fft3.8.1, libgnuradio-filter3.8.1, libgnuradio-pmt3.8.1, libgnuradio-qtgui3.8.1, libgnuradio-runtime3.8.1, libgnuradio-trellis3.8.1, libgnuradio-uhd3.8.1, libgnuradio-video-sdl3.8.1, libgnuradio-vocoder3.8.1, libgnuradio-wavelet3.8.1, libgnuradio-zeromq3.8.1
Architecture: any all
Version: 3.10.0-1
Maintainer: A. Maitland Bottoms <bottoms@debian.org>
Homepage: http://gnuradio.org/
Standards-Version: 4.5.0
Vcs-Browser: https://salsa.debian.org/bottoms/pkg-gnuradio
Vcs-Git: https://salsa.debian.org/bottoms/pkg-gnuradio.git
Build-Depends: cmake, debhelper (>= 12~), dh-python, doxygen, gir1.2-gtk-3.0, gir1.2-pango-1.0, graphviz, libasound2-dev, libboost1.67-all-dev, libcanberra-gtk-module, libcodec2-dev, libcomedi-dev [!hurd-i386], libcppunit-dev (>= 1.9.14), libfftw3-dev, libfontconfig1-dev, libgmp-dev, libgsl-dev (>= 2.0), libgsm1-dev, libjack-jackd2-dev, liblog4cpp5-dev, liborc-0.4-dev, libpulse-dev, libqwt-qt5-dev, libsdl1.2-dev, libsndfile1-dev, libthrift-dev [amd64 arm64 armel armhf i386], libuhd-dev, libusb-1.0-0-dev [!kfreebsd-any], libusb2-dev [kfreebsd-any], libvolk2-dev (>= 2.2.0), libxi-dev, libxrender-dev, libzmq3-dev [!hurd-i386] | libzmq-dev [!hurd-i386], ninja-build, pkg-config, portaudio19-dev, pybind11, python3-click, python3-click-plugins, python3-dev, python3-gi, python3-gi-cairo, python3-lxml, python3-mako, python3-numpy, python3-opengl, python3-pyqt5 [!hurd-i386], python3-pyqtgraph, python3-scipy, python3-sphinx, python3-yaml, python3-zmq [!hurd-i386], qt5-qmake, qtbase5-dev, qttools5-dev, thrift-compiler [amd64 arm64 armel armhf i386], xmlto
Package-List:
 gnuradio deb comm optional arch=any
 gnuradio-dev deb libdevel optional arch=any
 gnuradio-doc deb doc optional arch=all
 libgnuradio-analog3.8.1 deb libs optional arch=any
 libgnuradio-audio3.8.1 deb libs optional arch=any
 libgnuradio-blocks3.8.1 deb libs optional arch=any
 libgnuradio-channels3.8.1 deb libs optional arch=any
 libgnuradio-digital3.8.1 deb libs optional arch=any
 libgnuradio-dtv3.8.1 deb libs optional arch=any
 libgnuradio-fec3.8.1 deb libs optional arch=any
 libgnuradio-fft3.8.1 deb libs optional arch=any
 libgnuradio-filter3.8.1 deb libs optional arch=any
 libgnuradio-pmt3.8.1 deb libs optional arch=any
 libgnuradio-qtgui3.8.1 deb libs optional arch=kfreebsd-any,linux-any
 libgnuradio-runtime3.8.1 deb libs optional arch=any
 libgnuradio-trellis3.8.1 deb libs optional arch=any
 libgnuradio-uhd3.8.1 deb libs optional arch=any
 libgnuradio-video-sdl3.8.1 deb libs optional arch=any
 libgnuradio-vocoder3.8.1 deb libs optional arch=any
 libgnuradio-wavelet3.8.1 deb libs optional arch=any
 libgnuradio-zeromq3.8.1 deb libs optional arch=kfreebsd-any,linux-any
Checksums-Sha1:
 915944bc889027eda38e14347527f017f85e28a9 4359164 gnuradio_3.10.0.orig.tar.gz
 f223d1b1c87e4d469b6c835d61e25869ec4470c2 4796 gnuradio_3.10.0-1.debian.tar.xz
Checksums-Sha256:
 3f3db79c7002c64708b177841794dc1e4c04af7f73ea46cf1614087c84a25e12 4359164 gnuradio_3.10.0.orig.tar.gz
 bbfdcfe7eaabe160afd5c06ac52449f16e84c37fd48517f38a3fb1148b54d951 4796 gnuradio_3.10.0-1.debian.tar.xz
Files:
 8fea5e88cd9088e0296969fe1f6e686a 4359164 gnuradio_3.10.0.orig.tar.gz
 806e9c0650a43c8be104062d26c0dfe8 4796 gnuradio_3.10.0-1.debian.tar.xz
