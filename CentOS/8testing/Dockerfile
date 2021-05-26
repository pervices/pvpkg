FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget &&\
rpmdev-setuptree && \
ls && ls && ls && ls && ls && ls && ls && ls && ls && ls && ls && git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8testing && \
mv uhd.spec /root/rpmbuild/SPECS && \
mv master.tar.gz /root/rpmbuild/SOURCES
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y uhd.spec && \
QA_RPATHS=$(( 0x0001|0x0002 )) rpmbuild -ba uhd.spec
RUN sleep 10000 
