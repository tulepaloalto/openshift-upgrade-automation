# Openshift Helm Chart Upgrade Automation
This automation will upgrade the helm chart to the n-1 version of Compute.

## Download this repository

## Install dependencies

```pip3 install -r requirements.txt```

## Configuration File (config.yml)

    release-name:  <release-name> #name of the automation upgrade release

    current-version: '33_01_137' #This is the current defender version

    hard-version: None #Set this value if you'd like to upgrade to a specific version

    next-version: None #Leave as None, this will set itself when a new compute version is detected. 

    prisma-cloud-password: <prisma cloud secret access key> #encode in b64 before putting in

    prisma-cloud-url: https://us-east1.cloud.twistlock.com/us-2-158320372/api/v32.05/ #compute URL, can be found in Prisma Cloud Console -> Runtime Security -> Manage -> System -> Utilities -> Path to Console

    prisma-cloud-username: <prisma cloud access key id> #encode in b64 before putting in

    cluster-tokens: [] #b64_encode each cluster service account token before putting in

## How to run
`python3 automation.py config.yml values.yaml`

Note: values.yaml is the configuration file for the helm chart that should be available during initial download of the helm chart tar.gz. The automation essentially changes the version number of the defender used by the image_name and the DOCKER_TWISTLOCK_TAG

### Logging

All logs should be stored in openshift_upgrade_automation.log after the function is ran.