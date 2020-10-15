FROM ubuntu:18.04

RUN apt update
RUN apt-get -y install git 
RUN apt-get -y install cmake
WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
WORKDIR /home/uhd/host
RUN cmake 
RUN make -j8
RUN sudo make install
