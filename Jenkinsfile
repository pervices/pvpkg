pipeline { 

    environment { 

        registry = "than97/pvpkg" 

        registryCredential = '85454c7d-a176-4e4c-94c2-d415e42a4cc3' 

        dockerImage = '' 
    }
//TODO: use citests agents to build and test repo
    agent citests 

    stages { 


        stage('ArchLinux') { 

            steps { 
		//Build Image

                script { 
                        dir("${env.WORKSPACE}/Arch") {
                  		sh "pwd"
                    		dockerImage = docker.build registry + ":$BUILD_NUMBER" 
                  	}
		//Test with pvtests

		//If passed, save UHD package.
                }
            } 

        }
	// Replace with the other distributions
        stage('Deploy our image') { 

            steps { 

                script { 
                   
      
                    docker.withRegistry( '', registryCredential ) { 

                        dockerImage.push() 
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


