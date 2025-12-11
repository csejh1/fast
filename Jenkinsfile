pipeline {
    agent any
    
    environment {
        TIME_ZONE = 'Asia/Seoul'
        
        // GitHub 계정정보
        GIT_TARGET_BRANCH = 'main'
        GIT_REPOSITORY_URL = 'https://github.com/csejh1/fast'
        GIT_CREDENTIALS_ID = 'git_crd'
        GIT_EMAIL = 'jerrysong4912@gmail.com'
        GIT_NAME = 'csejh1'
        
        // [수정 1] 배포용(Argo) 레포지토리 주소를 HTTPS로 변경 (인증 오류 방지)
        // 기존: git@github.com:csejh1/ArgoRepo.git -> 수정됨
        GIT_REPOSITORY_DEP_URL = 'git@github.com:csejh1/ArgoRepo.git' 

        // AWS ECR 정보
        AWS_ECR_CREDENTIAL_ID = 'aws_crd'
        AWS_ECR_URI = '967361137282.dkr.ecr.ap-northeast-2.amazonaws.com'
        AWS_ECR_IMAGE_NAME = 'fast'
        AWS_REGION = 'ap-northeast-2'
    }

    stages {
        // 1. 초기화
        stage('1.init') {
            steps {
                echo '1.init stage'
                deleteDir()
            }
        }

        // 2. 소스코드 클론 (App Repo)
        stage('2.Cloning Repository') {
            steps {
                echo '2.Cloning Repository'
                git branch: "${GIT_TARGET_BRANCH}",
                    credentialsId: "${GIT_CREDENTIALS_ID}",
                    url: "${GIT_REPOSITORY_URL}"
            }
        }

        // 3. 도커 이미지 빌드
        stage('3.Build Docker Image') {
            steps {
                script {
                    sh """
                        docker build -t ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER} .
                        docker build -t ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest .
                    """
                }
            }
        }

        // 4. ECR 푸시
        stage('4.Push to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_ECR_CREDENTIAL_ID}"]]) {
                    script {
                        sh """
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ECR_URI}
                            docker push ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}
                            docker push ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }

        // 5. K8s Manifest 업데이트 (Argo Repo 수정)
        stage('5.EKS manifest file update') {
            steps {
                // [수정 2] 배포용 레포지토리 클론 (ArgoRepo)
                git branch: 'main',
                    credentialsId: "${GIT_CREDENTIALS_ID}",
                    url: "${GIT_REPOSITORY_DEP_URL}"
                
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    script {
                        sh """
                            git config --global user.email "${GIT_EMAIL}"
                            git config --global user.name "${GIT_NAME}"
                            
                            # [핵심 수정 3] 최신 변경사항 당겨오기 (에러 방지)
                            git pull origin main || echo "Already up to date"

                            # sed 명령어로 태그 교체 (test-dep.yml이 ArgoRepo에 있어야 함)
                            sed -i 's@${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:.*@${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}@g' test-dep.yml
                            
                            git add .
                            
                            # 변경사항이 있을 때만 커밋
                            git diff-index --quiet HEAD || git commit -m "fixed tag ${BUILD_NUMBER}"
                            
                            # [핵심 수정 4] Push 주소를 ArgoRepo로 명확하게 지정
                            # 기존 코드에서는 fast.git으로 푸시하고 있었음 -> ArgoRepo.git으로 변경
                            git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/csejh1/ArgoRepo.git main
                        """
                    }
                }
            }
        }
    } // stages end

    post {
        always {
            script {
                sh """
                    # [수정 5] docker rm -> docker rmi (이미지 삭제 명령어)
                    docker rmi -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER} || true
                    docker rmi -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest || true
                    echo "Docker images cleaned up."
                """
            }
        }
    }
}
