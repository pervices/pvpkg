FROM archlinux/archlinux:base-devel-20230322.0.136594
ARG DOCKER_USER=docker
# RUN useradd -m notroot 
# RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

RUN pacman -Sy --noconfirm archlinux-keyring git cmake clang icu inetutils iproute2 wget net-tools xorg-xclock xorg-xauth xterm
# Create a group and user
RUN groupadd "$DOCKER_USER" && \
    groupadd sudo && \
    useradd -ms /bin/bash -g $DOCKER_USER -G sudo $DOCKER_USER && \
    echo "${DOCKER_USER}:${DOCKER_USER}" | chpasswd  && \
    echo "$DOCKER_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
    
USER $DOCKER_USER
WORKDIR /home/$DOCKER_USER
RUN git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg --noconfirm --syncdeps --rmdeps --install --clean 
RUN git clone https://github.com/pervices/pvpkg.git
WORKDIR /home/$DOCKER_USER/testing
WORKDIR /home/$DOCKER_USER/libuhd
COPY PKGBUILD-uhd PKGBUILD
RUN sudo chown -R $DOCKER_USER /home/$DOCKER_USER/testing
RUN sudo chown -R $DOCKER_USER /home/$DOCKER_USER/libuhd
RUN yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]}))
RUN makepkg --noconfirm --syncdeps --install --needed
WORKDIR /home/$DOCKER_USER/pvpkg/Testing
RUN mv test-only-Arch.sh variables.sh /home/$DOCKER_USER/testing && mv tests /home/$DOCKER_USER/testing
WORKDIR /home/$DOCKER_USER/libuhd/src/uhd/host
RUN sudo chown -R $DOCKER_USER /home/$DOCKER_USER/libuhd/src/uhd/host && cp -R examples /home/$DOCKER_USER/libuhd
WORKDIR /home/$DOCKER_USER/gnuradio
COPY PKGBUILD-grc PKGBUILD
RUN sudo chown -R $DOCKER_USER /home/$DOCKER_USER/gnuradio && makepkg --noconfirm --syncdeps --install && yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && makepkg --noconfirm --install --needed
WORKDIR /home/$DOCKER_USER/testing
COPY SimpleShipTest.grc DockerSimpleShipTest.grc
RUN chmod +x test-only-Arch.sh && chmod +x variables.sh && chmod +x tests
WORKDIR /home/$DOCKER_USER
RUN touch touch .Xauthority
RUN yay -Sy --noconfirm su-exec
RUN sudo pacman -Sy --noconfirm python-rich python-reportlab
USER root

COPY files /
RUN chmod 0755 /entrypoint && \
    sed "s/\$DOCKER_USER/$DOCKER_USER/g" -i /entrypoint

ENTRYPOINT ["/entrypoint"]
