FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget &&\
rpmdev-setuptree && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8testing
RUN sleep 10000
