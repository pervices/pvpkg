FROM centos:8
RUN yum -y update && \
yum -y install yum-utils rpm-build git
WORKDIR /home/notroot/libuhd
RUN git clone https://github.com/pervices/pvpkg.git && \
cd pvpkg/Arch && \
mv variables.sh /home/notroot/libuhd && \
mv tests /home/notroot/libuhd && \
cd ../ubuntu && \
mv test-only.sh /home/notroot/libuhd && \
cd ../CentOS/8notsource && \
mv gnuradio-3.8.0.0-6.el8.src.rpm /home/notroot/libuhd
RUN rpm -ivh ./gnuradio-3.8.0.0-6.el8.src.rpm && \ 
ls && \
yum-builddep gnuradio-3.8.0.0-6.el8



