FROM archlinux/archlinux:base-devel-20230322.0.136594
ARG DOCKER_USER=docker

# Installing required binaries
RUN pacman -Sy --noconfirm archlinux-keyring git cmake clang icu inetutils iproute2 wget net-tools xorg-xclock xorg-xauth xterm python-rich python-reportlab

# Creating users and groups
RUN groupadd "$DOCKER_USER" && \
    groupadd sudo && \
    useradd -ms /bin/bash -g $DOCKER_USER -G sudo $DOCKER_USER && \
    echo "${DOCKER_USER}:${DOCKER_USER}" | chpasswd  && \
    echo "$DOCKER_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Changing user
USER $DOCKER_USER

# Installing yay
WORKDIR /home/$DOCKER_USER
RUN git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg --noconfirm --syncdeps --rmdeps --install --clean --needed && yay -Sy --noconfirm su-exec

# Installing UHD
WORKDIR /home/$DOCKER_USER/uhd
COPY PKGBUILD-uhd PKGBUILD
RUN yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && makepkg --noconfirm --syncdeps --rmdeps --install --clean --needed

# Installing GRC
WORKDIR /home/$DOCKER_USER/gnuradio
COPY PKGBUILD-grc PKGBUILD
RUN yay -Sy --noconfirm $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]})) && makepkg --noconfirm --syncdeps --rmdeps --install --clean --needed

# Finishing up
WORKDIR /home/$DOCKER_USER
COPY SimpleShipTest.grc SimpleShipTest.grc
RUN touch .Xauthority && rm -rf gnuradio uhd yay-bin
USER root
COPY entrypoint /
RUN chmod 0755 /entrypoint && \
    sed "s/\$DOCKER_USER/$DOCKER_USER/g" -i /entrypoint
ENTRYPOINT ["/entrypoint"]
