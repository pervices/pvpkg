FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget cmake &&\
rpmdev-setuptree && \
wget https://github.com/pervices/uhd/archive/refs/heads/master.tar.gz && \
mv master.tar.gz /root/rpmbuild/SOURCES && \
wget https://github.com/pervices/gnuradio/archive/refs/heads/maint-3.9.tar.gz && \
mv maint-3.9.tar.gz /root/rpmbuild/SOURCES && \
git clone --recursive https://github.com/gnuradio/volk.git && \
tar -czvf volk.tar.gz volk && \
mv volk.tar.gz /root/rpmbuild/SOURCES && \
#cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ 
ls && ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8testing && \
mv uhd.spec gnuradio.spec volk.spec /root/rpmbuild/SPECS 
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y uhd.spec && \
#QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba uhd.spec  && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba volk.spec -vv
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild --define 'debug_package %{nil}' -ba gnuradio.spec && \
cd ../RPMS/x86_64 && \
rpm -i uhd*.rpm 

