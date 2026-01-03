
## Overview

This document provides steps to setup dev and prod using your Moravian Google account and 
an EC2 instance launch in an AWS Learner Lab environment.

### Prerequisites

* Python 3.11 or later
* git
* Moravian Google Account
* Your username and bearer token from the [AWS DNS Subdomain System](https://webapps.cs.moravian.edu/awsdns/)
* An AWS Academy Learner Lab account


## Google OAuth Setup

Before you can run the application, you need to create a Google OAuth application in the Google Cloud Console.


### Step 1: Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your `@moravian.edu` Google account
3. Click on the "project picker" in the top bar (next to the Google Cloud logo) and then "New Project".  Enter in the following values:
   * **Project name**: "Cost Sharing App"
   * **Organization** and **Location**: Default values
4. Ensure the project is the current project (use the project picker if it isn't)


### Step 2: Configure the Consent Screen

1. Click on ☰ (the hamburger menu on the top-left)
2. In the left sidebar, navigate to "APIs & Services" and "OAuth consent screen"
3. Click "Get started" and fill out the fields:
  * **App name**: "Cost Sharing App"
  * **User support email**: Your `@moravian.edu` email
  * **Audience**: Internal
  * **Contact Information**: Your `@moravian.edu` email
  * Check the box to agree to the User Data Policy


### Step 3: Create OAuth Client

Your subdomain is your username from the [AWS DNS Subdomain System](https://webapps.cs.moravian.edu/awsdns/)
followed by "costsharing".  For example, `colemanbcostsharing`.

1. In the left sidebar, click "Clients" and then "Create client".  Provide the following values:
  * **Application type**: Web application
  * **Name**: Cost Sharing App
  * **Authorized JavaScript origins**: `http://localhost:8000` and `https://<your-subdomain>.moraviancs.click`
  * **Authorized redirect URIs**: `http://localhost:8000/` and `https://<your-subdomain>.moraviancs.click/`
    * **NOTE**: The trailing `/` on these URIs is **required**
2. When you click "Create" it will show you a Client ID and Client secret.  **SAVE THESE VALUES** - you need them to configure the server (next section).  You cannot retrieve the client secret after you leave this screen.


## Configuration

In both dev and prod, the system will get configuration options from a `.env` file.  Create this file in 
the root of the project with the following values.  **NOTE:** The `.env` file should **never** be committed to git.


* `BASE_URL`: The base URL of your application.  This must match one of the redirect URIs configured in the Google Cloud Console.
  * `http://localhost:8000` in dev
  * `https://<your-subdomain>.moraviancs.click` in prod
* `GOOGLE_CLIENT_ID`: The OAuth 2.0 Client ID from Google Cloud Console
* `GOOGLE_CLIENT_SECRET`: The OAuth 2.0 Client Secret from Google Cloud Console
* `JWT_SECRET`: A secret key used to sign JWT tokens


A safe way to generate the `JWT_SECRET` is with Python's `secrets` module:

```
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```


### Template `.env` file (in dev and prod)

```bash
BASE_URL=<redirect-URI>
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
JWT_SECRET=<your-random-secret-key>
```


In prod you also need to have the following values for the [AWS DNS Subdomain System](https://webapps.cs.moravian.edu/awsdns/):

* **USERNAME** - Your username in the AWS DNS Subdomain System 
* **TOKEN** - The bearer token provided by the AWS DNS Subdomain System
* **LABEL** - This should be `costsharing`

The username and token provide authentication when you register your IP on the EC2 instance.  The username and label define 
the subdomain.  For example if the username is `colemanb` and the subdomain is `costsharing`, the system will register
your IP as `colemanbcostsharing.moraviancs.click`.

### Template for extra `.env` values (in prod)

**ADD** these values to the `.env` file:

```bash
USERNAME=<username>
TOKEN=<token>
LABEL=costsharing
```


## Dev Setup

* Create a virtual environment

  ```
  python3 -m venv .venv
  ```

* Activate the environment

  ```
  source .venv/bin/activate
  ```

* Install required packages

  ```
  pip install -r requirements.txt
  ```

* Install the system as a editable package (changes to code will be seen)  

  ```
  pip install -e .
  ```

  This will run `setup.py` to create a `cost_sharing` package.  The `-e` switch installs 
  in editable mode so that changes to the source are "seen" within the package.

* Create a `.env` file as described in the [Configuration](#configuration) section.
Use `http://localhost:8000` as the `BASE_URL`.

* Initialize the database:

  ```
  mkdir -p database
  sqlite3 database/costsharing.db < src/cost_sharing/sql/schema-sqlite.sql
  ```

* (Optional) Load sample data:

  ```
  sqlite3 database/costsharing.db < src/cost_sharing/sql/sample-data.sql
  ```


## Running the Application in dev

From the project root directory (where `setup.py` is located):

```bash
python -m cost_sharing.app
```

The app will start on `http://localhost:8000`


## Testing

You can run tests from the root of the project or from the `tests` folder.  They cannot be run in `src` or its subfolders.

  ```
  pytest
  ```

The file `pytest.ini` configures how `pytest` and `pytest-cov` handle testing.  Most options
shouldn't need to be changed.  The `--cov-fail-under` option is set to `90` and should not be
changed without team discussion.

Marking code with `# pragma: no cover` will cause `pytest-cov` to exclude the code from 
the coverage computation.  This should be used **sparingly**, and only after consultation
with the team.


## Static Analysis

To check the source and tests for compliance to style guides:

  ```
  pylint src tests
  ```

The file `pylintrc` contains configuration options for Pylint.  Changes to this
file should only be done after consultation with the team.  This is especially
true for the `disable` setting, which disables a check across the entire codebase.

Marking code with `# pylint: disable=<some-message>` will disable the `<some message>` 
rule for that code.  This should be used **sparingly**, and only after consultation with
the team.


## Manual Deploy on EC2

* Create an EC2 Instance
  * **Instance Type**: `t3.micro`
  * **Key Pair**: `vockey`
  * In **Network Setting** select:
    * "Allow HTTPS traffic from the internet"
    * "Allow HTTP traffic from the internet"

* SSH to the instance

  ```
  ssh -i ~/.ssh/labsuser.pem ec2-user@<instance IP>
  ```

* Install `git`

  ```
  sudo yum install -y git
  ```

* Clone the repo

  ```
  git clone <repo url>
  ```

* In the repo, create a virtual environment and install the requred ibraries

  ```
  cd cost_sharing
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/pip install -e .
  ```

  NOTE: `-e` (install in editable mode) is required because the CD process will use `git pull` to update source files.

* Create a `.env` file as described in the [Configuration](#configuration) section.  On EC2 you need both the 
OAuth values **and** the AWS DNS Subdomain System values.

* Initialize the database:

  ```
  mkdir -p database
  sqlite3 database/costsharing.db < src/cost_sharing/sql/schema-sqlite.sql
  ```

* Register your subdomain

  ```
  ./register_ip.sh
  ```

* Create SSL certificates (commands from the [Let's Encrypt Setup](https://certbot.eff.org/instructions?ws=other&os=pip))

  ```
  sudo python3 -m venv /opt/certbot/
  sudo /opt/certbot/bin/pip install --upgrade pip
  sudo /opt/certbot/bin/pip install certbot certbot
  sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
  sudo certbot certonly --standalone
  ```

  When prompted, use the subdomain created by the AWS DNS Subdomain System, `<your-subdomain>.moraviancs.click`.

* Configure app to launch with Systemd

  ```
  sudo cp flask.service /etc/systemd/system
  sudo systemctl enable flask.service
  sudo systemctl start flask.service
  ```

  Verify with `sudo systemctl status flask.service`



## CI/CD

**CI**: Each time a developer pushes, testing (with coverage) and static analysis are executed automatically.
The results are reported in the PR, and no PR should be merged if either fails.


**CD**: After a PR is merged into `main` the changes can be deployed to the production server using
a manual Github Action.  

  * Click on "Actions" on the `upstream` repo
  * Click on "Redeploy on AWS" in the list of Actions
  * Click on the "Run Workflow" dropdown on the right and then on the "Run Workflow" button

This action uses Github Secrets (in the "Actions and variables" section)

  * `HOSTNAME` contains the DNS name of the server
  * `LABSUSERPEM` contains the text of the `labsuser.pem` file (i.e. the *private* half of the SSH key)

This action will SSH to the server and run the `redeploy.sh` script.  This script will:

  * Stop the `gunicorn` process with Systemd
  * Perform a `git pull origin main` (NOTE: `origin` points to the upstream repo because development should *never* happen in prod)
  * Start the `gunicorn` process with Systemd
