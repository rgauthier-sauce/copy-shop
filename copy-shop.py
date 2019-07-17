from string import Template
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
from sys import argv

import os
import json
import requests

USERNAME = os.environ["SAUCE_USERNAME"]
ACCESS_KEY = os.environ["SAUCE_ACCESS_KEY"]

def retrieve_job_info(domain, session_id):
    url = 'https://{}/rest/v1.1/jobs/{}'.format(domain, session_id)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()["base_config"]

def job_info_to_java(info, domain, template):
    capabilities = ""
    for key, value in info.items():

        if value == None:
            value = "null"
        elif type(value) == bool:
            value = str(value).lower()
        elif type(value) == str:
            value = '"' + str(value) + '"'

        capabilities += "caps.setCapability(\"{}\", {})\n".format(key, value)

    if domain == "app.saucelabs.com":
        domain = "ondemand.saucelabs.com"
    elif domain == "app.eu-central-1.saucelabs.com":
        domain = "ondemand.eu-central-1.saucelabs.com"
        
    return template.substitute(username=USERNAME, access_key=ACCESS_KEY, capabilities=capabilities, domain=domain)

def extract_url_info(url):
    parsed = urlparse(url)
    assert parsed.path.startswith("/tests/")
    return {
        "domain": parsed.netloc,
        "job_id": parsed.path[6:] # remove /tests/
    }

def main():
    url = argv[1]

    url_info = extract_url_info(url)
    
    info = retrieve_job_info(url_info["domain"], url_info["job_id"])

    template = Template(open("./template.java").read())
    print(job_info_to_java(info, url_info["domain"], template))

if __name__ == "__main__":
    main()
