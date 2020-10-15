FROM ubuntu:18.04

RUN apt update
RUN apt-get -y install git 
RUN apt-get -y install cmake
RUN apt-get -y install build-essential
RUN apt-get -y install python2


WORKDIR /home
RUN git clone https://github.com/pervices/uhd.git
RUN mkdir uhdlib
WORKDIR /home/uhdlib
RUN cmake /home/uhd/host
RUN make -j8
RUN sudo make install
