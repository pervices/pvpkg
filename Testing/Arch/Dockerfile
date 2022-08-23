FROM archlinux:base-devel
# build from most recent Archlinux base image
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot 
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot
RUN pacman -Sy --noconfirm archlinux-keyring&& \
    pacman -Sy --noconfirm git cmake clang && \
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
RUN git clone https://github.com/pervices/pvpkg.git
WORKDIR /home/notroot/testing
WORKDIR /home/notroot/libuhd
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo chown -R notroot /home/notroot/testing && \
sudo   wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/archlinux/uhd/ && \
sudo chown -R notroot /home/notroot/libuhd && \
mv libuhd*.tar.zst libuhd.pkg.tar.zst && \
sudo pacman -U --noconfirm libuhd.pkg.tar.zst
#creating directory to move CI tests to in order to run tests on UHD and Gnuradio installs before deployment
WORKDIR /home/notroot/pvpkg/Testing
RUN mv test-only-Arch.sh variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing
# copying examples directory to libuhd folder to enable test to be found in same location as for other distributions to enable test_tx_trigger to be run
WORKDIR /home/notroot/libuhd/src/uhd/host
RUN sudo chown -R notroot /home/notroot/libuhd/src/uhd/host && \
sudo find / -name "examples" && \
cp -R examples /home/notroot/libuhd
WORKDIR /home/notroot/gnuradio
# use wget to collect GnuRadio PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/archlinux/gnuradio/ &&  \ 
sudo chown -R notroot /home/notroot/gnuradio && \
mv gnuradio*.tar.zst gnuradio.pkg.tar.zst && \
sudo pacman -U --noconfirm gnuradio.pkg.tar.zst  
#make tests executable to allow for CI testing before deployment of packages to fileserver
WORKDIR /home/notroot/testing
RUN chmod +x test-only-Arch.sh && \
chmod +x variables.sh && \
chmod +x tests && \
./test-only-Arch.sh
