FROM archlinux:base-devel-20210131.0.14634
# build from previous Arch image to avoid issues on newer versions
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot && \
# the Archlinux keyring, git, wget are installed for later use, as well as the base-devel package group
pacman -Sy --noconfirm archlinux-keyring&& \
    #pacman -Sy --noconfirm git && \
# install previous version of git from Arch archives, most recent versions require a newer glibc, which causes errors
pacman -U --noconfirm https://archive.archlinux.org/packages/g/git/git-2.30.0-1-x86_64.pkg.tar.zst && \
 pacman -Sy --noconfirm inetutils && \
 pacman -Sy --noconfirm wget && \
# Allow notroot to run stuff as root (to install dependencies):
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot 
# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
# install yay for later use in install
RUN ls && ls && git clone https://aur.archlinux.org/yay-bin.git && \
cd yay-bin && \
  makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
# clone pvtest repo to allow for installation of previuous versions of boost, boost-libs, and libx11; current versions of these resulted in build issues
ls && ls && pwd && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch  && \
sudo pacman -U --noconfirm boost-libs-1.69.0-1-x86_64.pkg.tar.xz && \ 
sudo pacman -U --noconfirm boost-1.69.0-1-x86_64.pkg.tar.xz && \
sudo pacman -U --noconfirm libx11-1.7.0-1-x86_64.pkg.tar.zst && \
# building icu63, which UHD will not build without
git clone https://aur.archlinux.org/icu63.git && \
cd icu63 && \
 makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/p/python/python-3.9.1-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/p/python-numpy/python-numpy-1.19.5-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/l/libuv/libuv-1.40.0-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/c/cmake/cmake-3.19.4-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/v/vulkan-icd-loader/vulkan-icd-loader-1.2.166-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/x/xkeyboard-config/xkeyboard-config-2.31-1-any.pkg.tar.zst&& \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/g/gtk3/gtk3-1:3.24.25-1-x86_64.pkg.tar.zst && \
sudo pacman -U --noconfirm https://archive.archlinux.org/packages/p/python-gobject/python-gobject-3.38.0-2-x86_64.pkg.tar.zst
WORKDIR libuhd
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies speified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo chown -R notroot /home/notroot/libuhd && \
sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/UHD/PKGBUILD && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed && pwd && ls && pwd
WORKDIR /home/notroot/yay-bin/pvpkg/Arch
RUN mv test-only.sh variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd
WORKDIR /home/notroot/gnuradio
# use wget to collect GnuRadio PKGBUILD from Github, and create the package with the dependencies speified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN ls && ls && pwd && sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/GnuRadio/PKGBUILD &&  \ 
sudo chown -R notroot /home/notroot/gnuradio && \
sleep 10000 && \
  makepkg --noconfirm --syncdeps --install && gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key CB9387521E1EE0127DA804843FDBB55084CC5D84 && \
 yay -Sy --noconfirm \
$(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \ 
makepkg --noconfirm --install --needed 
RUN sudo ping 192.168.10.2 -c 5 && \
sudo ping 10.10.10.2 -c 5 && \
sudo ping 10.10.11.2 -c 5 && \
sudo uhd_find_devices --args="addr=192.168.10.2" && \
sudo uhd_usrp_probe --args="addr=192.168.10.2" 
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 
RUN ls && \
sudo ./test-only.sh && \
sudo ./test-only.sh 


