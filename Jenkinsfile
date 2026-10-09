

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Repository already checked out by Jenkins.'
                bat 'git branch'
            }
        }

        stage('Build') {
            steps {
                echo 'Focus Tracker project checked out successfully!'
            }
        }
    }
}

