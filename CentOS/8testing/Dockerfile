FROM centos:8
WORKDIR /home/notroot
WORKDIR /home/notroot/testing
WORKDIR /home/artifacts
WORKDIR /home
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget cmake &&\
rpmdev-setuptree && \
git clone -b master https://github.com/pervices/uhd.git && \
tar -czvf uhd.tar.gz uhd && \
mv uhd.tar.gz /root/rpmbuild/SOURCES && \
git clone -b maint-3.9 https://github.com/pervices/gnuradio.git && \
git clone --recursive https://github.com/gnuradio/volk.git && \
tar -czvf volk.tar.gz volk && \
mv volk.tar.gz /root/rpmbuild/SOURCES && \
#cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ 
ls && ls && ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8testing && \
mv uhd.spec gnuradio.spec volk.spec /root/rpmbuild/SPECS && \
cd ../../Testing && \
mv variables.sh /home/notroot/testing && \
mv tests /home/notroot/testing && \
mv test-only.sh /home/notroot/testing && \
rm /home/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc && \
mv /home/pvpkg/ubuntu/20.04/modified/uhd_types_python_mod.cc /home/gnuradio/gr-uhd/python/uhd/bindings && \
mv /home/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python_mod.cc /home/gnuradio/gr-uhd/python/uhd/bindings/uhd_types_python.cc
WORKDIR /home
RUN tar -czvf gnuradio-maint-3.9.tar.gz gnuradio && \
mv gnuradio-maint-3.9.tar.gz /root/rpmbuild/SOURCES
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y uhd.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba uhd.spec && \
cd ../RPMS/x86_64 && \
rpm -i uhd*.rpm && \
mv uhd*.rpm /home/uhd
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba volk.spec && \
cd ../RPMS/x86_64 && \
rpm -i volk-3.9-volk.x86_64.rpm && \
mv volk-3.9-volk.x86_64.rpm /home/volk
WORKDIR /root/rpmbuild/SPECS
RUN QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild --define 'debug_package %{nil}' -ba gnuradio.spec && \
cd ../RPMS/x86_64 && \
rpm -i libgnuradio*.rpm && rpm -i python3*.rpm && rpm -i gnuradio*.rpm && \
mv libgnuradio*.rpm python3*.rpm gnuradio*.rpm /home/gnuradio
WORKDIR /home/uhd 
RUN mv uhd-3.13.0.0-master.x86_64.rpm uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv uhd-debuginfo-3.13.0.0-master.x86_64.rpm uhdpv-debuginfo-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mv uhd-debugsource-3.13.0.0-master.x86_64.rpm uhdpv-debugsource-$(git describe --abbrev=8 --always --long)-$(date "+%F").rpm && \
mkdir uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
mv uhdpv*.rpm uhdpv-$(git describe --abbrev=8 --always --long)-$(date "+%F") && \
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







