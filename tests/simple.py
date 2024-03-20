from domain_catcher.catcher import DomainCatcher

dc = DomainCatcher()

# Extract URLs
urls = dc.extract_urls_from_file("tests/test.py")
print(urls)
