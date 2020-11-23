pipeline {
    agent { docker { image 'python:3.8.6' } }
    stages {
        stage('build') {
            steps {
                sh 'sudo pip install pybuilder'
                sh 'sudo pyb install_dependencies'
            }
        }
    }
}
