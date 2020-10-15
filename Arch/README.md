# pvpkg
Used to host Jenkinsfile and any other package dependencies and documentation

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
  sudo usermod -aG docker $USER
  chmod 777 /var/run/docker.sock
  docker restart jenkins
  
