Installation Instructions for .deb Files:



The first step is installing UHD, by running this command from within pvpkg/ubuntu/20.04/pkg/uhd :

dpkg -i uhd*.deb

This command will most likely fail with missing dependencies, but the install will work by subsequently running :

apt --fix-broken install

Gnuradio is installed similarly by first installing all the necesary library .deb files with this command from within pvpkg/ubuntu/20.04/pkg/gnuradio :

dpkg -i libgnuradio*.deb

The full Debian package is installed by running this command from the same directory as the previous command:

dpkg -i gnuradio*.deb
