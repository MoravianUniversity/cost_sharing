

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


## Run Tests

Test can be run in the root of the project or from the `tests` folder.  They cannot be run in `src` or its subfolders.

  ```
  pytest
  ```

## Run Static Analysis

To check the source and tests for compiance to style guides:

  ```
  pylint src tests
  ```


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
