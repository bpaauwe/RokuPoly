#!/usr/bin/env bash
pip3 install -r requirements.txt --user

mkdir -p profile/nodedef
mkdir -p profile/nls
mkdir -p profile/editor
cp -pr template/* profile
