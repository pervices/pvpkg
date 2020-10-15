FROM ubuntu:18.04

RUN apt update
RUN apt-get -y install git 
RUN apt-get -y install cmake
WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
WORKDIR /home
RUN mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake /home/uhd/host
RUN make -j8
RUN sudo make install
