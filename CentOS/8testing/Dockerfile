FROM centos:8
WORKDIR /home/notroot
WORKDIR /home/notroot/testing
WORKDIR /home
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget cmake &&\
rpmdev-setuptree && \
wget https://github.com/pervices/uhd/archive/refs/heads/master.tar.gz && \
mv master.tar.gz /root/rpmbuild/SOURCES && \
git clone -b maint-3.9 https://github.com/pervices/gnuradio.git && \
git clone --recursive https://github.com/gnuradio/volk.git && \
tar -czvf volk.tar.gz volk && \
mv volk.tar.gz /root/rpmbuild/SOURCES && \
#cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ 
ls && ls && git clone https://github.com/pervices/pvpkg.git && \
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
rpm -i uhd*.rpm
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba volk.spec && \
cd ../RPMS/x86_64 && \
rpm -i volk-3.9-volk.x86_64.rpm
WORKDIR /root/rpmbuild/SPECS
RUN QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild --define 'debug_package %{nil}' -ba gnuradio.spec && \
cd ../RPMS/x86_64 && \
sleep 10000 && \
rpm -i python3*.rpm && rpm -i gnuradio*.rpm && \
sleep 10000

