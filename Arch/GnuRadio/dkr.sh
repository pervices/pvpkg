#! /bin/bash -e

PV_DOCKER=pvtesting/archlinux:20230322.0.136594-a72fd3ef-v3.10.6.0-rc1
DISPLAY_NUMBER=$(echo $DISPLAY | cut -d. -f1 | cut -d: -f2)
AUTH_COOKIE=$(xauth list | grep "^$(hostname)/unix:${DISPLAY_NUMBER} " | awk '{print $3}')
DISPLAY_HOST=$DISPLAY
dkr() {
    CMD=$@
    docker run --rm \
               --interactive \
               --privileged \
               --tty \
               --env DISPLAY \
               --network host \
               --volume $(pwd):$(pwd) \
               --workdir $(pwd) \
               --env GGID=$(id -g) \
               --env UUID=$(id -u) \
               $PV_DOCKER \
               /bin/bash -c \
               "xauth add $DISPLAY_HOST . $AUTH_COOKIE && $CMD"
}

PS1='[\[\e[1;31m\]\u-docker\[\e[1;0m\]@\h \[\e[1;34m\]\W\[\e[1;0m\]]\$ '
