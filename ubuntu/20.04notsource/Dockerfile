FROM ubuntu:20.04
WORKDIR /home/notroot/libuhd
RUN apt-get update && \
apt-get install software-properties-common && \
add-apt-repository ppa:ettusresearch/uhd && \
apt-get update && \
apt-get install libuhd-dev libuhd003 uhd-host && \
 add-apt-repository ppa:gnuradio/gnuradio-releases && \
apt-get update && \
apt-get install gnuradio
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd
WORKDIR /home/notroot/libuhd
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
ldconfig && \
./test-only.sh
