#!/bin/bash

gunicorn --chdir /opt/mcc-ws -b 0.0.0.0 mcc-ws:app
