#!/bin/bash
apt-get update
apt-get install -y chromium-chromedriver
export PATH=$PATH:/usr/lib/chromium/
python3 main.py