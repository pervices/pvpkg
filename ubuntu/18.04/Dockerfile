FROM ubuntu:18.04

RUN apt update
RUN apt-get -y install git 
RUN git clone https://github.com/pervices/uhd.git
RUN cd bin

RUN cmake ..

RUN make -j8

RUN sudo make install
