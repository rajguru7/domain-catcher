
---
title: Domain Catcher
author: saurabh rajguru
---


# Aim

> "Beat obfuscation by only allowing expected FQDNs/IPs"

## Objectives

1. To restrict network calls to allowlist of FQDNs/IPs based on proces (single
   host) or service (k8s, cloud, etc.)
2. To automate the process of generating the allowlist based on the source code
   of the application.

---

# Scenarios

## Based on repository to deployment environment mapping

* One-to-One (control over source code repository and deployment environment)
  * possible to control the deployment environment from the source code repository
    For example, using a CI/CD pipeline to deploy the domain list to the firewall.
<!-- stop -->
* One-to-Many (single source code repository, multiple deployment environments)
    * Only list can be generated and stored in repository
    * Enforcement component to be run in deployment environment to consume the
      list and enforce the rules

___

# Scenarios

## Based on source of FQDNs

* Hardcoded in source-code
    * Specific format that can be caught by domain-catcher
    * Formats which will not be caught by domain-catcher - maintainer work
<!-- stop -->
* Dynamically configured during runtime
    * FQDNs coming from config files, environment variables, etc.
    * Could add client components to enforcer component that can fetch the list
      at runtime from the pre-defined sources
    * OR, maintainer manually adds the list to dc config if possible.

---

# Scenarios

## Based on run-time or build-time

* Run-time
    * Network calls made during the execution of the application
    * Restricting should be done on the host where the application is running
<!-- stop -->
* Build-time
    * Network calls made during build process
    * Restricting should be done on the runner or on the cloud firewall/network if
      runner is set up with proper networking in an enterprise

<!-- stop -->
The list generated must differentiate between FQDNs required during build-time
and run-time.

---

# Implementation

domain-catcher will execute differently based on different scenarios.
It will depend on various scenarios which will configured in a dc config file.
<!-- stop -->

1.  Run domain-catcher on the source code repository to generate initial list of
    FQDNs.
2.  Maintainer reviews the list and adds any missing FQDNs or dynamic sources.
3.  Deployment environment team configures the enforcer component in the dc
    config.
4.  Run domain-catcher again to enforce the rules based on the dc config.

---

# Enforcement

Enforcing network based on FQDN list

1. Kubernetes deployed with CNI plugin
    * policy yamls containing FQDNs can be directly applied
2. Single Linux host
    * Need to figure out how to restrict network calls per application.

---

# Demo

---

# Next Steps

1.  Join security-tooling WG meeting and show demo.
2.  Figuring out how to restrict network calls per application using FQDNs. 
3.  Covering more scenarios
4.  Adding ports

---

# THANK YOU

## Questions?
