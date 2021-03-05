FROM archlinux:base-devel
# build from previous Arch image to avoid issues on newer versions
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot && \
echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot && \
pacman-db-upgrade
# the Archlinux keyring, git, wget are installed for later use, as well as the base-devel package group
RUN pacman -Sy --noconfirm archlinux-keyring&& \
    #pacman -Sy --noconfirm git && \
# install previous version of git from Arch archives, most recent versions require a newer glibc, which causes errors
 pacman -Sy --noconfirm inetutils && \
 pacman -Sy --noconfirm wget && \
# Allow notroot to run stuff as root (to install dependencies): 
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
# building icu63, which UHD will not build without
yay -Sy --noconfirm icu63 && \
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
RUN ls && pwd && pwd && ls && ls && ls && sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/GnuRadio/PKGBUILD &&  \ 
sudo chown -R notroot /home/notroot/gnuradio && \
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


