FROM archlinux

COPY PKGBUILD /PKGBUILD

# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot

RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm

# Allow notroot to run stuff as root (to install dependencies):
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers

# Continue execution (and CMD) as notroot:
USER notroot
RUN makepkg
RUN sudo pacman -U --noconfirm *.pkg.tar.xz
