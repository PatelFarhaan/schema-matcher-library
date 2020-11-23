pipeline {
    agent { docker { image 'python:3.8.6' } }
    stages {
        stage('build') {
            steps {
                sh 'pip install pybuilder'
                sh 'pyb install_dependencies'
            }
        }
    }
}
