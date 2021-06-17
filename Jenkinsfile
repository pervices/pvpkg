pipeline { 

// citests agents used to build and test repo.
    agent {
	label 'crossci||waveci'
    }

    stages { 

        // Build stages for each distribution are set to run in parallel. Need to add build artifacts and run tests 
        // for each parallel build. 

	stage('Test Credentials'){
steps {
    withCredentials([sshUserPrivateKey(credentialsId: sshfilespervices, keyFileVariable: 'KEY')]) {
        sh "ssh -i ${KEY} -p 237 -i /home/altrus/.ssh/id_rsa_pv_files filespervices@files.pervices.com"
    }
}
}
        stage('Build UHD and GNU Radio') {
        parallel {

                stage('ArchLinux') { 

                  steps { 
		      //Build Image

                      script { 
                              dir("${env.WORKSPACE}/Arch") {
                    		      dockerImageArch = docker.build(registry + ":$BUILD_NUMBER", "--network host .") 
                  	}
		       //Test with pvtests

		      //If passed, save UHD package.
                      }
                  } 

              }


               stage('CentOS 8') { 

                  steps { 

                       script { 
                             dir("${env.WORKSPACE}/CentOS/8notsource") {
                                     dockerImageCentos8 = docker.build(registry + ":$BUILD_NUMBER", "--network host .") 
                       }
                     }
                    } 

             }



               stage('Ubuntu 20.04 PV Debian') { 

                   steps { 

                      script { 
                             dir("${env.WORKSPACE}/ubuntu/20.04/20.04testing") {
                                     dockerImageUbuntu2004 = docker.build(registry + ":$BUILD_NUMBER", "--network host .") 
                        }
                       }
                     } 

             }
             
               stage('CentOS8 RPM Generation and Testing') { 

                   steps { 

                      script { 
                              dir("${env.WORKSPACE}/CentOS/8testing") {
                                       dockerImageUbuntu1804 = docker.build(registry + ":$BUILD_NUMBER", "--network host .") 
                }
               }
           } 

      }

       }
      }

	// Replace with the other distributions
        stage('Deploy our image') { 

            steps { 

                script { 
                   
    //   ssh -p 237 -i /home/altrus/.ssh/id_rsa_pv_files filespervices@files.pervices.com 
                    }

                } 

            }

        } 
        stage('Cleaning up') { 

            steps { 

                sh "docker rmi $registry:$BUILD_NUMBER" 

            }
        } 
    }
}


