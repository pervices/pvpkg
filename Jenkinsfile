pipeline { 

// citests agents used to build and test repo.
    agent {
	label 'waveci'
    }
parameters {
        choice(name: "CI_BUILD_TYPE", choices: ["UHD_ONLY", "FULL"], description: "Select whether to only build UHD package or to build Gnuradio with UHD. Gnuradio has a considerably longer compile time, so FULL should not be slected if a new UHD package is required quickly.")
        choice(name: "BRANCH", choices: ["master", "testing"], description: "Select whether to build package from master branch and push to latest on the fileserver or to build from a testing branch and push to testing on the fileserver.")
		booleanParam(name: "ENABLE_ARCH", defaultValue: true, description: "Select whether to generate packages for Archlinux.")
		booleanParam(name: "ENABLE_UBUNTU", defaultValue: true, description: "Select whether to generate packages for Ubuntu 20.04.")
		booleanParam(name: "ENABLE_ORACLE", defaultValue: true, description: "Select whether to generate packages for Oracle Linux 8.")
		booleanParam(name: "CLEAN", defaultValue: true, description: "Select whether to clean Docker cache and remove all Docker images after build. This step is necessary in order to ensure all Git commits and changes are applied to the subsequent build. Cleaning should be disabled for failing builds that require troubleshooting.")
		booleanParam(name: "ENABLE_TESTING", defaultValue: true, description: "Select whether to run CI tests for enabled build distributions after successful build.")
	}
    stages {


        stage('Build UHD and GNU Radio') {
        parallel {

                stage('ArchLinux UHD') { 
                    //Build UHD only
                    when {
                        allOf {
                          expression {params.ENABLE_ARCH == true}
                          expression {params.CI_BUILD_TYPE == 'UHD_ONLY'}
                          expression {params.BRANCH == 'master'}
                        }
                        }
                            steps { 
                        script { 
                                dir("${env.WORKSPACE}/Arch/UHD") {
                                dockerImageArch = docker.build("arch:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
                                env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Arch/UHD"
                                sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/archlinux/uhd/*' && \
                                scp -P 237 libuhdpv* filespervices@files.pervices.com:/home/filespervices/www/latest/sw/archlinux/uhd/"
                        }
                        }
                        }
                        }
                        }
                        
                        
                        
                        
                  stage('ArchLinux Full') { 
                 	//Build UHD and Gnuradio
                     when {
                         allOf {
                          expression {params.ENABLE_ARCH == true}
                          expression {params.CI_BUILD_TYPE == 'FULL'}
                          expression {params.BRANCH == 'master'}
                        }
                        }
                             steps { 
                        script { 
                                dir("${env.WORKSPACE}/Arch/GnuRadio") {
                                dockerImageArch = docker.build("arch:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
                                env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Arch/GnuRadio"
                                sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/archlinux/uhd/* && rm -f /home/filespervices/www/latest/sw/archlinux/gnuradio/*' && \
                                scp -P 237 libuhdpv* filespervices@files.pervices.com:/home/filespervices/www/latest/sw/archlinux/uhd/ && \
                                scp -P 237 gnuradio* filespervices@files.pervices.com:/home/filespervices/www/latest/sw/archlinux/gnuradio/"                        
                        }
                        } 
                        }
                        }
                        }


               stage('Ubuntu 20.04 UHD') { 
               //Build UHD
                     when {
                          allOf {
                           expression {params.ENABLE_UBUNTU == true}
                           expression {params.CI_BUILD_TYPE == 'UHD_ONLY'}
                           expression {params.BRANCH == 'master'}
                       }
                       }
                            steps { 
                        script { 
                                dir("${env.WORKSPACE}/ubuntu/20.04/uhd") {
                                dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                                env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/ubuntu/20.04/uhd"
                                sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/ubuntu20.04/uhd/*' && \
                                scp -P 237 uhdpv*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/ubuntu20.04/uhd/"
                       } 
                       }
                       }
                       }
                       }
                       
                         stage('Ubuntu 20.04 UHD Testing Branch') { 
               //Build UHD
                     when {
                          allOf {
                           expression {params.ENABLE_UBUNTU == true}
                           expression {params.CI_BUILD_TYPE == 'UHD_ONLY'}
                           expression {params.BRANCH == 'testing'}
                       }
                       }
                            steps { 
                        script { 
                                dir("${env.WORKSPACE}/ubuntu/20.04/testing/uhd") {
                                dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                                env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/ubuntu/20.04/testing/uhd"
                                sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/testing/sw/ubuntu20.04/uhd/*' && \
                                scp -P 237 uhdpv*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/testing/sw/ubuntu20.04/uhd/"
                       } 
                       }
                       }
                       }
                       }
                       
                stage('Ubuntu 20.04 Full') {
               //Build UHD
                     when {
                          allOf {
                            expression {params.ENABLE_UBUNTU == true}
                            expression {params.CI_BUILD_TYPE == 'FULL'}
                            expression {params.BRANCH == 'master'}
                       }
                       }
                               steps { 
                        script { 
                                dir("${env.WORKSPACE}/ubuntu/20.04/gnuradio") {
                                dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                                env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/ubuntu/20.04/gnuradio"
                                sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/ubuntu20.04/uhd/* && rm -f /home/filespervices/www/latest/sw/ubuntu20.04/gnuradio/*' && \
                                scp -P 237 uhdpv*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/ubuntu20.04/uhd/ && \
                                scp -P 237 gnuradio*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/ubuntu20.04/gnuradio/"
                       } 
                       }
                       }
                       }
                       }

                                      
               stage('RPM_OracleLinux UHD') {
               //Build UHD
                    when {
                          allOf {
                           expression {params.ENABLE_ORACLE == true}
                           expression {params.CI_BUILD_TYPE == 'UHD_ONLY'}
                           expression {params.BRANCH == 'master'}
                        }
                        } 
                              steps { 
                        script { 
                               dir("${env.WORKSPACE}/Oracle/Oracle8/UHD") {
                               dockerImageOracle = docker.build("oracle:$BUILD_NUMBER", "--network host .") 
                               env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                               env.CID="\$(docker create $IID)"
                               sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Oracle/Oracle8/UHD"
                               sshagent(credentials: ['sshfilespervices']) {
                               sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/centos8/uhd/*' && \
                               scp -P 237 uhd*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/centos8/uhd/"
                        }
                        }
                        }
                        }
                        }
                stage('RPM_OracleLinux Full') {
                 //Build UHD and Gnuradio
                    when {
                          allOf {
                           expression {params.ENABLE_ORACLE == true}
                           expression {params.CI_BUILD_TYPE == 'FULL'} 
                           expression {params.BRANCH == 'master'}
                        }
                        }
                              steps { 
                        script { 
                               dir("${env.WORKSPACE}/Oracle/Oracle8/GnuRadio") {
                               dockerImageOracle = docker.build("oracle:$BUILD_NUMBER", "--network host .") 
                               env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                               env.CID="\$(docker create $IID)"
                               sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Oracle/Oracle8/GnuRadio"
                               sshagent(credentials: ['sshfilespervices']) {
                               sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/centos8/uhd/* && rm -f /home/filespervices/www/latest/sw/centos8/gnuradio/*' && \
                               scp -P 237 uhd*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/centos8/uhd/ && \
                               scp -P 237 gnuradio*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/centos8/gnuradio/"
                        }
                        }
                        }
                        }
                    }
                    }
                    }


                stage('Arch Testing'){  
                when {
                          allOf {
                           expression {params.CI_BUILD_TYPE == 'FULL'}
                           expression {params.ENABLE_ARCH == true}
                           expression {params.ENABLE_TESTING == true}
                        }
                        }
                    options {
                    timeout(time: 3, unit: "HOURS")
                    } 
                    steps {
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script{
                    dir("${env.WORKSPACE}/Arch/GnuRadio") {
                    env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
                    sh "docker run --net=host -i $IID /bin/bash -c './test-only-Arch.sh'"
                    }
                    }
                    }
                    }
                    }
                    


                stage('Ubuntu Testing'){    
                when {
                          allOf {
                           expression {params.CI_BUILD_TYPE == 'FULL'}
                           expression {params.ENABLE_UBUNTU == true}
                           expression {params.ENABLE_TESTING == true}
                        }
                        }
                    options {
                    timeout(time: 3, unit: "HOURS")
                    } 
                    steps {
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script{
                    dir("${env.WORKSPACE}/ubuntu/20.04/gnuradio") {
                    env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                    sh "docker run --net=host -i $IID /bin/bash -c './test-only.sh'"
                    }
                    }
                    }
                    }
                    }


               stage('Oracle Testing'){    
               when {
                          allOf {
                           expression {params.CI_BUILD_TYPE == 'FULL'}
                           expression {params.ENABLE_ORACLE == true}
                           expression {params.ENABLE_TESTING == true}
                        }
                        }
                    options {
                    timeout(time: 3, unit: "HOURS")
                        } 
                    steps {
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script{
                        dir("${env.WORKSPACE}/Oracle/Oracle8/GnuRadio") {
                            env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                            sh "docker run --net=host -i $IID /bin/bash -c './test-only.sh'"
                    }
                    }
                    }
                    }
                    }
}



post {
   always{
        script{
        if (params.CLEAN == true){
        sh "docker stop \$(docker ps -a -q) && docker system prune -a -f"
        echo 'This build is finished. Cleaning up build environment.'}
        else { echo 'This build is finished. Not running clean.'}
        }
        }
    failure {
 			mail to: 'tech@pervices.com',
 			subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
 			body: "Something is wrong with the build ${env.BUILD_URL}"
 		}
}
}
