pipeline {
    agent any
    
  environment {
        TIME_ZONE = 'Asia/Seoul'
        
        // GitHub 계정정보. 본인껄로 넣으세요!!
        GIT_TARGET_BRANCH = 'main'
        GIT_REPOSITORY_URL = 'https://github.com/oolralra/fast'
        GIT_CREDENTIONALS_ID = 'git_cre'


        // AWS ECR 정보. 본인껄로 넣으세요!!
        AWS_ECR_CREDENTIAL_ID = 'aws_cre'
        AWS_ECR_URI = '865577889736.dkr.ecr.ap-northeast-2.amazonaws.com' // 레지스트리주소
        AWS_ECR_IMAGE_NAME = 'fast' // 레포지토리이름.
        AWS_REGION = 'ap-northeast-2'
        
    }

    stages {
        // 첫번째 스테이지 : 초기화.

        stage('1.init') {
            steps {
                echo '1.init stage'
                deleteDir()
            }
        }

        // 두번째 스테이지 : 소스코드 클론

        stage('2.Cloning Repository') {
            steps {
                echo '2.Cloning Repository'
                git branch: "${GIT_TARGET_BRANCH}",
                    credentialsId: "${GIT_CREDENTIONALS_ID}",
                    url: "${GIT_REPOSITORY_URL}"

                // 깃플러그인 설치하면 마치 함수쓰듯 사용가능.
            }
        
        }

        stage('3.Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker build -t ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER} .
                        docker build -t ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest .
                    '''
                }
                // 명령어가 많아질것같아서 스크립트 블록을 추가.
                // BUILD_NUMBER = 젠킨스가 제공해주는 변수.
            }
        }


        stage('4.Push to ECR') {
            steps {
              // aws credential 플러그인을 설치해서 사용할 수 있는 함수. aws configure와 같은 기능.
              withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_ECR_CREDENTIAL_ID}"]]) {
                    script {
                        sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ECR_URI}
                        docker push ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest
                        '''
                    }
                }
            }
            post {
                failure {
                    script {
                        sh '''
                        docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}
                        docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest
                        echo docker image push fail
                        '''
                    }
                }
                success {
                    script {
                   
                        sh '''
                        docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}
                        docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest
                        echo docker image push success
                        '''
                    }

                }                
            }
        }






    }
}
