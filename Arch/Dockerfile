FROM archlinux

# makepkg cannot (and should not) be run as root:
RUN useradd -m notroot

RUN pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Sy --noconfirm base-devel git && \
    pacman -Syu --noconfirm
RUN pacman -Syu --noconfirm wget

# Allow notroot to run stuff as root (to install dependencies):
RUN echo "notroot ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/notroot

# Continue execution (and CMD) as notroot:
USER notroot
WORKDIR home/notroot
RUN wget https://raw.githubusercontent.com/than97/pvpkg/master/Arch/PKGBUILD
RUN ls
RUN git clone https://aur.archlinux.org/yay-bin.git && \
    cd yay-bin && \
    makepkg --noconfirm --syncdeps --rmdeps --install --clean
RUN gpg --keyserver ipv4.pool.sks-keyservers.net --recv-key 330239C1C4DAFEE1
RUN yay -Sy --noconfirm \
   $(pacman --deptest $(source ./PKGBUILD && echo ${depends[@]} ${makedepends[@]}))
RUN makepkg --noconfirm --install
