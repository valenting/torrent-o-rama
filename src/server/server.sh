#!/bin/bash
. $HOME/.pythonbrew/etc/bashrc
pythonbrew switch 2.7.1
python Server.py &> /dev/null
