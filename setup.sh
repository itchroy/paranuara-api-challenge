#! /bin/bash
sudo apt install -y python3-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt