FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools &&\
rpmdev-setuptree && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8notsource && \
rpm -ivh ./gnuradio-3.8.0.0-6.el8.src.rpm && \
cd /root/rpmbuild/SPECS && \
dnf builddep --enablerepo=powertools -y gnuradio.spec && \
rpmbuild -bp gnuradio.spec && \
rpmbuild -ba --define 'debug_package %{nil}' gnuradio.spec && \
sleep 10000
 




