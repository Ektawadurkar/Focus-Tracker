
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/Ektawadurkar/Focus-Tracker.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Focus Tracker project checked out successfully!'
            }
        }
    }
}
