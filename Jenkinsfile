// CI only: deployment is handled by Coolify.
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Lint') {
            agent {
                docker {
                    image 'python:3.12-slim'
                    reuseNode true
                }
            }
            steps {
                // Same fatal checks as upstream CI: syntax errors and undefined names.
                sh '''
                    python -m venv .venv
                    .venv/bin/pip install --quiet flake8
                    .venv/bin/flake8 --count --select=E9,F63,F7,F82 --ignore F824 --show-source --statistics --exclude .venv .
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t archipelago:${BUILD_NUMBER} .'
            }
        }
    }

    post {
        always {
            sh 'docker image rm archipelago:${BUILD_NUMBER} || true'
        }
    }
}
