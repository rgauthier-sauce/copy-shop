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

def job_info_to_java(info, domain, commands, template):
    capabilities = ""
    for key, value in info.items():
        if value == None:
            value = "null"
        elif type(value) == bool:
            value = str(value).lower()
        elif type(value) == str:
            value = '"' + escape(str(value)) + '"'

        capabilities += "caps.setCapability(\"{}\", {});\n".format(key, value)

    if domain == "app.saucelabs.com":
        domain = "ondemand.saucelabs.com"
    elif domain == "app.eu-central-1.saucelabs.com":
        domain = "ondemand.eu-central-1.saucelabs.com"
        
    commands = "\n".join(commands)
    return template.substitute(username=USERNAME, access_key=ACCESS_KEY, capabilities=capabilities, commands=commands, domain=domain)

def extract_url_info(url):
    parsed = urlparse(url)
    assert parsed.path.startswith("/tests/")
    return {
        "domain": parsed.netloc,
        "job_id": parsed.path[6:] # remove /tests/
    }

def get_log_filename(domain, session_id):
    url = 'https://{}/rest/v1/{}/jobs/{}/assets'.format(domain, USERNAME, session_id)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()["sauce-log"]
    # return r.json()["base_config"]

def extract_commands(domain, session_id, log_filename):
    url = 'https://{}/rest/v1/{}/jobs/{}/assets/{}'.format(domain, USERNAME, session_id, log_filename)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()

def translate_commands(commands):
    java_commands = []
    for command in commands:
        if command["method"] == "GET":
            continue

        c = "// ignored command"
        if command["path"] == "url" and command["method"] == "POST":
            c = "driver.get(\"{}\");".format(command["request"]["url"])
        elif command["path"] == "element" and command["method"] == "POST":
            if command["request"]["using"] == "xpath":
                c = "el = driver.findElement(By.xpath(\"{}\"));".format(escape(command["request"]["value"]))
        elif command["path"].startswith("element/") and command["path"].endswith("/click") and command["method"] == "POST":
            c = "el.click();"
        elif command["path"].startswith("element/") and command["path"].endswith("/clear") and command["method"] == "POST":
            c = "el.clear();"
        elif command["path"].startswith("element/") and command["path"].endswith("/value") and command["method"] == "POST":
            c = "el.sendKeys(\"{}\");".format(escape(command["request"]["value"][0]))
        elif command["path"] == "timeouts" and command["method"] == "POST" and command["request"]["type"] == "implicit":
            c = "driver.manage().timeouts().implicitlyWait({}, TimeUnit.MILLISECONDS);".format(command["request"]["ms"])
        else:
            c += ": {} {}".format(command["method"], command["path"])
        
        java_commands.append(c)
    return java_commands

def escape(s):
    s = s.replace("\"", "\\\"")
    # s = s.replace("'", "\'")
    return s

def main():
    url = argv[1]

    url_info = extract_url_info(url)
    
    info = retrieve_job_info(url_info["domain"], url_info["job_id"])

    log_filename = get_log_filename(url_info["domain"], url_info["job_id"])
    commands = extract_commands(url_info["domain"], url_info["job_id"], log_filename)
    java_commands = translate_commands(commands)

    template = Template(open("./template.java").read())
    print(job_info_to_java(info, url_info["domain"], java_commands, template))

if __name__ == "__main__":
    main()
