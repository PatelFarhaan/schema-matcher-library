pipeline {
    agent any 
    stages {
        stage('Stage 1') {
            steps {
                sh 'pip install pybuilder'
                sh 'virtualenv venv'
                sh 'source venv/bin/activate'
                sh 'pyb install_dependencies'
            }
        }
    }
}
