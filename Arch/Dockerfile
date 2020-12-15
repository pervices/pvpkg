FROM archlinux


# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot && \
pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm && \
 pacman -Syu --noconfirm wget 
RUN gpg --verify "sha256":"c66e88d5786f2ca4dbebb14e06b566fb642a1a6947ad8cc9091f9f445134143f" && \
wget https://dl.bintray.com/boostorg/release/1.72.0/source/boost_1_72_0.tar.gz.asc && \
wget https://dl.bintray.com/boostorg/release/1.72.0/source/boost_1_72_0.tar.gz && \
pacman -Syu --noconfirm boost_1_72_0.tar.gz && \
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


