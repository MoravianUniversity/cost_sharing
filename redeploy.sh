sudo systemctl stop flask
git pull origin main
# Run this in case a new library is added
.venv/bin/pip install -r requirements.txt
sudo systemctl start flask
