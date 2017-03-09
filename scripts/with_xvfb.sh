#!/usr/bin/env bash

# Xvfb is needed for electron karma tests
export DISPLAY=':99.0'
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
nvm alias default 6.0.0
nvm use 6.0.0

npm --version
node --version

echo "Starting app build"
eval $1
