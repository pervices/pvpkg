#! /bin/bash -e

PV_DOCKER=pvtesting/archlinux:20230322.0.136594-a72fd3ef-v3.10.6.0-rc1-test
PV_DOCKER_TAR=$(echo $PV_DOCKER | sed s:/:-:g)
NUM_THREAD=$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')
sed -i s/j4/j$NUM_THREAD/g PKGBUILD-uhd
sed -i s/j4/j$NUM_THREAD/g PKGBUILD-grc
docker build -t $PV_DOCKER .
# docker save -o $PV_DOCKER_TAR.tar $PV_DOCKER
