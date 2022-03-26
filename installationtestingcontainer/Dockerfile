FROM oraclelinux:8.5
WORKDIR /home
RUN yum -y update && \
yum -y install dnf-plugins-core oracle-epel-release-el8 make gcc rpm-build git rpmdevtools wget cmake python3-pip &&\
dnf config-manager --set-enabled ol8_codeready_builder && \
pip3 install retrying pygccxml && \
cd /usr/local/lib/python3.6/site-packages/ && \
mv pygccxml pygccxml-2.2.1.dist-info /usr/lib/python3.6/site-packages
WORKDIR /home
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Oracle/Oracle8 && \
mv uhd.spec gnuradio.spec volk.spec /home
RUN sleep 10000

