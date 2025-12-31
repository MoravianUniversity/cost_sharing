

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

  This will run `setup.py` to create a `cost_sharing` package


## Running the Application

From the project root directory (where `setup.py` is located):

```bash
python -m cost_sharing.app
```

The app will start on `http://localhost:8000`


## Testing

Test can be run in the root of the project or from the `tests` folder.  They cannot be run in `src` or its subfolders.

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

To check the source and tests for compiance to style guides:

  ```
  pylint src tests
  ```

The file `pylintrc` contains configuration options for Pylint.  Changes to this
file should only be done after consultation with the team.  This is especially
true for the `disable` setting, which disables a check across the entire codebase.

Marking code with `# pylint: disable=<some-message>` will disable the `<some message>` 
rule for that code.  This should be used **sparkingly**, and only after consultation with
the team.


## Manual Deploy on EC2

* Create an EC2 Instance
  * t3.micro
  * Use `labsuser.pem`
  * Enable port 443
* SSH to instance

  ```
  ssh -i ~/.ssh/labsuser.pem ec2-user@<instance IP>
  ```

* Install `git`

  ```
  sudo yum install -y git
  ```

* Clone repo

  ```
  git clone <repo url>
  ```

* In repo, create `.venv` and install libraries

  ```
  cd cost_sharing
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/pip install -e .
  ```

* Add credentials to `.env` for subdomain registration

  ```
  USERNAME=<username>
  TOKEN=<token>
  LABEL=costsharing
  ```

  This step used the [AWS DNS Subdomain System](https://webapps.cs.moravian.edu/awsdns/).

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

  When prompted, use the subdomain `<username>costsharing.moraviancs.click`

* Configure app to launch with Systemd

  ```
  sudo cp flask.service /etc/systemd/system
  sudo systemctl enable flask.service
  sudo systemctl start flask.service
  ```

  Verify with `sudo systemctl status flask.service`



## CI/CD

**CI**: Each time a developer pushes testing (with coverage) and static analysis are run automatically.
The results are reported in the PR, and no PR should be merged if either fails.


**CD**: After a PR is merged into `main` the changes can be deployed to the production server using
a Github Action.  

  * Click on "Actions" on the `upstream` repo
  * Click on "Redeploy on AWS" in the list of Actions
  * Click on the "Run Workflow" dropdown on the right and then on the "Run Workflow" button

This action uses Github Secrets (in the "Actions and variable" secction)

  * `HOSTNAME` contains the DNS name of the server
  * `LABSUSERPEM` contains the text of the `labsuser.pem` file (i.e. the *private* half of the SSH key)

This action will SSH to the server and run the `redeploy.sh` script.  This script will:

  * Stop the `gunicorn` process with Systemd
  * Perform a `git pull origin main` (NOTE: `origin` points to the upstream repo because development should *never* happen in prod)
  * Start the `gunicorn` process with Systemd
