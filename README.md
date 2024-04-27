# Domain Catcher

"Beat obfuscation by only allowing expected Domains/IPs"

Aims: 
1. To restrict network calls to allowlist of domains/IPs based on process
   (single host) or service (k8s, cloud, etc.)
2. To automate the process of generating the allowlist based on the source code
   of the application.

## Demo


**Requirements**
1. K8s cluster with cilium network policy
2. Kubernetes API access from github actions (KUBECONFIG should be set in the
   github secrets)

**Steps**
1. Clone sample repo on which to test domain-catcher
2. Download dc-demo script at root of git repo
    ```bash
    git clone https://github.com/rajguru7/url-fetcher.git
    cd url-fetcher
    curl -O https://raw.githubusercontent.com/rajguru7/domain-catcher/main/tools/dc-demo.py
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
6. Push the changes to the repo

