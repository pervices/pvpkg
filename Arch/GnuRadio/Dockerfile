FROM archlinux:base-devel
# build from most recent Archlinux base image
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot
RUN pacman-key --init
RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm git cmake clang icu && \
 pacman -Sy --noconfirm inetutils iproute2 && \
 pacman -Sy --noconfirm wget net-tools ccache distcc
# Allow notroot to run stuff as root (to install dependencies):
# Continue execution (and CMD) as notroot:
USER notroot

###
# Prep
###
# DIRECTORY CREATION / PERMISSIONS: If not already created, WORKDIR also
# creates the directory. To avoid permission issues and ugly code, we initially
# create all the directories here, and also ensure correct permissions.
WORKDIR /home/notroot
WORKDIR /home/notroot
WORKDIR /home/artifacts
WORKDIR /home/notroot/testing
WORKDIR /home/notroot/libuhd
WORKDIR /home/notroot/gnuradio
RUN sudo chown -R notroot /home/{notroot,artifacts}/

### Install other dependencies
WORKDIR /home/notroot

# Yay:
RUN git clone https://aur.archlinux.org/yay-bin.git && \
cd yay-bin && \
makepkg --noconfirm --syncdeps --rmdeps --install --clean

# Configure makepkg to use ccache:
RUN sudo sed -i 's/\!ccache/ccache/g' /etc/makepkg.conf

# Configure makepkg to use distcc:
## TODO: Needs to be tested
#RUN sudo sed -i 's/\!distcc/distcc/g' /etc/makepkg.conf

###
# PVPKG: Clone PVPKG
###
# clone pvtest repo to allow for installation of previous versions of boost and boost-libs; current versions of these resulted in build issues
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

###
# UHD: Build and Install UHD from PKGBUILD
###
WORKDIR /home/notroot/libuhd
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN cp /home/notroot/pvpkg/Arch/UHD/PKGBUILD . && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && \
 makepkg --noconfirm --syncdeps --needed --install && \
sudo mv libuhdpv*.tar.zst /home/artifacts

###
# CI: Structure CI Test Scripts
###
WORKDIR /home/notroot/pvpkg/Testing
RUN mv test-only-Arch.sh variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing
# copy example sources and executables to libuhd folder to enable test to be found in same location as for other distributions to enable test_tx_trigger to be run
WORKDIR /home/notroot/libuhd/src/uhd/host
RUN sudo chown -R notroot /home/notroot/libuhd/src/uhd/host && \
cp -R examples /home/notroot/libuhd && \
cp -R build/examples/* /home/notroot/libuhd/examples
#make tests executable to allow for CI testing before deployment of packages to fileserver
WORKDIR /home/notroot/testing
RUN chmod +x test-only-Arch.sh && \
chmod +x variables.sh && \
chmod +x tests

###
# GNURADIO: Build Gnuradio and Gnuradio Companion
###
# use wget to collect GnuRadio PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
WORKDIR /home/notroot/gnuradio
RUN cp /home/notroot/pvpkg/Arch/GnuRadio/PKGBUILD . && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && \
 makepkg --noconfirm --syncdeps --needed --install && \
sudo mv gnuradio*.tar.zst /home/artifacts
