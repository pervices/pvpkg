FROM archlinux

# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot && \

pacman -Sy --noconfirm archlinux-keyring boost-libs orc python2 && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Sy --noconfirm cmake make boost boost-libs doxygen gcc glibc python2-setuptools python2-numpy python2-requests python2-docutils python-mako python-cheetah && \
pacman -Sy --noconfirm wget
 #echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git && \
mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/ \
           -DENABLE_EXAMPLES=ON \
          -DENABLE_UTILS=ON \
          -DENABLE_TESTS=OFF \
           -DENABLE_E100=OFF \
	   -DENABLE_N230=OFF \
	   -DENABLE_N300=OFF \
	   -DENABLE_E320=OFF \
	   -DENABLE_USRP1=OFF \
	   -DENABLE_USER2=OFF \
	   -DENABLE_B200=OFF \
	   -DENABLE_X300=OFF \
       -DENABLE_CRIMSON_TNG=ON \
       -DENABLE_CYAN_16T=OFF \
      -DENABLE_CYAN_64T=OFF \
	   -DENABLE_OCTOCLOCK=OFF \
	   -DENABLE_DOXYGEN=OFF \
	   -DENABLE_USB=OFF \
        /home/uhd/host && \
make -j4 && \
 make install


