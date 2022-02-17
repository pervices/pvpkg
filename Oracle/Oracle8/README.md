Installation Instructions for CentOS8 RPM Packages






1. Get latest versions of uhdpv and gnuradio rpms from https://www.files.pervices.com/latest/sw/centos8/ and decompress the archives.




2. To install uhd, run the following command in the directory with the uhd rpms: 

     rpm -i uhd*.rpm



3. To install gnuradio, run the following commands in the directory with the gnuradio rpms:

     rpm -i volk*.rpm
     rpm -i libgnuradio*.rpm && rpm -i python3*.rpm && rpm -i gnuradio*.rpm

            
