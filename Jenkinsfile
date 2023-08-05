podTemplate(yaml: '''
              apiVersion: v1
              kind: Pod
              spec:
                serviceAccountName: jenkins-agent
                containers:
                - name: docker
                  image: docker:latest
                  command:
                  - cat
                  tty: true
                  volumeMounts:
                  - name: dockersock
                    mountPath: /var/run/docker.sock
                - name: kubectl
                  image: portainer/kubectl-shell
                  command:
                  - cat
                  tty: true
                  volumeMounts:
                  - name: dockersock
                    mountPath: /var/run/docker.sock
                volumes:
                - name: dockersock
                  hostPath:
                    path: /var/run/docker.sock
''') {
  node(POD_LABEL) {
    stage('prep') {
      git url: 'https://github.com/dabealu/example-flask-app.git', branch: 'main'
      script {
        env.imageTag = getImageTag()
        sh "echo ${env.imageTag}"
      }
    }

    stage('build docker image') {
      container('docker') {
        script {
          buildImage(env.imageTag)
        }
      }
    }

    stage('run tests') {
      container('docker') {
        script {
          runTests()
        }
      }
    }

    stage('deploy') {
      // when {
      //   branch 'main'
      //   changeset 'app/**'
      // }
      container('kubectl') {
        script {
          deployManifests(env.imageTag)
        }
      }
    }

  }
}

def getImageTag() {
  return sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
}

def buildImage(def tag) {
  sh "docker build -t localhost:30003/userapi:${tag} app/"
  sh "docker tag localhost:30003/userapi:${tag} localhost:30003/userapi:latest"
  sh "docker push localhost:30003/userapi:${tag}"
  sh "docker push localhost:30003/userapi:latest"
}

def runTests() {
  // TODO: replace sleep with proper readiness check
  sh '''
    CLEANUP='docker compose down --volumes'
    docker compose up -d || $CLEANUP
    sleep 15
    docker compose exec app python3 userapi_test.py
    EX=$?
    $CLEANUP
    exit $EX
  '''
}

def deployManifests(def tag) {
  sh "sed -i 's/NEW_USERAPI_TAG/${tag}/' k8s/kustomization.yaml"
  sh "kubectl kustomize k8s | kubectl apply -f -"
}
