FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget &&\
rpmdev-setuptree && \
wget https://github.com/pervices/uhd/archive/refs/heads/master.tar.gz && \
mv master.tar.gz /root/rpmbuild/SOURCES && \
wget https://github.com/pervices/gnuradio/archive/refs/heads/maint-3.9.tar.gz && \
mv maint-3.9.tar.gz /root/rpmbuild/SOURCES && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8testing && \
mv uhd.spec gnuradio.spec /root/rpmbuild/SPECS
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba gnuradio.spec && \
sleep 10000 && \
RUN dnf builddep --enablerepo=powertools -y uhd.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba uhd.spec && \
cd ../RPMS/x86_64 && \
rpm -i uhd*.rpm 

