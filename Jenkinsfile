pipeline {
  agent any

  environment {
    IMAGE_NAME = "inventory-api"
    API_CONTAINER = "inventory-api-jenkins"
    MONGO_CONTAINER = "inventory-mongo-jenkins"
    NETWORK = "inventory-net"
    // No host port binding (avoids conflicts on Windows agents).
    BASE_URL = "http://inventory-api-jenkins:8000"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker image') {
      steps {
        bat 'docker build -t %IMAGE_NAME%:latest .'
      }
    }

    stage('Start MongoDB') {
      steps {
        bat '''
          docker network create %NETWORK% || exit /b 0
        '''
        bat '''
          docker rm -f %MONGO_CONTAINER% || exit /b 0
        '''
        bat '''
          docker run -d --name %MONGO_CONTAINER% --network %NETWORK% ^
            -e MONGO_INITDB_ROOT_USERNAME=admin ^
            -e MONGO_INITDB_ROOT_PASSWORD=adminpassword ^
            mongo:7
        '''
      }
    }

    stage('Run API container (background)') {
      steps {
        bat '''
          docker rm -f %API_CONTAINER% || exit /b 0
        '''
        bat '''
          docker run -d --name %API_CONTAINER% --network %NETWORK% -p 8000:8000 ^
            -e MONGO_URL=mongodb://admin:adminpassword@%MONGO_CONTAINER%:27017/?authSource=admin ^
            -e MONGO_DB=inventory ^
            -e MONGO_COLLECTION=products ^
            %IMAGE_NAME%:latest
        '''
      }
    }

    stage('Wait for API') {
      steps {
        powershell '''
          $ErrorActionPreference = "Stop"
          # Probe from inside the Docker network to avoid host networking issues on Windows.
          docker run --rm --network $env:NETWORK curlimages/curl:8.6.0 `
            -sSf "$env:BASE_URL/getAll" | Out-Null
          Write-Host "API is up (reachable on Docker network)"
        '''
      }
    }

    stage('Run Newman tests') {
      steps {
        powershell '''
          $ErrorActionPreference = "Stop"
          $testsDir = Join-Path $env:WORKSPACE "tests"
          docker run --rm --network $env:NETWORK `
            -v "${testsDir}:/etc/newman" `
            postman/newman:alpine `
            run /etc/newman/postman_collection.json `
            --env-var baseUrl=$env:BASE_URL
        '''
      }
    }

    stage('Generate README.txt') {
      steps {
        powershell '''
          $ErrorActionPreference = "Stop"
          docker run --rm --network host `
            -v "$env:WORKSPACE:/work" -w /work `
            python:3.11-slim `
            python generate_readme.py
          if (-not (Test-Path (Join-Path $env:WORKSPACE "README.txt"))) { throw "README.txt not generated" }
        '''
      }
    }

    stage('Create zip artifact') {
      steps {
        powershell '''
          $ErrorActionPreference = "Stop"
          $ts = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
          $zip = Join-Path $env:WORKSPACE ("complete-{0}.zip" -f $ts)
          Get-ChildItem $env:WORKSPACE -Filter "complete-*.zip" -ErrorAction SilentlyContinue | Remove-Item -Force

          $items = @(
            "app","scripts","tests","monitoring",
            "Dockerfile","Jenkinsfile","requirements.txt",
            "generate_readme.py","products.csv","docker-compose.yml",
            "README.txt",".env.example",".dockerignore",".gitignore"
          )
          $paths = $items | ForEach-Object { Join-Path $env:WORKSPACE $_ } | Where-Object { Test-Path $_ }

          Compress-Archive -Path $paths -DestinationPath $zip -Force
          Write-Host ("Created {0}" -f $zip)
        '''
      }
    }
  }

  post {
    always {
      bat '''
        docker rm -f %API_CONTAINER% || exit /b 0
      '''
      bat '''
        docker rm -f %MONGO_CONTAINER% || exit /b 0
      '''
      bat '''
        docker network rm %NETWORK% || exit /b 0
      '''
    }
  }
}

