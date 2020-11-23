pipeline {
    agent any 
    stages {
        stage('Stage 1') {
            steps {
                sh 'python3.8 -m virtualenv env
                sh 'source env/bin/activate'
                sh 'pip3.8 install pybuilder'
                sh 'pyb install_dependencies'
            }
        }
    }
}
