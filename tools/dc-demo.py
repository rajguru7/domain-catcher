#!/usr/bin/env python
import os
import json
import re
from urllib.parse import urlparse

git_hook = r"""#!/usr/bin/env bash

# Get the diff of staged changes, showing only lines that are added or removed
STAGED_DIFF=$(git diff --cached --unified=0)
# STAGED_DIFF=$(cat temp)

# grep -R -o -P "https?://[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|\/))" "$1"

URL_PATTERN="https?://[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|\/))"
DOMAIN_PATTERN="s/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/"
# https://stackoverflow.com/questions/2497215/how-to-extract-domain-name-from-url

# If there are no URLs in the staged changes, exit
if ! echo "$STAGED_DIFF" | grep -oP "$URL_PATTERN" >/dev/null; then
    exit 0
fi

DC_DOMAIN_LIST='.dc.json'

# Temporary files for URLs
temp_added_domains=$(mktemp)
temp_removed_domains=$(mktemp)
temp_known_domains=$(mktemp)

# Cleanup function to remove temp files on exit
cleanup() {
    rm -f "$temp_added_domains" "$temp_removed_domains" "$temp_known_domains"
}
trap cleanup EXIT


# Function to process lines from diff
process_line() {
    local line=$1
    if [[ $line == +* ]]; then
        # echo "$line"
        echo "$line" | grep -oP "$URL_PATTERN" | sed -e "$DOMAIN_PATTERN" >> "$temp_added_domains"
        # cat "$temp_added_domains"
    elif [[ $line == -* ]]; then
        echo "$line" | grep -oP "$URL_PATTERN" | sed -e "$DOMAIN_PATTERN" >> "$temp_removed_domains"
    fi
}

# Process each line of the diff
while read -r line; do
    process_line "$line"
done <<< "$STAGED_DIFF"

# Sort the outputs for comparison
sort -u "$temp_added_domains" -o "$temp_added_domains"
sort -u "$temp_removed_domains" -o "$temp_removed_domains"

# Read known URLs from JSON file, sort them, and store in temp file
if [[ -f "$DC_DOMAIN_LIST" ]]; then
    jq -r '.catcher.run_time[]' "$DC_DOMAIN_LIST" | sort -u > "$temp_known_domains"
else
    echo "dc config file does not exist: $DC_DOMAIN_LIST"
    exit 1
fi

# Compare and display added URLs not in the known list
comm_output=$(comm -23 "$temp_added_domains" "$temp_known_domains")
if [ -n "$comm_output" ]; then
    echo "Newly added domains (not in dc config):"
    echo "$comm_output"

    # Prompt user to add URLs
    read -rp "Proceed with adding these domains to dc config? (y/n) " add_response < /dev/tty
    if [[ "$add_response" == "y" ]]; then
        comm -23 "$temp_added_domains" "$temp_known_domains" | while read -r domain; do
            jq --arg domain "$domain" '.catcher.run_time += [$domain]' "$DC_DOMAIN_LIST" > tmp.$$ && mv tmp.$$ "$DC_DOMAIN_LIST"
        done
        echo "please run domain-catcher again to update the enforcement policies"
    fi

fi


# # Compare and display removed URLs that are in the known list
# echo "Known URLs that were removed:"
# comm -12 "$temp_removed_domains" "$temp_known_domains"
#
# # Prompt user to remove URLs
# read -rp "Do you want to remove these URLs from the known list? (y/n) " remove_response
# if [[ "$remove_response" == "y" ]]; then
#     comm -12 "$temp_removed_domains" "$temp_known_domains" | while read -r url; do
#         jq --arg url "$url" 'del(.urls[] | select(. == $url))' "$JSON_URL_LIST" > tmp.$$ && mv tmp.$$ "$JSON_URL_LIST"
#     done
# fi

if [ -n "$(cat "$temp_removed_domains")" ]; then
    echo "The below domains were removed. Please check if they are still needed."
    cat "$temp_removed_domains"
fi

exit 0
"""

policies = {
    "kubernetes": {
        "cilium": """\
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "to-fqdn"
spec:
  endpointSelector:
    matchLabels:
      {deployment_label}
  egress:
    - toEndpoints:
      - matchLabels:
          "k8s:io.kubernetes.pod.namespace": kube-system
          "k8s:k8s-app": kube-dns
      toPorts:
        - ports:
           - port: "53"
             protocol: ANY
          rules:
            dns:
              - matchPattern: "*"
    - toFQDNs:
"""
    }
}

gh_workflows = {
    "kubernetes": {
        "cilium": """\
name: Domain Enforcer

on:
  push:
    branches:
      - main
    paths:
      - 'cilium-network-policy.yaml'

jobs:
  enforce_network_policy:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Set up Kubernetes kubectl
        uses: azure/setup-kubectl@v1

      - name: Configure Kubernetes context
        uses: azure/k8s-set-context@v1
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG }}

      - name: Enforce network policy
        run: |
            kubectl apply -f cilium-network-policy.yaml
"""
    }
}

def extract_urls(directory):
    """Extract URLs from all files in the given directory."""
    url_pattern = re.compile(r'https?://[^\s"\'\]]+')
    urls = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    found_urls = url_pattern.findall(text)
                    urls.extend(found_urls)
    return urls

def extract_domain(url):
    """Extract the domain from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return None

def create_config():
    return {
        "catcher": {
            "build_time": [],
            "run_time": []
        },
        "enforcer": {
            "value": False,
            "run_time": {
                "environment": "",
                "cni": "",
                "deployment_namespace": "",
                "deployment_label": ""
            },
            "build_time": {}
        }
    }

def main():
    repo_root_dir = os.getcwd()

    if os.path.exists(f"{repo_root_dir}/.dc.json"):
        print("Configuration file found: .dc.json")
        with open(f"{repo_root_dir}/.dc.json", "r") as f:
            dc_config = json.load(f)
        if dc_config["enforcer"]["value"]:
            policy = ""
            gh_workflow = ""
            enforcer_runtime = dc_config["enforcer"]["run_time"]
            if enforcer_runtime["environment"] == "kubernetes" and enforcer_runtime["cni"] == "cilium":
                policy = policies["kubernetes"]["cilium"].format(deployment_label=enforcer_runtime["deployment_label"])
                for domain in dc_config["catcher"]["run_time"]:
                    policy += (f"        - matchName: \"{domain}\"\n")
                gh_workflow = gh_workflows["kubernetes"]["cilium"]

                with open("cilium-network-policy.yaml", "w") as f:
                    f.write(policy)
                with open(".github/workflows/domain_enforcer.yml", "w") as f:
                    f.write(gh_workflow)
            print("Policy file created: cilium-network-policy.yaml")
            print("GitHub workflow file created: .github/workflows/domain_enforcer.yml")
    else:
        dc_config = create_config()
        urls = extract_urls(repo_root_dir)
        unique_domains = set(extract_domain(url) for url in urls if extract_domain(url))
        dc_config["catcher"]["run_time"] = list(unique_domains)
        with open(".dc.json", "w") as f:
            json.dump(dc_config, f, indent=4)
        with open(".git/hooks/pre-commit", "w") as f:
            f.write(git_hook)
        os.system("chmod +x .git/hooks/pre-commit")
        print(f"Unique domains found: {unique_domains}")
        print("Configuration file created: .dc.json")
        print("Git hook created: .git/hooks/pre-commit")


if __name__ == "__main__":
    main()

