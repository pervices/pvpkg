pipeline { 

// citests agents used to build and test repo.
    agent {
	label 'crossci||waveci'
    }

    stages {

        // Build stages for each distribution are set to run in parallel. Need to add build artifacts and run tests 
        // for each parallel build. 

	//stage('Test Credentials'){
//steps {
   //  sshagent(credentials: ['sshfilespervices']) {
  //  sh "ssh -T -p 237 filespervices@files.pervices.com && \
   // echo 'ssh -T -p 237 filespervices@files.pervices.com'"
   // }
//}
//}
        stage('Build UHD and GNU Radio') {
        parallel {

                stage('ArchLinux') { 

                  steps { 
		      //Build Image

                      script { 
                              dir("${env.WORKSPACE}/Arch") {
                    		      dockerImageArch = docker.build("$BUILD_NUMBER", "--network host .") 
                  	}
		       //Test with pvtests

		      //If passed, save UHD package.
                      }
                  } 

              }


              // stage('TestingFTP') { 

                  //steps { 

                     //  script { 
                           //  dir("${env.WORKSPACE}/ftptesting") {
                               //   dockerImageftptesting = docker.build("ftp:$BUILD_NUMBER", "--network host .")
                              //    env.IID = "\$(docker images ftp:$BUILD_NUMBER --format \"{{.ID}}\")"
                              //   env.CID="\$(docker create $IID)"
                              //  sh "docker cp ${CID}:/test.txt $WORKSPACE/ftptesting"
                             //   sh "echo ${IID} && echo ${CID}"
                             //    sshagent(credentials: ['sshfilespervices']) {
                            //     sh "ssh -T -p 237 filespervices@files.pervices.com && \
                              //  scp -P 237 test.txt filespervices@files.pervices.com:/home/filespervices/www/latest/crimson/"
                    //   }
                     
              //   }
              //  }
           //  }
         //    }


               stage('Ubuntu 20.04') { 

                   steps { 

                      script { 
                             dir("${env.WORKSPACE}/ubuntu/20.04/20.04testing") {
                                 dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                             //    env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                             //    env.CID="\$(docker create $IID)"
                              //   sh "docker cp ${CID}: $WORKSPACE/ftptesting && \
                           //         docker cp ${CID}: $WORKSPACE/ftptesting"
                              //  sh "echo ${IID} && echo ${CID}"
                         //        sshagent(credentials: ['sshfilespervices']) {
                        //         sh "ssh -T -p 237 filespervices@files.pervices.com && \
                        //         scp -P 237 test.txt filespervices@files.pervices.com:/home/filespervices/www/latest/ && \
                       //          scp -P 237 test.txt filespervices@files.pervices.com:/home/filespervices/www/latest/"
                      //  }
                       }
                     } 
                 }
             }
             
               stage('CentOS8 RPM Generation and Testing') { 

                   steps { 

                      script { 
                              dir("${env.WORKSPACE}/CentOS/8testing") {
                                       dockerImageUbuntu1804 = docker.build("$BUILD_NUMBER", "--network host .") 
                }
               }
           } 
}
      }

       }
      }
}



