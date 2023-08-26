# Simple DynamoDB reader

This is a simple code to access AWS dynamoDB database to check for if a resource for a given date is 
present in given table or not. The dynamoDB table name is hard-coded `readiness-states` but you can feel free
take it from args too. 

## Motivation

This code is used in Apache Airflow as KubernetesPodSensor in tutorial.

## Build instructions

### Build locally

* create virtual environment: 

   `PIP_NO_CACHE_DIR=0 PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy`

* activate venv

  `source .venv/bin/activate`

* export environemnt variables

  ```js
  export AWS_ACCESS_KEY_ID=<aws_access_key_id>
  export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
  export AWS_REGION=<aws_region>
  ```

* run

  `python main.py readiness-check --table-name <resource_name> --date <date YYYY-MM-DD>`

### Using Docker

`docker build . -t readiness-check`

```
docker run --rm -e AWS_ACCESS_KEY_ID=<aws_access_key_id> \
                -e AWS_SECRET_ACCESS_KEY=<aws_secret_access_key> \
                -e AWS_REGION=<aws_region (default=eu-west-1)>
                readiness-check --table-name <resource_name> --date <date YYYY-MM-DD>
```

### Using Nerdctl

`nerdctl --namespace k8s.io build . -t readiness-check`

```
nerdctl run --rm --namespace k8s.io  
                 -e AWS_ACCESS_KEY_ID=<aws_access_key_id> \
                 -e AWS_SECRET_ACCESS_KEY=<aws_secret_access_key> \
                 -e AWS_REGION=<aws_region (default=eu-west-1)>
                 readiness-check --table-name <resource_name> --date <date YYYY-MM-DD>
```

