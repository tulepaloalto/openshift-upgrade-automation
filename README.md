# Openshift Helm Chart Upgrade Automation
This automation will upgrade the helm chart to the n-1 version of Compute.

## Download this repository

	@@ -9,36 +8,56 @@ This automation will upgrade the helm chart to the n-1 version of Compute.

## Configuration File (config.yml)

    release-name:  <release-name> #name of the automation upgrade release

    current-version: '33_01_137' #This is the current defender version

    hard-version: None #Set this value if you'd like to upgrade to a specific version

    next-version: None #Leave as None, this will set itself when a new compute version is detected. 

    prisma-cloud-password: <prisma cloud secret access key> #encode in b64 before putting in

    prisma-cloud-url: https://us-east1.cloud.twistlock.com/us-2-158320372/api/v32.05/ #compute URL, can be found in Prisma Cloud Console -> Runtime Security -> Manage -> System -> Utilities -> Path to Console

    prisma-cloud-username: <prisma cloud access key id> #encode in b64 before putting in

    cluster-tokens: [] #b64_encode each cluster service account token before putting in


### Testing

To test, modify the config.yml file and change the current-version to '33_01_000', and change the next-version to '33_01_136'. Once the run is finished, the current-version should be 33_01_136, and the next-version should be '33_01_137'.

The version number of the image_name in values.yaml should be at '33_01_136'

Note: Not real versions mentioned in this example, for testing purposes only

## How to run
`python3 automation.py config.yml values.yaml`
