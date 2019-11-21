from string import Template
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

import argparse
import os
import re
import json
import requests

USERNAME = os.environ["SAUCE_USERNAME"]
ACCESS_KEY = os.environ["SAUCE_ACCESS_KEY"]
MASTER_PASSWORD = os.environ.get("MASTER_PASSWORD")


def retrieve_job_info(domain, session_id):
    url = 'https://{}/rest/v1.1/jobs/{}'.format(domain, session_id)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()["base_config"]

def retrieve_rdc_appium_logs(domain, username, project, job_id):
    r = requests.post("https://app.testobject.com/api/rest/auth/login", {"user": username, "password": MASTER_PASSWORD})
    cookie = r.headers["Set-Cookie"]

    url = "https://app.testobject.com/api/rest/users"
    url += "/{}/projects/{}/apiKey/appium".format(username, project)

    r = requests.get(url, headers={"Cookie": cookie})
    api_key = r.json()["id"]

    url = "https://app.testobject.com/api/rest/v2/logs/{}/appium".format(job_id)
    r = requests.get(url, auth=HTTPBasicAuth(username, api_key))
    return r.json()


def job_info_to_java(info, domain, commands, template):
    capabilities = ""
    for key, value in info.items():
        if value is None:
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
    return template.substitute(username=USERNAME, access_key=ACCESS_KEY,
                               capabilities=capabilities,
                               commands=commands, domain=domain)

def rdc_job_info_to_java(info, domain, commands, template):
    capabilities = ""
    for key, value in info.items():
        if value is None:
            value = "null"
        elif type(value) == bool:
            value = str(value).lower()
        elif type(value) == str:
            value = '"' + escape(str(value)) + '"'

        capabilities += "caps.setCapability(\"{}\", {});\n".format(key, value)

    if domain == "app.testobject.com":
        domain = "https://eu1.appium.testobject.com/wd/hub"
    else:
        raise Exception("Invalid domain: {}".format(domain))

    commands = "\n".join(commands)
    return template.substitute(username=USERNAME, access_key=ACCESS_KEY,
                               capabilities=capabilities,
                               commands=commands, domain=domain)

def extract_vdc_url_info(url):
    parsed = urlparse(url)
    assert parsed.path.startswith("/tests/")
    return {
        "domain": parsed.netloc,
        "job_id": parsed.path[6:]  # remove /tests/
    }

def extract_rdc_url_info(url):
    parsed = urlparse(url)
    assert "app.testobject.com" in parsed.netloc
    assert "/appium/executions/" in parsed.fragment

    split_path = parsed.fragment.split("/")
    username = split_path[1]
    project  = split_path[2]
    test_report_id = int(split_path[-1])

    return {
        "domain": parsed.netloc,
        "job_id": test_report_id,
        "username": username,
        "project": project
    }


def get_log_filename(domain, session_id):
    url = 'https://{}/rest/v1/{}/jobs/{}/assets'.format(domain, USERNAME,
                                                        session_id)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()["sauce-log"]
    # return r.json()["base_config"]


def extract_commands(domain, session_id, log_filename):
    url = 'https://{}/rest/v1/{}/jobs/{}/assets/{}'.format(domain, USERNAME,
                                                           session_id,
                                                           log_filename)
    r = requests.get(url, auth=HTTPBasicAuth(USERNAME, ACCESS_KEY))
    return r.json()


def translate_commands(commands):
    java_commands = []
    for command in commands:
        if "status" in command:
            continue
        if command["method"] == "GET":
            continue

        c = "// ignored command"
        if command["path"] == "url" and command["method"] == "POST":
            c = "driver.get(\"{}\");".format(command["request"]["url"])
        elif command["path"] == "element" and command["method"] == "POST":
            if command["request"]["using"] == "xpath":
                c = "el = driver.findElement(By.xpath(\"{}\"));"\
                        .format(escape(command["request"]["value"]))
            elif command["request"]["using"] == "name":
                c = "el = driver.findElement(By.name(\"{}\"));".format(escape(command["request"]["value"]))
        elif command["path"].startswith("element/") and \
                command["path"].endswith("/click") and \
                command["method"] == "POST":
            c = "el.click();"
        elif command["path"].startswith("element/") \
                and command["path"].endswith("/clear") \
                and command["method"] == "POST":
            c = "el.clear();"
        elif command["path"].startswith("element/") and command["path"] \
                .endswith("/value") and command["method"] == "POST":
            c = "el.sendKeys(\"{}\");" \
                .format(escape(command["request"]["value"][0]))
        elif command["path"] == "timeouts" and command["method"] == "POST" \
                and command["request"]["type"] == "implicit":
            c = "driver.manage().timeouts().implicitlyWait({}," \
                 "TimeUnit.MILLISECONDS);".format(command["request"]["ms"])
        else:
            c += ": {} {}".format(command["method"], command["path"])

        java_commands.append(c)
    return java_commands

def translate_rdc_commands(appium_logs):
    commands_info = []
    java_commands = []
    capabilities  = None

    for line in appium_logs:
        if line["message"].startswith("[HTTP] -->"):
            info = parse_appium_log_line(line["message"])
        elif line["message"].startswith("[HTTP] {"):
            info["data"] = json.loads(line["message"][7:])
            commands_info.append(info)
        else:
            continue

    for command in commands_info:
        c = "//ignored command"
        if command["method"] == "POST" and command["path"] == "/wd/hub/session":
            capabilities = command["data"]["desiredCapabilities"]

        if command["method"] == "POST" and command["path"].endswith("/element"):
            if command["data"]["using"] == "accessibility id":
                c = "el = driver.findElementByAccessibilityId(\"{}\");".format(command["data"]["value"])
        elif command["method"] == "POST" and command["path"].endswith("/click"):
            c = "el.click();"
        elif command["method"] == "POST" and command["path"].endswith("/context"):
            c = "driver.context(\"{}\");".format(command["data"]["name"])
        else:
            c += ": {} {}\n".format(command["method"], command["path"])
            c += "// " + repr(command["data"])

        java_commands.append(c)
    return capabilities, java_commands


def parse_appium_log_line(line):
    info = {}
    pattern = "(\[HTTP\]) --> (GET|POST|PUT|DELETE) (.+)"
    results = re.search(pattern, line)

    if not results:
        raise Exception("Command not recognised: {}".format(line))

    info["method"] = results.group(2)
    info["path"] = unescape(results.group(3))
    return info


def escape(s):
    return s.replace("\"", "\\\"")

def unescape(s):
    return s.replace("\/", "/")

def main(arguments=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("job_urls", nargs="+", help="URL of test to copy.")

    args = parser.parse_args(arguments)
    for job_url in args.job_urls:
        parsed = urlparse(job_url)
        if parsed.netloc == "app.saucelabs.com" or parsed.netloc == "app.eu-central-1.saucelabs.com":
            _vdc_main(args, job_url)
        elif parsed.netloc == "app.testobject.com":
            _rdc_main(args, job_url)
        else:
            raise Exception("URL not recognized: {}".format(job_url))

def _vdc_main(args, job_url):
    url_info = extract_vdc_url_info(job_url)

    info = retrieve_job_info(url_info["domain"], url_info["job_id"])

    log_filename = get_log_filename(url_info["domain"], url_info["job_id"])
    commands = extract_commands(url_info["domain"], url_info["job_id"],
                                log_filename)
    java_commands = translate_commands(commands)

    template = Template(open("./template.java").read())
    print(job_info_to_java(info, url_info["domain"], java_commands,
                            template))

def _rdc_main(args, job_url):
    if not MASTER_PASSWORD:
        raise Exception("Environment variable MASTER_PASSWORD is empty. It is required for RDC URLs.")
    url_info = extract_rdc_url_info(job_url)
    info = retrieve_rdc_appium_logs(url_info["domain"], url_info["username"], url_info["project"], url_info["job_id"])

    capabilities, java_commands = translate_rdc_commands(info)

    template = Template(open("./template2.java").read())
    print(rdc_job_info_to_java(capabilities, url_info["domain"], java_commands,
                            template))

if __name__ == "__main__":
    main()
