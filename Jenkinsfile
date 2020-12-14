pipeline { 

    environment { 

        registry = "than97/pvpkg" 

        registryCredential = '85454c7d-a176-4e4c-94c2-d415e42a4cc3' 

        dockerImageArch = '' 
        dockerImageCentos8 = '' 
        dockerImageUbuntu1804 = '' 
        dockerImageUbuntu2004 = '' 
    }
// citests agents used to build and test repo.
    agent {
	label 'citests'
    }

    stages { 

        // Build stages for each distribution are set to run in parallel. Need to add build artifacts and run tests 
        // for each parallel build. 
 
        stage('Build UHD and GNU Radio') {
        parallel {

              stage('ArchLinux') { 

                  steps { 
		      //Build Image

                       script { 
                              dir("${env.WORKSPACE}/Arch") {
                    		      dockerImageArch = docker.build registry + ":$BUILD_NUMBER" 
                  	}
		       //Test with pvtests

		      //If passed, save UHD package.
                      }
                  } 

              }

               stage('CentOS 8') { 

                   steps { 

                       script { 
                              dir("${env.WORKSPACE}/CentOS/8") {
                                      dockerImageCentos8 = docker.build registry + ":$BUILD_NUMBER" 
                       }
                      }
                     } 

              }



                stage('Ubuntu 18.04') { 

                   steps { 

                      script { 
                              dir("${env.WORKSPACE}/ubuntu/18.04") {
                                      dockerImageUbuntu1804 = docker.build registry + ":$BUILD_NUMBER" 
                        }
                       }
                      } 

             }
             
                stage('Ubuntu 20.04') { 

                    steps { 

                       script { 
                              dir("${env.WORKSPACE}/ubuntu/20.04") {
                                       dockerImageUbuntu2004 = docker.build registry + ":$BUILD_NUMBER" 
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
                   
      
                    docker.withRegistry( '', registryCredential ) { 

                        dockerImageArch.push() 
                        dockerImageCentos8.push() 
                        dockerImageUbuntu1804.push() 
                        dockerImageUbuntu2004.push() 
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


