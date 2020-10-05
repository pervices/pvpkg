FROM archlinux

COPY PKGBUILD /home/PKGBUILD

# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot

RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm

# Allow notroot to run stuff as root (to install dependencies):
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR /home
RUN git clone https://aur.archlinux.org/yay-bin.git && \
    cd yay-bin && \
    makepkg --noconfirm --syncdeps --rmdeps --install --clean

RUN makepkg
RUN sudo pacman -U --noconfirm *.pkg.tar.xz
