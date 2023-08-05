# local environment
while following steps to reproduce the environment should be identical on every OS,
it's been tested only on a Linux machine, and it might work slightly different on MacOS or Windows.

## create minikube vm
```sh
# get minikube binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# start vm
minikube start --insecure-registry "10.0.0.0/24"

# get kubectl
minikube kubectl
# i've also copied binary to $PATH for convenience
sudo cp ~/.minikube/cache/linux/amd64/v1.27.3/kubectl /usr/local/bin

# setup image `registry`
# this setup tested on linux, registry may require additional steps on Mac/Win: https://minikube.sigs.k8s.io/docs/handbook/registry/#docker-on-macos
# registry dns name inside cluster: `registry.kube-system.svc.cluster.local:80`
minikube addons enable registry
```

## mysql
deploy mysql pod:
```sh
kubectl apply -f k8s/mysql.yaml
```

## jenkins
```sh
# deploy
kubectl apply -f k8s/jenkins.yaml

# get password for `admin` user
kubectl exec -ti -n jenkins $(kubectl get po -n jenkins --no-headers | awk '{print $1}') -- cat /var/jenkins_home/secrets/initialAdminPassword
```
- in jenkins web ui select "install suggested plugins"
- also install plugins `Kubernetes` and `docker-build-step` plugins (go to Manage Jenkins -> Plugins -> Available)
- configure clouds http://MINIKUBE_VM_IP:30001/configureClouds/ - add `Kubernetes`,
  open cloud details, leave all fields default, press `Test Connection` - it should return `Connected to Kubernetes v1.27.3`
- set jenkins URL to http://jenkins/:
  Manage Jenkins -> System -> Jenkins URL, http://MINIKUBE_VM_IP:30001/manage/configure
  URL used by k8s agents to connect back to Jenkins main
- create job:
  - on home page click `New item`
  - select `Pipeline`, and enter job name, like `userapi-pipeline`
  - check `Poll SCM`, and enter schedule `*/2 * * * *`
  - in pipeline definition select `Pipeline script from SCM`, and enter following parameters:
    - SCM: `Git`
    - Repository URL: https://github.com/dabealu/example-flask-app
    - Branch Specifier: `*/main`
    - leave other fields at their default values, and save job
- after app is deployed, run following before doing other api requests (see `accessing endpoints`):
```sh
  curl -H 'Content-Type: application/json' -X GET $MINIKUBE_VM_IP:30005/create_table
```
  this will run "migrations" and create `users` table in DB

## accessing endpoints
all services configured with static node ports which exposed by minikube vm.
endpoints can be accessed by MINIKUBE_VM_IP:PORT, minikube tunnel must be established.

start minikube tunnel, and grab VM IP:
```sh
MINIKUBE_VM_IP=$( minikube ip )
echo $MINIKUBE_VM_IP

# run in a separate terminal or in background
minikube tunnel
```

ports:
```yaml
userapi: 30005
jenkins: 30001
registry: 30003
```

# API
```sh
# create db table:
curl -H 'Content-Type: application/json' -X GET $MINIKUBE_VM_IP:30005/create_table
# create:
curl -H 'Content-Type: application/json' -X POST $MINIKUBE_VM_IP:30005/create -d '{"name":"first user","email":"first@mail.io","pwd":"1"}'
curl -H 'Content-Type: application/json' -X POST $MINIKUBE_VM_IP:30005/create -d '{"name":"second user","email":"second@mail.io","pwd":"2"}'
# get all:
curl -H 'Content-Type: application/json' -X GET $MINIKUBE_VM_IP:30005/users
# get by id:
curl -H 'Content-Type: application/json' -X GET $MINIKUBE_VM_IP:30005/user/1
# update:
curl -H 'Content-Type: application/json' -X POST $MINIKUBE_VM_IP:30005/update -d '{"user_id":1,"name":"third user","email":"third@mail.io","pwd":"3"}'
# delete:
curl -H 'Content-Type: application/json' -X GET $MINIKUBE_VM_IP:30005/delete/1
```

# CICD
> tools/vendors selection

it depends on a multiple factors, it's probably a good idea to draw a matrix with requirements and various tools/products, then select those which are having a best fit. then do some tests and see how is it working (or not) for a specific case.

for demo purposes i've selected jenkins because i tried to keep this environment self-contained and run all required components inside k8s cluster.
apart from it, i'm familiar with technology and knew that it have all the features i need to get job done.
alternatively i was thinking about github actions + fluxcd:
- build image via actions, store it in ghcr or any other public container registry
- then flux (gitops tool) will pick image from registry and update deployment for userapi

in a real world scenario there are usually multiple factors which can make certain solution better than other, for example:
- feature set provided by the tool
- time available to adopt certain tool - commercial products are usually easier/faster to start with
- budget
- operational costs
- expertise on the team
- maturity of the tool - especially important for open source solutions without any paid support
- maintenance costs - e.g. jenkins with all possible plugins installed may require a lot of efforts to maintain
- integrations with other tools used at the company
- ability to scale to the required level
- reliability - not fun when paid actions are down
- user experience provided by the solution
- level of flexibility and extensibility
- etc etc...
only prioritizing and evaluating all of the factors (which are important for particular case) and comparing some number of different solutions may give an idea what is an optimal choice.
for example if cicd system required to be set up today and shouldn't require any efforts to maintain it's probably going to be some commercial managed solution like actions, travis, circle, etc.

> continuous delivery plan

before having CD, first i'll think about having a proper underlying platform:
- managed fault-tolerant kubernetes cluster, and infra components like loadbalancers-ingress controllers, container registry (for example ECR), etc
- reliable database - managed solution like AWS RDS, or self hosted DB with configured replication, automatic failovers and backups
- properly configured CICD system itself

then configure pipeline, which includes following basic steps:
- continuous integration - run tests, linters, security checks etc; run automatically on commit
- continuous deployment - build image, generate k8s manifests, deploy manifests;
  this step may include deployment health-checks, canary stage, and potentially auto rollback failed deploys
- depends on the requirements auto deployments may be configured for staging and prod environments
- optionally there are might be disposable feature-branch allowing developers to test their PRs

# improvements and notes
there is a HUGE room for improvement, but time limit allocated for this task was quite tight.

i've tried to make this environment self-contained - there's no dependencies like cloud, database, external CI/CD system, or container registry,
all required components are open source free solutions and residing within kubernetes "cluster". to clean everything up - just stop and delete minikube vm.

one of the negative consequences of a limited time and selected tools, is that the whole process of setting up this env is quite manual and lacks of automation.

i tried to keep a list, on things which can be done better:
- hardcoded sql user `root`, changed to env var
- missing tests, added some in `userapi_test.py`
- missing migrations, doing manual migration steps which in a real world scenario should be automated
- flask version was old, upgraded (1.0.3 -> 2.3.2)
- for mysql deployment single pod is used, but it should be something resilient (AWS RDS, or replicaed db with persistent storage etc)
- env variables named inconsistently, renamed
- config listening addr:port via env variables
- use persistent agents/prebuilt images with dependencies (requirements.txt)/staged builds to cache image layers
- nodeports used instead of proper ingress and domain/url based routing
- jenkins, registry, and database are deployed in a minimal possible configuration, which is absolutely unreliable and intended only to serve demo purposes
- jenkins job is configured to poll scm periodically instead of receiving webhooks from github
- jenkins jobs is configured manually instead of using github org and automatically detect repositories and create pipelines
- jenkins pipeline is configured to run only for main branch, in a real world it would be more complex, for example:
  - pipeline may run tests and other integration steps (like linters, security scans, etc), for non-main branches
  - for staging or feature branches it may deploy app to staging/feature testing environments after ci steps
  - and for main branch it deploys to production (which could be more complex too, for example including canaries)
- all k8s manifests are minimal and not templated, only a bit of kustomize; use proper templates, may be create helm charts
- secrets passed as plain env variables
