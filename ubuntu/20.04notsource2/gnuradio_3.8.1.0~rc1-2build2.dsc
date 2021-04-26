-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

Format: 3.0 (quilt)
Source: gnuradio
Binary: gnuradio, gnuradio-doc, gnuradio-dev, libgnuradio-analog3.8.1, libgnuradio-audio3.8.1, libgnuradio-blocks3.8.1, libgnuradio-channels3.8.1, libgnuradio-digital3.8.1, libgnuradio-dtv3.8.1, libgnuradio-fec3.8.1, libgnuradio-fft3.8.1, libgnuradio-filter3.8.1, libgnuradio-pmt3.8.1, libgnuradio-qtgui3.8.1, libgnuradio-runtime3.8.1, libgnuradio-trellis3.8.1, libgnuradio-uhd3.8.1, libgnuradio-video-sdl3.8.1, libgnuradio-vocoder3.8.1, libgnuradio-wavelet3.8.1, libgnuradio-zeromq3.8.1
Architecture: any all
Version: 3.8.1.0~rc1-2build2
Maintainer: A. Maitland Bottoms <bottoms@debian.org>
Homepage: http://gnuradio.org/
Standards-Version: 4.5.0
Vcs-Browser: https://salsa.debian.org/bottoms/pkg-gnuradio
Vcs-Git: https://salsa.debian.org/bottoms/pkg-gnuradio.git
Build-Depends: cmake, debhelper (>= 12~), dh-python, doxygen, gir1.2-gtk-3.0, gir1.2-pango-1.0, graphviz, libasound2-dev, libboost-date-time-dev, libboost-dev, libboost-filesystem-dev, libboost-program-options-dev, libboost-regex-dev, libboost-system-dev, libboost-test-dev, libboost-thread-dev, libcodec2-dev, libcomedi-dev [!hurd-i386], libcppunit-dev (>= 1.9.14), libfftw3-dev, libfontconfig1-dev, libgmp-dev, libgsl-dev (>= 2.0), libgsm1-dev, libjack-jackd2-dev, liblog4cpp5-dev, liborc-0.4-dev, libpulse-dev, libqwt-qt5-dev, libsdl1.2-dev, libsndfile1-dev, libthrift-dev [amd64 arm64 armel armhf i386], libuhd-dev, libusb-1.0-0-dev [!kfreebsd-any], libusb2-dev [kfreebsd-any], libvolk2-dev (>= 2.2.0), libxi-dev, libxrender-dev, libzmq3-dev [!hurd-i386] | libzmq-dev [!hurd-i386], ninja-build, pkg-config, portaudio19-dev, python3-click, python3-click-plugins, python3-dev, python3-gi, python3-gi-cairo, python3-lxml, python3-mako, python3-numpy, python3-opengl, python3-pyqt5 [!hurd-i386], python3-scipy, python3-sphinx, python3-yaml, python3-zmq [!hurd-i386], qt5-qmake, qtbase5-dev, qttools5-dev, swig (>= 3.0.8), thrift-compiler [amd64 arm64 armel armhf i386], xmlto
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
 a2f1a10b5c0419ad9519643b311d504f15e2f5e7 2344056 gnuradio_3.8.1.0~rc1.orig.tar.xz
 abf6a317007a9c9c86e550d06c6626931fb457da 1475772 gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz
Checksums-Sha256:
 8a67fd4ec8ce46f745f5e338aa5e138c11e1b22ef244e87269ff9d530e98e939 2344056 gnuradio_3.8.1.0~rc1.orig.tar.xz
 784d99101961698cb06b1da8373001f86dd34b1973cfe0eebdaf4c4a86537cb6 1475772 gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz
Files:
 d8b83b6a0ba2e3d8b243cbe889b5b60d 2344056 gnuradio_3.8.1.0~rc1.orig.tar.xz
 97add7403aa66efb99d994ddc85121b0 1475772 gnuradio_3.8.1.0~rc1-2build2.debian.tar.xz

-----BEGIN PGP SIGNATURE-----

iQJEBAEBCAAuFiEE1WVxuIqLuvFAv2PWvX6qYHePpvUFAl5gszMQHGRva29AdWJ1
bnR1LmNvbQAKCRC9fqpgd4+m9ewCD/0RbHLvgi/KsOxGG/X/mJ6qURuQLtSHEING
5nTi5/43z2Dt+a9KH0i2mxAhdl2ZHqdCb0YuMtGVQACWQkr9ovOcahdtUcsva10s
PGFTfPG4GQBvlEBnAOwYaVBz9LfBdlCfQENO47YxOs07FGnmXabx4zaggMiXqiBA
5G9B3bYS2Esiag+K+31pzgSOpoyuzmRWes9LfPBsQ5LIiLsXacEEOYnlF24EEacZ
zirYJsVkC3jv/lo4z7kN94ucXzgaQXhmSMgKzSBtKuEzsA3aIUNnHcmbEcu25CNR
xoIjOfPYHTcNOmZGNc8vwOeVsOGQWlLmlLX6Fw3uLHa1SqDy3T6MLTNdX+ATaP61
XqfoR5hrLpjVqAtiUarGG2FMCCQkGwWLlvJaNN+H8K/TIXMvz2A8P+6K/lLEPFoy
dYCr1qEMMQMNrHwxmNS45BBn3yqdmljRFV/Ltg/oEfuIipRd6TREPZPdE81bXpaP
XuY6j443hN8gpB3jAlXX7sI5oA/g6XDLBClYvX7gdsI9MeT8S+58glP2kLhJvhma
2jHr8AEt9z6k+5Hz4EucOuC1WYDYA1faSec5uABLFPOvReimZY+oEi5j0yapTxh8
f9Dbw9OLDNq1PkVfDfYwMJy13ibJXypvoWfltczMgB2BvmLLN0NFnACHKIE9YtJm
9+rAtq9uzw==
=MYar
-----END PGP SIGNATURE-----
