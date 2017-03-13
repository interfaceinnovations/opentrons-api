#!/usr/bin/env bash

set -e

run_install ()
{
  if [ "$1" == "linux" ]; then
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
  else
    mkdir -p ~/.nvm && export NVM_DIR=~/.nvm && source $(brew --prefix nvm)/nvm.sh && nvm alias default 6.0.0
    echo "$(brew --prefix nvm)/nvm.sh" >> ~/.bashrc
  fi

  if [ "$1" == "linux" ]; then
    export DISPLAY=':99.0'
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
  fi

  nvm install 6.0.0
  nvm use 6.0.0
  node --version
  npm --version

  pip3 install pip --upgrade
  echo "Upgrading virtualenv"
  pip3 install --upgrade virtualenv

  which pip
  which pip3
  pip3 --version
  mkdir -p $HOME/.cache/pip3

  pip3 install -r requirements.txt --cache-dir $HOME/.cache/pip3
  npm install && cd app && npm install && cd ..  # Hack until instapp-app-deps works on travis

  cd server && python3 -m nose -s --logging-level WARNING && cd ..

  npm i -g mocha
  npm run unit-renderer
  npm run unit-main
  npm run release:posix
  # TODO(Ahmed): figure out how to get these working w/new structure
  #  npm run e2e
  ls dist/*
  ls releases

  echo "Creating python virtualenv"
  # TODO(Ahmed): Run create env test script in create_env dir!!!
  # python3 scripts/create_env.py
  # cd env-dist && ../scripts/test_env.sh && cd ..
}

execute_mac ()
{
  if [ "$1" == "pre-install" ]; then
    export HOMEBREW_CACHE=$HOME/.cache/our-brew
    uname -a
    python --version
    python -c "import struct; print(struct.calcsize('P') * 8)"

    # Update brew
    brew update

    # Install node.js
    brew install nvm
    mkdir -p ~/.nvm && export NVM_DIR=~/.nvm && source $(brew --prefix nvm)/nvm.sh && nvm alias default 6.0.0
    echo "$(brew --prefix nvm)/nvm.sh" >> ~/.bashrc
    nvm install 6.0.0
    nvm use 6.0.0
    node --version
    npm --version

    # NOTE(ahmed): We might not need python 3 explicit installation any more
    brew install scripts/ot_python3.rb
    python3 --version
    python3 -c "import struct; print(struct.calcsize('P') * 8)"
    python --version
    echo $PATH

    # Install Python packages (built with Python 3)
    pip3 install pyinstaller
    pyinstaller --version
  fi

  if [ "$1" == "install" ]; then
    run_install "mac"
  fi
}

execute_linux ()
{
  if [ "$1" == "pre-install" ]; then
    curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

    nvm install 6.0.0
    nvm use 6.0.0
    node --version
    npm --version
    ls -la ~/virtualenv/python2.7/bin/
    npm config set python ~/virtualenv/python2.7/bin/python
    echo "npm's python is $(npm config get python)"
    # if [ "$1" == "linux" ]; then
      # export DISPLAY=':99.0'
      # Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    # fi

    # sudo apt-get install g++
    # sudo apt-get install gcc
    # sudo apt-get install python3-pip
    # sudo apt-get install icnsutils # electron-builder dependency
    # sudo apt-get install graphicsmagick # electron-builder dependency
    # sudo apt-get install xvfb

    export PATH=$PATH:$(pwd)/node_modules/.bin/
  fi

  if [ "$1" == "install" ]; then
    run_install "linux"
  fi
}

os="$(uname)"

if [ "$os" = "Darwin" ]; then
  execute_mac $1
fi

if [ "$os" = "Linux" ]; then
    execute_linux $1
fi
