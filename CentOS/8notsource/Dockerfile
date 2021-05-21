FROM centos:8
RUN yum -y update && \
yum -y install dnf-plugins-core epel-release make gcc rpm-build git rpmdevtools wget &&\
rpmdev-setuptree && \
git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/CentOS/8notsource && \
wget https://download-ib01.fedoraproject.org/pub/epel/8/Everything/SRPMS/Packages/u/uhd-3.15.0.0-0.1.rc2.el8.src.rpm && \
rpm -ivh ./uhd-3.15.0.0-0.1.rc2.el8.src.rpm && \
rpm -ivh ./gnuradio-3.8.0.0-6.el8.src.rpm 
WORKDIR /home/notroot/testing
WORKDIR /pvpkg/Testing
RUN mv variables.sh /home/notroot/testing && \
mv tests home/notroot/testing && \
mv test-only.sh home/notroot/testing
WORKDIR /root/rpmbuild/SPECS 
RUN dnf builddep --enablerepo=powertools -y uhd.spec && \
rpmbuild -bp uhd.spec && \
rpmbuild --rebuild --define 'debug_package %{nil}' /pvpkg/CentOS/8notsource/uhd-3.15.0.0-0.1.rc2.el8.src.rpm && \   
cd ../RPMS/x86_64 && \
yum -y install python3-tkinter && \
rpm -i uhd*.rpm 
WORKDIR /root/rpmbuild/SPECS
RUN dnf builddep --enablerepo=powertools -y gnuradio.spec && \
rpmbuild -bp gnuradio.spec && \
rpmbuild --rebuild --define 'debug_package %{nil}' /pvpkg/CentOS/8notsource/gnuradio-3.8.0.0-6.el8.src.rpm && \
cd ../RPMS/x86_64 && \
rpm -i *gnuradio*.rpm 
WORKDIR /home/notroot/testing
RUN chmod +x test-only.sh && \
chmod +x variables.sh && \
chmod +x tests && \
./test-only.sh
