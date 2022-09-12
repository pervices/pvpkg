FROM oraclelinux:8.6
WORKDIR /home/notroot
WORKDIR /home/notroot/testing
WORKDIR /home/artifacts
WORKDIR /home
RUN yum -y update && \
yum -y install dnf-plugins-core oracle-epel-release-el8 make gcc rpm-build git rpmdevtools wget cmake python3-pip &&\
#dnf config-manager --set-enabled ol8_codeready_builder && \
#pip3 install retrying pygccxml pyqtgraph==0.11.1 && \
pip3 install pygccxml && \
cd /usr/local/lib/python3.6/site-packages/ && \
#mv pygccxml  pygccxml-2.2.1.dist-info  pyqtgraph  pyqtgraph-0.11.1.dist-info  retrying-1.3.3-py3.6.egg-info  retrying.py /usr/lib/python3.6/site-packages
mv  pygccxml  pygccxml-2.2.1.dist-info /usr/lib/python3.6/site-packages
WORKDIR /home
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Testing && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
mv test-only.sh /home/notroot/testing
WORKDIR /home/uhd 
RUN wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/centos8/uhd/ && \
tar -xvzf uhd*.tar.gz && \
#cd uhd* && \
dnf builddep -y uhd.spec && \
rpm -i uhd*.rpm
WORKDIR /home/volk
WORKDIR /home/gnuradio
RUN wget -r -np -nH --cut-dirs=4 --reject "index*"  http://files.pervices.com/latest/sw/centos8/gnuradio/ && \
tar -xvzf gnuradio*.tar.gz && \
cd gnuradio* && \
dnf builddep -y gnuradio.spec && \
rpm -i volk*.rpm && rpm -i libgnuradio*.rpm && rpm -i python3*.rpm && rpm -i gnuradio*.rpm
WORKDIR /home/notroot/testing
RUN pip3 install numpy==1.16.4 && \
chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 







