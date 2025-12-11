pipeline {
    agent any
    
    environment {
        TIME_ZONE = 'Asia/Seoul'
        
        // GitHub 계정정보
        GIT_TARGET_BRANCH = 'main'
        GIT_REPOSITORY_URL = 'https://github.com/csejh1/fast.git'
        GIT_CREDENTIALS_ID = 'git_crd' // 오타 수정 (CREDENTIONALS -> CREDENTIALS)
        GIT_EMAIL = 'jerrysong4912@gmail.com'
        GIT_NAME = 'csejh1'
        
        // 중요: 배포용 레포지토리도 HTTPS 주소를 권장합니다 (Credential 재사용을 위해)
        // SSH(git@...)를 쓰려면 Jenkins에 SSH 키가 등록되어 있어야 합니다.
        // 여기서는 편의상 HTTPS로 통일하여 작성했습니다.
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

        // 2. 소스코드 클론 (애플리케이션 코드)
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
                    // 중요: 변수 치환을 위해 큰따옴표 3개(""") 사용
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

        // 5. K8s Manifest 업데이트 (Git Push)
        stage('5.EKS manifest file update') {
            steps {
                // Manifest 파일이 있는 레포지토리를 별도로 클론
                // 만약 같은 레포라면 이 과정 생략 가능하지만, 분리된 구조라 가정하고 진행
                git branch: 'main',
                    credentialsId: "${GIT_CREDENTIALS_ID}",
                    url: "${GIT_REPOSITORY_DEP_URL}"
                
                // Git Push를 위한 인증 정보 주입
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    script {
                        sh """
                            git config --global user.email "${GIT_EMAIL}"
                            git config --global user.name "${GIT_NAME}"
                            
                            # sed 명령어로 태그 교체 (구분자를 @로 사용)
                            sed -i 's@${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:.*@${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER}@g' test-dep.yml || echo "test-dep.yml not found, skipping sed"
                            
                            git add .
                            
                            # 변경사항이 있을 때만 커밋 (에러 방지)
                            git diff-index --quiet HEAD || git commit -m "fixed tag ${BUILD_NUMBER}"
                            
                            # 인증 정보가 포함된 URL로 Push (보안상 안전)
                            git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/csejh1/fast.git main
                        """
                    }
                }
            }
        }
    } // stages end

    // post 블록을 전역으로 이동 (어떤 단계에서 실패하든 실행됨)
    post {
        failure {
            script {
                sh """
                    # 이미지가 없을 수도 있으니 에러 무시를 위해 || true 추가
                    docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER} || true
                    docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest || true
                    echo "Docker image build/push failed. Cleaned up."
                """
            }
        }
        success {
            script {
                sh """
                    docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:${BUILD_NUMBER} || true
                    docker rm -f ${AWS_ECR_URI}/${AWS_ECR_IMAGE_NAME}:latest || true
                    echo "Docker image push success. Cleaned up."
                """
            }
        }
    }
}
