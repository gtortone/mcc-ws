#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.realpath('/opt/mcc-board-cli'))
from lib.MCCBoard import MCCBoard

from flask import Flask, request, send_from_directory
from flask_json import FlaskJSON, JsonError, json_response, as_json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

schema = {
    "type": "object",
    "properties": {
        "command": {
            "enum": ["power", "status"]
        },
    },

    "required": ["command"],
   
    "if": {
      "properties": {
         "command": { "const": "power" }
      }
    },
    "then": {
      "properties": {
         "ports": {
            "type": "array",
            "items": {"type": "number", "minimum": 0, "maximum": 7},
            "minItems": 1,
         },
         "value": {
            "type": "number",
            "minimum": 0,
            "maximum": 1, 
         }
      },
      "required": ["ports", "value"],
    },
}

mcc = MCCBoard()

app = Flask(__name__)
FlaskJSON(app)

@app.route("/")
def send_homepage():
   return send_from_directory('static', 'index.html')

@app.route("/<path:path>")
def send_static(path):
   return send_from_directory('static', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route("/api", methods=["POST"])
def handle_request():
   data = request.get_json(force=True)

   try:
      validate(instance=data, schema=schema)
   except ValidationError as e:
      raise JsonError(error=e.message)

   cmd = data["command"]

   if cmd == "power":
      response = {}
      response["ports"] = []
      for p in data["ports"]:
         if data["value"] == 0:
            mcc.sw.port_off(p)
         else:
            mcc.sw.port_on(p)
         response["ports"].append({
            "id": p, 
            "status": 'on' if mcc.sw.port_status(p) else 'off' 
         })
         
   if cmd == "status":
      response = {}
      response["controller"] = []
      response["ports"] = []
      response["sfp"] = []

      for c in range(0,2):
         d = {"id": c}
         d.update(mcc.sw.poectrl[c].as_dict())
         response["controller"].append(d)

      for p in range(0,8):
         response["ports"].append(mcc.sw.as_dict(p))

      if mcc.sfp0.is_available():
         d = {"id": 0}
         d.update(mcc.sfp0.as_dict())
         response["sfp"].append(d)

      if mcc.sfp1.is_available():
         d = {"id": 1}
         d.update(mcc.sfp1.as_dict())
         response["sfp"].append(d)

   return json_response(result=response)
      
if __name__ == "__main__":
   app.run()
