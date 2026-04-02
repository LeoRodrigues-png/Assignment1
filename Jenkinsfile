pipeline {
  agent any

  environment {
    IMAGE_NAME = "inventory-api"
    API_CONTAINER = "inventory-api-jenkins"
    MONGO_CONTAINER = "inventory-mongo-jenkins"
    NETWORK = "inventory-net"
    BASE_URL = "http://localhost:8000"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME}:latest .'
      }
    }

    stage('Start MongoDB') {
      steps {
        sh '''
          docker network create ${NETWORK} || true
          docker rm -f ${MONGO_CONTAINER} || true
          docker run -d --name ${MONGO_CONTAINER} --network ${NETWORK} \
            -e MONGO_INITDB_ROOT_USERNAME=admin \
            -e MONGO_INITDB_ROOT_PASSWORD=adminpassword \
            mongo:7
        '''
      }
    }

    stage('Run API container (background)') {
      steps {
        sh '''
          docker rm -f ${API_CONTAINER} || true
          docker run -d --name ${API_CONTAINER} --network ${NETWORK} -p 8000:8000 \
            -e MONGO_URL=mongodb://admin:adminpassword@${MONGO_CONTAINER}:27017/?authSource=admin \
            -e MONGO_DB=inventory \
            -e MONGO_COLLECTION=products \
            ${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Wait for API') {
      steps {
        sh '''
          for i in $(seq 1 30); do
            if curl -sf ${BASE_URL}/getAll >/dev/null; then
              echo "API is up"
              exit 0
            fi
            sleep 2
          done
          echo "API did not become ready"
          docker logs ${API_CONTAINER} || true
          exit 1
        '''
      }
    }

    stage('Run Newman tests') {
      steps {
        sh '''
          docker run --rm --network host \
            -v "$PWD/tests:/etc/newman" \
            postman/newman:alpine \
            run /etc/newman/postman_collection.json \
            --env-var baseUrl=${BASE_URL}
        '''
      }
    }

    stage('Generate README.txt') {
      steps {
        sh 'python3 generate_readme.py'
        sh 'test -f README.txt'
      }
    }

    stage('Create zip artifact') {
      steps {
        sh '''
          TS=$(date +"%Y-%m-%d-%H-%M-%S")
          ZIP="complete-${TS}.zip"
          rm -f complete-*.zip || true
          zip -r "${ZIP}" app scripts tests monitoring Dockerfile Jenkinsfile requirements.txt generate_readme.py products.csv docker-compose.yml README.txt .env.example .dockerignore || true
          echo "Created ${ZIP}"
        '''
      }
    }
  }

  post {
    always {
      sh '''
        docker rm -f ${API_CONTAINER} || true
        docker rm -f ${MONGO_CONTAINER} || true
        docker network rm ${NETWORK} || true
      '''
    }
  }
}

