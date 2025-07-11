#!/bin/bash

git fetch origin
git reset --hard origin/main
systemctl daemon-reload
systemctl restart myportfolio
