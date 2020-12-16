FROM archlinux


# makepkg cannot (and should not) be run as root:
RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm && \
 pacman -Syu --noconfirm wget
RUN git clone https://github.com/pervices/pvpkg.git && \
ls 
WORKDIR pvpkg/Arch && \
pacman -U --verbose boost-1.72.0-2-x86_64.pkg.tar.zst && \
pacman -U boost-libs-1.72.0-2-x86_64.pkg.tar.zst && \
# Allow notroot to run stuff as root (to install dependencies):
WORKDIR ../..
RUN useradd -m notroot && \
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot && \
ls
# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
RUN git clone https://aur.archlinux.org/yay-bin.git 
WORKDIR yay-bin && \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
yay -Syyu --noconfirm
WORKDIR ../libuhd
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


