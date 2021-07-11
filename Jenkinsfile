pipeline { 

// citests agents used to build and test repo.
    agent {
	label 'waveci'
    }

    stages {


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


               stage('Ubuntu 20.04') { 

                   steps { 
                              // Build image, enter container to transfer build artifacts from Dockerfile image, 
                              // remove image from cache to allow subsequent builds to build from scratch, transfer build artifacts to FTP server.
                      script { 
                             dir("${env.WORKSPACE}/ubuntu/20.04") {
                                 dockerImageUbuntu2004 = docker.build("ubuntu:$BUILD_NUMBER", "--network host .") 
                            //     env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                             //    env.CID="\$(docker create $IID)"
                            //     sh "docker cp ${CID}:/home/artifacts/. $WORKSPACE/ubuntu/20.04 && \
                           //          docker rmi -f ${IID}"
                           //      sshagent(credentials: ['sshfilespervices']) {
                          //      sh "ssh -T -p 237 filespervices@files.pervices.com && \
                           //      scp -P 237 uhdpv*.deb filespervices@files.pervices.com:/home/filespervices/www/latest/sw/uhd/ && \
                           //      scp -P 237 gnuradio*.tar.gz filespervices@files.pervices.com:/home/filespervices/www/latest/sw/gnuradio/"
                       // }
                       }
                     } 
                 }
             }
             
        //       stage('CentOS8 RPM Generation and Testing') { 

          //         steps { 

         //             script { 
              //                dir("${env.WORKSPACE}/CentOS/8testing") {
         //                              dockerImageUbuntu1804 = docker.build("$BUILD_NUMBER", "--network host .") 
          //      }
           //    }
         //  } 
//}
      }

       }


    stage('Testing'){
          
                stage('Ubuntu Testing'){
                     steps {
                      script{
                            dir("${env.WORKSPACE}/ubuntu/20.04") {
                               env.IID = "\$(docker images ubuntu:$BUILD_NUMBER --format \"{{.ID}}\")"
                               env.CID="\$(docker create $IID)"
                           //    sh "docker start $CID && \
                           //       docker exec -it $CID script /dev/null -c "./test-only.sh" &&\
                           //        ls"
}
}
}
}
}
}
}
