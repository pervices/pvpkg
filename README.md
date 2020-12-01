# pvpkg
Used to host Jenkinsfile and any other package dependencies and documentation

h1. Clean Installation

If you don't previously have jenkins installed, the following notes may help;

Steps for Jenkins container configuration to ensure package can be built successfully:

1. From command line, launch a Jenkins container using this command: 

docker container run -idt --name jenkins -P -p  8080:8080 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:2.178-slim

2. To install the docker client in the container, run the following commands: 

docker exec -it -u root jenkins bash

apt-get update && \
apt-get -y install apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common && \
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey && \
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
   $(lsb_release -cs) \
   stable" && \
apt-get update && \
apt-get -y install docker-ce

exit

3. Run the following commands to adjust user permissions within the container: 

  sudo groupadd docker
  sudo usermod -aG docker $USER   //Be careful with this.
  chmod 644 /var/run/docker.sock  //Try using 664 if members of the group also need write permission on this bit.
  docker restart jenkins


h2. Build Process

The Jenkinsfile will automatically build UHD for Arch, Centos 7 (not fully supported), Centos 8, Ubuntu 18.06, Ubuntu 20.04.

The file is divided into a number of stages that first build UHD within a container, then run the pvtest repo against the hardware, and then publish the packages on github if they succeed.

