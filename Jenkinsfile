pipeline {
    agent any 
    stages {
        stage('Stage 1') {
            steps {
                sh 'pip install pybuilder'
                sh 'pyb install_dependencies'
            }
        }
    }
}
