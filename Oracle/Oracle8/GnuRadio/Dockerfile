FROM oraclelinux:8.5
#FROM centos:8
WORKDIR /home/notroot
WORKDIR /home/notroot/testing
WORKDIR /home/artifacts
WORKDIR /home
RUN yum -y update && \
yum -y install dnf-plugins-core oracle-epel-release-el8 make gcc rpm-build git rpmdevtools wget cmake python3-pip &&\
dnf config-manager --set-enabled ol8_codeready_builder && \
pip3 install retrying pygccxml pyqtgraph==0.11.1 && \
cd /usr/local/lib/python3.6/site-packages/ && \
mv pygccxml  pygccxml-2.2.1.dist-info  pyqtgraph  pyqtgraph-0.11.1.dist-info  retrying-1.3.3-py3.6.egg-info  retrying.py /usr/lib/python3.6/site-packages
WORKDIR /home
RUN rpmdev-setuptree && \
git clone -b master https://github.com/pervices/uhd.git && \
tar -czvf uhd.tar.gz uhd && \
mv uhd.tar.gz /root/rpmbuild/SOURCES && \
git clone -b maint-3.10 https://github.com/gnuradio/gnuradio.git && \
git clone --branch v2.4.1 --recursive https://github.com/gnuradio/volk.git && \
tar -czvf volk.tar.gz volk && \
mv volk.tar.gz /root/rpmbuild/SOURCES && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Oracle/Oracle8 && \
mv uhd.spec gnuradio.spec volk.spec /root/rpmbuild/SPECS && \
mv InstallInstructionsOracle /home/uhd && \
cd ../../Testing && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
mv test-only.sh /home/notroot/testing && \
rm /home/gnuradio/cmake/Modules/GrMinReq.cmake && \
mv /home/pvpkg/Oracle/Oracle8/GrMinReq.cmake /home/gnuradio/cmake/Modules
WORKDIR /home
RUN tar -czvf gnuradio-maint-3.10.tar.gz gnuradio && \
mv gnuradio-maint-3.10.tar.gz /root/rpmbuild/SOURCES
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep -y uhd.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba uhd.spec && \
cd ../RPMS/x86_64 && \
rpm -i uhd*.rpm && \
mv uhd*.rpm /home/uhd
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep  -y gnuradio.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba volk.spec && \
cd ../RPMS/x86_64 && \
rpm -i volk-3.9-volk.x86_64.rpm && \
mv volk-3.9-volk.x86_64.rpm /home/volk
WORKDIR /root/rpmbuild/SPECS
RUN QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba gnuradio.spec && \
cd ../RPMS/x86_64 && \
rpm -i libgnuradio*.rpm && rpm -i python3*.rpm && rpm -i gnuradio*.rpm && \
mv libgnuradio*.rpm python3*.rpm gnuradio*.rpm /home/gnuradio
WORKDIR /root/rpmbuild/SPECS
RUN mv uhd.spec gnuradio.spec /home/uhd
WORKDIR /home/uhd 
RUN mv uhd-3.13.0.0-master.x86_64.rpm uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mkdir uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv uhdpv*.rpm uhd.spec InstallInstructionsOracle gnuradio.spec uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").tar.gz uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").tar.gz /home/artifacts
WORKDIR /home/volk
RUN mv volk-3.9-volk.x86_64.rpm volk-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv volk-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm /home/gnuradio
WORKDIR /home/gnuradio
RUN mv gnuradio-3.9-maint.x86_64.rpm gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv gnuradio-devel-3.9-maint.x86_64.rpm gnuradio-devel-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv gnuradio-doc-3.9-maint.x86_64.rpm gnuradio-doc-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv gnuradio-examples-3.9-maint.x86_64.rpm gnuradio-examples-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv libgnuradio-3.9-maint.x86_64.rpm libgnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv python3-gnuradio-3.9-maint.x86_64.rpm python3-gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mkdir gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv *.rpm gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
tar -czvf gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").tar.gz gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv gnuradio-$(git describe --abbrev=8 --always --long)-$(date "+%F").tar.gz /home/artifacts
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests 







