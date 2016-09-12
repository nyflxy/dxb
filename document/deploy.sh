#!/bin/sh
cd /usr/share/nginx/dxb
git pull origin dev
supervisorctl restart all