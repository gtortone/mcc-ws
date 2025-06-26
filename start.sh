#!/bin/bash

gunicorn --chdir /opt/mcc-ws -w 4 -b 0.0.0.0 mcc-ws:app
