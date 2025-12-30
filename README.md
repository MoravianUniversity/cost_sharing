

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
