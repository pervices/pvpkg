FROM archlinux

# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot && \

pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm && \
pacman -Syu --noconfirm wget && \
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
RUN wget https://raw.githubusercontent.com/than97/pvpkg/master/Arch/PKGBUILD &&\
ls && \
 git clone https://aur.archlinux.org/yay-bin.git && \
    cd yay-bin && \
    makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
 yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
makepkg --noconfirm --install
RUN yay -Sy --noconfirm libgmp-dev swig  \
 python-sphinx python-lxml libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python-pyqt5 \
liblog4cpp5-dev libzmq3-dev python-yaml python-click python-click-plugins \
python-zmq python-scipy python-gi python-gi-cairo gobject-introspection gir1.2-gtk-3.0  python-pybind11 && \
git clone --recursive https://github.com/gnuradio/volk.git
WORKDIR volk
RUN mkdir build
WORKDIR build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make && \
make install
WORKDIR /home
RUN git clone https://github.com/gnuradio/gnuradio.git
WORKDIR gnuradio
RUN mkdir build
WORKDIR build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ && \
make && \
make install

