

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
  * Enable port 80 and 443
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

* Configure app to launch with Systemd

  ```
  sudo cp flask.service /etc/systemd/system
  sudo systemctl enable flask.service
  sudo systemctl start flask.service
  ```

  Verify with `sudo systemctl status flask.service`
