FROM archlinux
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot && \
# the Archlinux keyring, git, wget are installed for later use, as well as the base-devel package group
pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm && \
 pacman -Syu --noconfirm wget && \
# Allow notroot to run stuff as root (to install dependencies):
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot 
# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
# install yay for later use in install
RUN git clone https://aur.archlinux.org/yay-bin.git && \
cd yay-bin && \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
yay -Syyu --noconfirm && \
# clone pvtest repo to allow for installation of previuous versions of boost, boost-libs, and libx11; current versions of these resulted in build issues
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch 
#sudo pacman -U --noconfirm boost-libs-1.72.0-2-x86_64.pkg.tar.zst && \ 
#sudo pacman -U --noconfirm boost-1.72.0-2-x86_64.pkg.tar.zst && \
#sudo pacman -U --noconfirm libx11-1.7.0-1-x86_64.pkg.tar.zst

WORKDIR libuhd
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies speified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/UHD/PKGBUILD && \
sudo chown -R notroot /home/notroot/libuhd && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed
WORKDIR ../gnuradio
# use wget to collect GnuRadio PKGBUILD from Github, and create the package with the dependencies speified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/GnuRadio/PKGBUILD &&  \
sudo chown -R notroot /home/notroot/gnuradio && \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key CB9387521E1EE0127DA804843FDBB55084CC5D84 && \
yay -Syyu --noconfirm && \
 yay -Sy --noconfirm\
$(pacman --verbose --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
makepkg --noconfirm --install --needed --syncdeps


