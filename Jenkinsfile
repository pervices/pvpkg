pipeline { 

// citests agents used to build and test repo.
    agent {
	label 'waveci'
    }

    stages {


        stage('Build UHD and GNU Radio') {
        parallel {

            //    stage('ArchLinux') { 

             //     steps { 
		      //Build Image

              //        script { 
               //              dir("${env.WORKSPACE}/Arch") {
               //     		      dockerImageArch = docker.build("arch:$BUILD_NUMBER", "--network host .") 
              //                         env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
              //                  env.CID="\$(docker create $IID)"
             //                   sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Arch"
              //                   sshagent(credentials: ['sshfilespervices']) {
            //                    sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/archlinux/uhd/* && rm -f /home/filespervices/www/latest/sw/archlinux/gnuradio/*' && \
            //                    scp -P 237 libuhdpv* filespervices@files.pervices.com:/home/filespervices/www/latest/sw/archlinux/uhd/ && \
            //                    scp -P 237 gnuradio* filespervices@files.pervices.com:/home/filespervices/www/latest/sw/archlinux/gnuradio/"
          //       	}
           //             }
		       //Test with pvtests

		      //If passed, save UHD package.
         //             }
         //        } 
         //    }


               stage('Ubuntu 20.04') { 

                   steps { 
                              // Build image, enter container to transfer build artifacts from Dockerfile image, 
                              // remove image from cache to allow subsequent builds to build from scratch, transfer build artifacts to FTP server.
                    script { 
                             dir("${env.WORKSPACE}/ubuntu/20.04") {
                                 dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                                env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                                 env.CID="\$(docker create $IID)"
                                sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/ubuntu/20.04"
                                 sshagent(credentials: ['sshfilespervices']) {
                                sh "ssh -T -p 237 filespervices@files.pervices.com 'rm -f /home/filespervices/www/latest/sw/ubuntu20.04/uhd/* && rm -f /home/filespervices/www/latest/sw/ubuntu20.04/gnuradio/*' && \
                               scp -P 237 uhdpv*.deb filespervices@files.pervices.com:/home/filespervices/www/latest/sw/ubuntu20.04/uhd/ && \
                               scp -P 237 gnuradio*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/ubuntu20.04/gnuradio/"
                        }
                       }
                     } 
                 }
            }
 //             stage('Installation Testing Container') { 
 
  //                  steps { 
   //                    script { 
   //                          dir("${env.WORKSPACE}/installationtestingcontainer") {
   //                               dockerImageTestContainer = docker.build("test:$BUILD_NUMBER", "--network host .") 
    //                    }
    //                 } 
  //                }
    //          }
               stage('RPM_OracleLinux') { 
 
                    steps { 
 
                       script { 
                               dir("${env.WORKSPACE}/Oracle/Oracle8") {
                                        dockerImageOracle = docker.build("oracle:$BUILD_NUMBER", "--network host .") 
                               env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                                  env.CID="\$(docker create $IID)"
                                 sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/Oracle/Oracle8"
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
                     options {
                timeout(time: 3, unit: "HOURS")
                           } 
                     steps {
                     catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                      script{
                            dir("${env.WORKSPACE}/arch") {
                               env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
                               sh "docker run --net=host -i $IID /bin/bash -c './test-only-Arch.sh'"
}
}
}
}
}
    stage('Remove Arch Image'){  
                    steps {
                    script{
                     dir("${env.WORKSPACE}/arch") {
                     env.IID = "\$(docker images arch:$BUILD_NUMBER --format \"{{.ID}}\")"
                    sh "docker stop \$(docker ps -a -q) && \
                        docker rm \$(docker ps -a -q) && \
                        docker rmi -f ${IID}"
}
} 
}
}


         stage('Ubuntu Testing'){    
                        options {
                timeout(time: 3, unit: "HOURS")
                           } 
                     steps {
                      catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                      script{
                            dir("${env.WORKSPACE}/ubuntu/20.04") {
                               env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                               sh "docker run --net=host -i $IID /bin/bash -c './test-only.sh'"
}
}
}
}
}
    stage('Remove Ubuntu Image'){  
                    steps {
                    script{
                     dir("${env.WORKSPACE}/ubuntu/20.04") {
                     env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                    sh "docker stop \$(docker ps -a -q) && \
                        docker rm \$(docker ps -a -q) && \
                        docker rmi -f ${IID}"
}
} 
}
}


          stage('Oracle Testing'){    
                      options {
                 timeout(time: 3, unit: "HOURS")
                            } 
                      steps {
                       catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                       script{
                             dir("${env.WORKSPACE}/Oracle/Oracle8") {
                                env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                                sh "docker run --net=host -i $IID /bin/bash -c './test-only.sh'"
 }
 }
 }
 }
 }
     stage('Remove Oracle Image'){  
                     steps {
                     script{
                      dir("${env.WORKSPACE}/Oracle/Oracle8") {
                      env.IID = "\$(docker images oracle:$BUILD_NUMBER --format \"{{.ID}}\")"
                     sh "docker stop \$(docker ps -a -q) && \
                         docker rm \$(docker ps -a -q) && \
                         docker rmi -f ${IID}"
 }
 }
 }
 }
 stage('Clean Up'){  
                    steps {
                    script{
                     dir("${env.WORKSPACE}") {
                     sh "docker system prune -a -f"
}
}
}
}
}
//post {
//		always {
// 			echo 'The UHD-only test is finished, cleaning up workspace...'
// 			//might need to use deleteDir() to clean up workspace
// 		}
// 		failure {
// 			mail to: 'tech@pervices.com',
// 			subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
// 			body: "Something is wrong with the build ${env.BUILD_URL}"
// 		}
// 	}
// }
}
