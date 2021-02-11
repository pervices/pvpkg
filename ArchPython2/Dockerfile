FROM archlinux:base-devel-20210131.0.14634
# using old Archlinux docker image for build to work around /etc/makepkg.conf issue that results from newer versions
# makepkg cannot (and should not) be run as root, so a dummy user is created:
RUN useradd -m notroot && \
# the Archlinux keyring, git, wget are installed for later use, as well as the base-devel package group
pacman -Sy --noconfirm git && \
 pacman -Sy --noconfirm inetutils && \
pacman -Sy --noconfirm wget && \
# Allow notroot to run stuff as root (to install dependencies):
 echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot 
# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR /home/notroot
# install yay for later use in install
RUN pwd && ls && git clone https://aur.archlinux.org/yay-bin.git && \
cd yay-bin && \
makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1 && \
# clone pvtest repo to allow for installation of previuous versions of boost, boost-libs, and libx11; current versions of these resulted in build issues
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg && cd Arch && \ 
sudo pacman -U --noconfirm boost-libs-1.69.0-1-x86_64.pkg.tar.xz && \ 
sudo pacman -U --noconfirm boost-1.69.0-1-x86_64.pkg.tar.xz && \
sudo pacman -U --noconfirm libx11-1.7.0-1-x86_64.pkg.tar.zst && \
# building icu63, which UHD will not build without
git clone https://aur.archlinux.org/icu63.git && \
cd icu63 && \
 makepkg --noconfirm --syncdeps --rmdeps --install --clean && \
gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1
WORKDIR /home/notroot/libuhd
#chown command used to give proper permissions in build directories
RUN sudo chown -R notroot /home/notroot/libuhd && \
sudo wget -v https://raw.githubusercontent.com/pervices/pvpkg/master/ArchPython2/UHD/PKGBUILD && \
# use wget to collect UHD PKGBUILD from Github, and create the package with the dependencies speified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
# installs UHD
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed 
# moving test files to same directory as UHD
WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2
RUN ls && sudo chown -R notroot /home/notroot/yay-bin/pvpkg/ArchPython2 && \
 mv test-only.sh variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd 
# installs pygtk, since correct version is not available for pacman install in PKGBUILD
WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2/pygtk
RUN sudo chown -R notroot /home/notroot/yay-bin/pvpkg/ArchPython2/pygtk && \
yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed
WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2/pyqt4
RUN sudo chown -R notroot /home/notroot/yay-bin/pvpkg/ArchPython2/pyqt4 && \
#yay -S --noconfirm python-pyqt4 && \
# installs qt4, since correct version is not available for pacman install in PKGBUILD
yay -Sy --noconfirm qt4 && \
# installing sip from tar file, since it is needed for PyQt4 installation
tar -zxvf sip-4.19.24.tar.gz && \
cd sip-4.19.24 && \
#sudo python2 configure.py --sip-module PyQt4.sip --no-dist-info --no-tools && \
sudo python2 configure.py && \
sudo make && \
sudo make install 
# installs PyQt4 from tar, with necessary confirm license and qmake (from qt4) install directory options
WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2/pyqt4 
RUN tar -zxvf PyQt4_gpl_x11-4.12.3.tar.gz && \
cd PyQt4_gpl_x11-4.12.3 && \
python2 configure.py --confirm-license --qmake /usr/lib/qt4/bin/qmake && \
sudo make && \
sudo make install
#WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2/qt4
#RUN sudo chown -R notroot /home/notroot/yay-bin/pvpkg/ArchPython2/qt4 && \
#yay -Sy --noconfirm \
 #  $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
# makepkg --noconfirm --syncdeps --install --needed
# install qwt-qt4 from PKGBUILD, since it is no longer available from Pacman
WORKDIR /home/notroot/yay-bin/pvpkg/ArchPython2/qwt-qt4
RUN sudo chown -R notroot /home/notroot/yay-bin/pvpkg/ArchPython2/qwt-qt4 && \
yay -Sy --noconfirm \
  $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
 makepkg --noconfirm --syncdeps --install --needed
#sudo pacman -Sy --noconfirm python2-gobject && \
#sudo pacman -U --noconfirm pygtk-2.24.0-3-x86_64.pkg.tar.xz 
WORKDIR /home/notroot/gnuradio
# ensure Python2 is grabbed for Python instructions
RUN echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc && \
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc && \
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.profile && \
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.profile && \
# install cheetah Python2 module with pip, since it is no longer available using pacman
pip2 install Cheetah 
# use wget to collect GnuRadio PKGBUILD from Github, and create the package with the dependencies specified from the PKGBUILD; sudo chown command allows user notroot to build in this directory
RUN sudo wget 'https://raw.githubusercontent.com/pervices/pvpkg/master/ArchPython2/GNURadio/PKGBUILD' &&  \ 
sudo chown -R notroot /home/notroot/gnuradio && \
  makepkg --noconfirm --syncdeps --install && gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key CB9387521E1EE0127DA804843FDBB55084CC5D84 && \
 yay -Sy --noconfirm \
$(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]})) && \
makepkg --noconfirm --install --needed
#test ping commands, then give tests executable permission, and run them twice; non-critical issues can be present on fresh build, so second run clears these up
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


