#!/bin/bash

apt-get install sudo

sudo apt-get update \
    && apt-get install -y wget unzip \
    && rm -rf /var/lib/apt/lists/*

# 更新地址：
#   https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
#   https://chromedriver.storage.googleapis.com/index.html
wget -N http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_98.0.4758.80-1_amd64.deb
wget -N https://chromedriver.storage.googleapis.com/98.0.4758.80/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip
