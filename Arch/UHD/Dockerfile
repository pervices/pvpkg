FROM archlinux:base-devel
# build from most recent Archlinux base image
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot 
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot
# patched version of glibc 2.33 is installed as a workaround for Docker compatibility issue present after glibc was updated in early 2021
# the Archlinux keyring, git, wget are installed for later use, as well as the base-devel package group
#RUN patched_glibc=glibc-linux4-2.33-4-x86_64.pkg.tar.zst && \
 #   curl -LO "https://repo.archlinuxcn.org/x86_64/$patched_glibc" && \
 #  bsdtar -C / -xvf "$patched_glibc"
RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm git cmake clang icu && \
 pacman -Sy --noconfirm inetutils iproute2 && \
 pacman -Sy --noconfirm wget
# Allow notroot to run stuff as root (to install dependencies): 
# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR /home/notroot
# install yay for later use in install
RUN git clone https://aur.archlinux.org/yay-bin.git && \
cd yay-bin && \
makepkg --noconfirm --syncdeps --rmdeps --install --clean 
# clone pvtest repo to allow for installation of previous versions of boost and boost-libs; current versions of these resulted in build issues
WORKDIR /home/artifacts
WORKDIR /home/notroot
RUN git clone https://github.com/pervices/pvpkg.git 
#cd pvpkg/Arch  && \
# building icu63, boost, and boost-libs; which UHD will not build without
#yay -Sy --noconfirm icu63 
#sudo pacman -U --noconfirm boost-libs-1.69.0-1-x86_64.pkg.tar.xz && \ 
#sudo pacman -U --noconfirm boost-1.69.0-1-x86_64.pkg.tar.xz && \
#sudo pacman -U --noconfirm shared-mime-info-2.0+57+gc1d1c70-1-x86_64.pkg.tar.zst && \
#sudo pacman -U --noconfirm gtk3-1_3.24.30+62+g8d04980f38-2-x86_64.pkg.tar.zst
#sudo pacman -U --noconfirm qwt-6.1.6-1-x86_64.pkg.tar.zst
WORKDIR /home/notroot/testing
WORKDIR /home/notroot/libuhd
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo chown -R notroot /home/notroot/testing && \
sudo wget https://raw.githubusercontent.com/pervices/pvpkg/master/Arch/UHD/PKGBUILD && \
sudo chown -R notroot /home/notroot/libuhd && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed && \
sudo mv libuhdpv*.tar.zst /home/artifacts
#creating directory to move CI tests to in order to run tests on UHD install before deployment
WORKDIR /home/notroot/pvpkg/Testing
RUN mv test-only-Arch.sh variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing
# copying examples directory to libuhd folder to enable test to be found in same location as for other distributions to enable test_tx_trigger to be run
WORKDIR /home/notroot/libuhd/src/uhd/host
RUN sudo chown -R notroot /home/notroot/libuhd/src/uhd/host && \
cp -R examples /home/notroot/libuhd
#make tests executable to allow for CI testing before deployment of packages to fileserver
WORKDIR /home/notroot/testing
RUN chmod +x test-only-Arch.sh && \
chmod +x variables.sh && \
chmod +x tests



