#!/bin/sh
# Test what key codes the Kindle sends

export TERM=linux
cd /mnt/us/kLibby/src
python3 debug_keys.py
