import requests
import json
import tarfile
import yaml
import sys
import logging
import base64
import subprocess

logger = logging.getLogger(__name__)

with open(sys.argv[1]) as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

PRISMA_CLOUD_CURRENT_VERSION=config["current-version"]
PRISMA_CLOUD_NEXT_VERSION=config["next-version"]
PRISMA_CLOUD_HARD_VERSION=config["hard-version"]
PRISMA_CLOUD_USERNAME=base64.b64decode(config["prisma-cloud-username"]).decode('utf-8')
PRISMA_CLOUD_PASSWORD=base64.b64decode(config["prisma-cloud-password"]).decode('utf-8')
PRISMA_CLOUD_URL=config["prisma-cloud-url"]
CLUSTER_TOKENS=config["cluster-tokens"]
RELEASE_NAME=config["release-name"]

def get_token():

    authenticate_url = PRISMA_CLOUD_URL + "authenticate"

    payload = json.dumps({
        "username": PRISMA_CLOUD_USERNAME,
        "password": PRISMA_CLOUD_PASSWORD
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.request("POST", authenticate_url, headers=headers, data=payload)
    token = json.loads(response.text)["token"]
    return token

def upgrade_helm_chart(values_file):
    with open(values_file) as stream:
        try:
            values = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        values["DOCKER_TWISTLOCK_TAG"]=values["DOCKER_TWISTLOCK_TAG"].replace(PRISMA_CLOUD_CURRENT_VERSION, PRISMA_CLOUD_NEXT_VERSION)
        values["image_name"]=values["image_name"].replace(PRISMA_CLOUD_CURRENT_VERSION, PRISMA_CLOUD_NEXT_VERSION)
        with open(values_file, 'w') as f:
            yaml.dump(values, f)
        
    for encoded_token in CLUSTER_TOKENS:
        token = base64.b64decode(encoded_token).decode('utf-8')
        results=subprocess.run(["oc", "login", "--token", token], capture_output=True)
        logging.info(results.stdout.decode("utf-8"))
        logging.info(results.stderr.decode("utf-8"))
        results=subprocess.run(["helm", "repo", "update"], capture_output=True)
        logging.info(results.stdout.decode("utf-8"))
        logging.info(results.stderr.decode("utf-8"))
        results=subprocess.run(["helm", "upgrade", RELEASE_NAME, "twistlock/twistlock-defender", "-f", values_file], capture_output=True)
        logging.info(results.stdout.decode("utf-8"))
        logging.info(results.stderr.decode("utf-8"))

def check_version(headers, values_file):

    version_url = PRISMA_CLOUD_URL + "version"
    response = requests.request("GET", version_url, headers=headers)
    latest_version = response.text.replace(".", "_").replace('"','')
    if PRISMA_CLOUD_HARD_VERSION!="None" and PRISMA_CLOUD_HARD_VERSION!=PRISMA_CLOUD_CURRENT_VERSION:
        logging.info("Hard version is set, installing helm with the desired hard version...")
        config["current-version"]=PRISMA_CLOUD_HARD_VERSION
    elif PRISMA_CLOUD_NEXT_VERSION=="None":
        if PRISMA_CLOUD_CURRENT_VERSION == latest_version:
            logging.info("Next version does not exist yet, the latest version is the same as the current version, upgrade will not commence until the latest version is past the next version. Exiting...")
            return
        else:
            logging.info("Next version does not exist yet, the latest version is n+1 from the current version, upgrade will not commence until the newest version is past the next version. Updating next version to the latest version. Exiting...")
            config["next-version"]=latest_version
            with open(sys.argv[1], 'w') as f:
                yaml.dump(config, f)
    else:
        if PRISMA_CLOUD_NEXT_VERSION != latest_version:
            logging.info("Latest version is newer than next version. Update the current version to the next version, update the next version to the latest version in config.yml. Upgrading helm chart to the next version...")
            config["current-version"]=PRISMA_CLOUD_NEXT_VERSION
            config["next-version"]=latest_version
            with open(sys.argv[1], 'w') as f:
                yaml.dump(config, f)
            upgrade_helm_chart(values_file)
        else:
            logging.info("Latest version is the same as next version. upgrade will not commence until the newest version is past the next version")

    return False

def main(values_file):
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='openshift_upgrade_automation.log', level=logging.INFO, format=FORMAT)
    logger.info("Openshift Upgrade Automation starting...")
    token = get_token()
    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + token
    }
    
    check_version(headers, values_file)

if __name__ == "__main__":
    main(sys.argv[2])