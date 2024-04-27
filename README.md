# Domain Catcher

"Beat obfuscation by only allowing expected Domains/IPs"

Aims: 
1. To restrict network calls to allowlist of domains/IPs based on proces (single
   host) or service (k8s, cloud, etc.)
2. To automate the process of generating the allowlist based on the source code
   of the application.

## A URL Finder

* Look for files and put in set
* Get file-types from set of files selected and put in set
* Download tree-sitter parsers for each file-type detected if not present
* extract URLs using tree-sitter parser for corresponding files
* URL finding will only run on the diffs to see if any new URLs are being
  introduced.
  * Can tree-sitter run on only the diff?
  * Do we need tree-sitter or can we do a simple regex?

The source of the URL should also be collected so that maintainer can review the
list later to define the category of each URL.

The maintainer has to categorise each URL to the time of requirement:
* Build time
* Runtime

### Plugin system

* Extend sources of URLs detected in domain-catcher by allowing maintainer to
  add another source of URLs like a config file with a specific regex match.
* Provision for manual addition of URLs by maintainer.

### Summing up maintainer work:

1.  Review URLs detected
2.  Categorise URLs
3.  Optional:
    * Add new sources of URLs
    * Add manual list of URLs

## Restrict network based on list generated

* The list generated will be converted to a form which can be used to restrict
  the network in the end user's environment.
* The domains listed have to be converted to IPs for network rules to be
  enforced.

Refer:
1. <https://github.com/falcosecurity/falco/issues/835#issuecomment-531274911>
2. <https://falco.org/docs/rules/fd-sip-name/>

### Build time

* What about restricting build time URLs?
* Will have to analyse all CI commands to see which commands lead to network
  calls
* Restricting should be done on the runner or on the cloud firewall/network if
  runner is set up with proper networking in an enterprise?

Cases:
1. GitHub runner
2. Larger GitHub runners
3. Self Hosted runners
4. 3rd party CI/CD - Jenkins, Travis, CircleCI, etc.
5. Manual build and upload of release binaries
6. No build, user builds locally

### Runtime

There are a lot of ways a program can be deployed.

Help to automatically generate rules for all deployment types individually or
generate rules for one tool which can be a plugin for all deployment types.

* Generate OPA Rego rules automatically based on list of domains.
* OPA rules can be created to configure:
    * iptables in standalone machines
    * cloud firewalls for cloud environment
    * Istio egress rules for service mesh
    * Kubernetes network policies/envoy/isio for k8s clusters
      <https://tanzu.vmware.com/content/blog/enhancing-kubernetes-security-with-opa>
      <https://monzo.com/blog/controlling-outbound-traffic-from-kubernetes>

There are multiple ways to configure policies on kubernetes:
- <https://github.com/aquasecurity/trivy>
- <https://snyk.io/plans/>
- <https://github.com/datreeio/datree>
- <https://github.com/bridgecrewio/checkov>
- <https://github.com/FairwindsOps/polaris>
- <https://kyverno.io/>
- <https://github.com/open-policy-agent/gatekeeper>



Things I am considering:
* It should be possible to reuse the Falco component to generate the list of IPs
  based on domains.
* No need to detect the network calls, just keep an updated list of IPs
  based on domains. I don't need Falco as a dependency, only OPA.
* This could be run as a cronjob:
    * Keeps the IP list updated
    * How to persist and update the domain list which the cronjob queries?
    * If IP list updated
        * Generate Rego rule based on type of deployment of application (k8s,
          standalone, cloud, etc.)
        * The type of deployment of applications and how their network is
          restricted(firewall, istio, iptables etc) will have to configured and
          persisted somewhere.
        * Will have to figure how Rego rules work and how to generate them. 
        * Some kind of template for each deployment type.
        * Submit the updated rule to OPA for enforcement.

* The project scope has increased a lot. Will people find this useful?
        
### Runtime Usage Scenarios

There will be different scenarios based on control over source code repository.

Privately owned source code repository and deployment environment - possible to
chain the domain list created in the source code to the deployment environment.
For example, Github actions call OPA's REST API to configure network
restrictions. The endpoints found in the source code in this case can be private
IPs.

No ownership of either the source code repository or the deployment environment
* Source code owners can publish domain-list/post-install scripts (if supported
  by the package manager) to release page.
* End users will need a tool that can handle the domain-list from the
  release/image. This tool will create the policy based on type of deployment.
  For example, Rego rules if OPA present, then what Rego rules based on specific
  deployment. If OPA not present, then direct iptables, network policy, or a
  format which can be consumed by a firewall with a REST API.
* This tool can be run directly on github actions when there is control over
  both the source code and deployment environment.


1.  Single Linux host

    * Automatically configure end user's linux host to 'only allow' network
      calls that are required by the application.
    * I could use iptables but then only ALLOW rules can be added since iptables
      is global. Can't put DENY all.
    * Need to find a way to restrict also based on application
    * SELinux is too much work to set-up for random users to adopt
    * Also how is it possible to configure someone's linux host from github
      actions? It needs to be done at the end user host only.
        * Sigstore allows developers to sign container images. Can I store list
          of urls in a signed container image?
        * during creation of package, an optional post install script could be
          included and then the package manager client would install the package
          with the post install script if passed as an argument.

2.  Corporate Linux Host
    
    * Has SELinux?
    * Use SELinux to restrict network calls based on application

3.  Kubernetes Cluster

    * Kubernetes SIG Network is working on FQDN based network policies.
      <https://network-policy-api.sigs.k8s.io/>,
      <https://network-policy-api.sigs.k8s.io/npeps/npep-133/>

