FROM ubuntu:20.04

# set environemnt to non-interactive to stop input prompts that occurred on certain instructions
ENV DEBIAN_FRONTEND=noninteractive

# install necessary components for UHD; install some Python components using pip; use version 1.67 of boost to prevent issues
RUN apt update && \
touch test.txt && \
echo "This is a test file" > test.txt
