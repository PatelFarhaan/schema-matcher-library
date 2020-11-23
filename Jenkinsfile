pipeline {
    agent { docker { image 'python:3.8.6' } }
    stages {
        stage('build') {
            steps {
                sh 'pyb install_dependencie'
            }
        }
    }
}
