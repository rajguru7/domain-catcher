# Domain Catcher

"Beat obfuscation by only allowing expected Domains/IPs"

Aims: 
1. To automate the process of generating the allowlist based on the source code
   of the application.
1. Help in restricting network calls to allowlist of domains/IPs based on
   process (single host) or service (k8s, cloud, etc.) in various deployment
   scenarios.

## Demo

**Requirements**
1. K8s cluster with cilium network policy
2. Kubernetes API access from github actions (KUBECONFIG should be set in the
   github secrets)

**Steps**
1. Fork and Clone sample repo on which to test domain-catcher
2. Download dc-demo script at root of git repo
    ```bash
    git clone https://github.com/rajguru7/url-fetcher.git
    cd url-fetcher
    curl -O https://raw.githubusercontent.com/rajguru7/domain-catcher/main/tools/dc-demo.py
    chmod +x dc-demo.py
    ./dc-demo.py
    ```
3. Run the script
    * It will create a .dc.json file with the allowlist of domains
4. Update .dc.json with the deployment type as below:
    ```json
    {
      "catcher": {
        "build_time": [],
        "run_time": [
          "www.google.com",
          "github.com"
        ]
      },
      "enforcer": {
        "value": true,
        "run_time": {
          "environment": "kubernetes",
          "cni": "cilium",
          "deployment_namespace": "",
          "deployment_label": "app: url-fetcher"
        },
        "build_time": {}
      }
    }
    ```
5. Run the script again
    * It will create a cilium network policy to allow only the domains in the
      allowlist
    * It will create a github action to update the allowlist on every push
6. If you are not making changes to the code for testing, delete the workflow
   yaml (build-deploy.yaml). If you are going to make changes to the code,
   update the image repository path in build-deploy.yaml.
7. Push the changes to your forked repo

### Results

* `url-fetcher` is a sample flask app.
* expose its service from the k8s cluster `kubectl port-forward
  service/url-fetcher-service 8080:8080`
* <http://localhost:8080/status> will show 200 OK for www.google.com, github.com
  and evil.com (obfuscated entry in code)
* After running domain-catcher and running the workflow successfully, the
  response for evil.com will be connection timed out.
* This process demonstrates how to restrict network calls to only expected
  domains/IPs.

### Testing locally 

In case you don't have access to a k8s cluster which is accessible publicly, you
can use minikube and [act](https://github.com/nektos/act) to test the workflow
action locally. To skip configuring minikube client authentication in KUBECONFIG
to pass to your `act` in workflow you can use `kubectl proxy --api-prefix=/` to
expose kubernetes api server on localhost without authentication.

```bash
minikube --cni=cilium start
gh act --secret-file ../.secrets --env ACT=1
```

`.secrets` should have KUBECONFIG set. DOCKER_USERNAME and DOCKER_PASSWORD
depending on step 6.

example `.secrets` file:
```
DOCKER_USERNAME=<docker-username>
DOCKER_PASSWORD="<docker-password>"
KUBECONFIG='apiVersion: v1
clusters:
- cluster:
    extensions:
    - extension:
        last-update: Sat, 20 Apr 2024 23:57:32 EDT
        provider: minikube.sigs.k8s.io
        version: v1.32.0
      name: cluster_info
    server: http://172.24.192.1:8001 #Replace with your local k8s api address
  name: minikube
contexts:
- context:
    cluster: minikube
    extensions:
    - extension:
        last-update: Sat, 20 Apr 2024 23:57:32 EDT
        provider: minikube.sigs.k8s.io
        version: v1.32.0
      name: context_info
    namespace: default
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users: null'
```
