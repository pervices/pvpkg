FROM archlinux/archlinux:base-devel-20230322.0.136594
RUN useradd -m notroot 
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot
RUN pacman -Sy --noconfirm archlinux-keyring git cmake clang icu inetutils iproute2 wget net-tools xorg-xclock xorg-xauth xterm
USER notroot
WORKDIR /home/notroot
RUN git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg --noconfirm --syncdeps --rmdeps --install --clean 
RUN git clone https://github.com/pervices/pvpkg.git
WORKDIR /home/notroot/testing
WORKDIR /home/notroot/libuhd
COPY PKGBUILD-uhd PKGBUILD
RUN sudo chown -R notroot /home/notroot/testing
RUN sudo chown -R notroot /home/notroot/libuhd
RUN yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]}))
RUN makepkg --noconfirm --syncdeps --install --needed
WORKDIR /home/notroot/pvpkg/Testing
RUN mv test-only-Arch.sh variables.sh /home/notroot/testing && mv tests /home/notroot/testing
WORKDIR /home/notroot/libuhd/src/uhd/host
RUN sudo chown -R notroot /home/notroot/libuhd/src/uhd/host && cp -R examples /home/notroot/libuhd
WORKDIR /home/notroot/gnuradio
COPY PKGBUILD-grc PKGBUILD
RUN sudo chown -R notroot /home/notroot/gnuradio && makepkg --noconfirm --syncdeps --install && yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && makepkg --noconfirm --install --needed
WORKDIR /home/notroot/testing
COPY SimpleShipTest.grc DockerSimpleShipTest.grc
RUN chmod +x test-only-Arch.sh && chmod +x variables.sh && chmod +x tests
WORKDIR /home/notroot
RUN touch touch .Xauthority
