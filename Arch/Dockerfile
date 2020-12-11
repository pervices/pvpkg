FROM archlinux


# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot && \
pacman-key --recv-keys APKAIFKFWOMXM2UMTSFA
 pacman -U https://dl.bintray.com/boostorg/release/1.71.0/source/boost_1_71_0.tar.gz && \
pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm && \
 pacman -Syu --noconfirm wget && \

# Allow notroot to run stuff as root (to install dependencies):
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
RUN mkdir libuhd
RUN mkdir gnuradio
RUN git clone https://aur.archlinux.org/yay-bin.git && \
  cd yay-bin && \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
yay -Syyu --noconfirm
WORKDIR libuhd
RUN wget -v -d -nv https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/UHD/PKGBUILD && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed

WORKDIR ../gnuradio
RUN wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/GnuRadio/PKGBUILD &&  \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key CB9387521E1EE0127DA804843FDBB55084CC5D84 && \
yay -Syyu --noconfirm && \
 yay -Sy --noconfirm   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
makepkg --noconfirm --install


