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
            "enum": ["power", "status", "setoption"]
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

    "if": {
      "properties": {
         "command": { "const": "setoption" }
      }
    },
    "then": {
      "properties": {
         "option": {
            "type": "string",
            "enum": ["keep_power"], 
            "minItems": 1,
         },
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
      "required": ["option", "ports", "value"],
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

   if cmd == "setoption":
      response = {}
      response["ports"] = []
      if data["option"] == "keep_power":
         for p in data["ports"]:
            if data["value"] == 0:
               mcc.sw.port_set_keep_power(p, False)
            else:
               mcc.sw.port_set_keep_power(p, True)
            response["ports"].append({
               "id": p,
               "option": data["option"],
               "value": data["value"]
            })
         
   if cmd == "status":
      response = {}
      response["controller"] = []
      response["ports"] = []
      response["sfp"] = []

      response["version"] = mcc.version

      for c in range(0,2):
         d = {"id": c}
         d.update(mcc.sw.poectrl[c].as_dict())
         response["controller"].append(d)

      for p in range(0,8):
         response["ports"].append(mcc.sw.as_dict(p))

      for i, el in enumerate(mcc.sfp):
         #if mcc.sfp[i].is_available():
         d = {"id": i}
         d.update(mcc.sfp[i].as_dict())
         response["sfp"].append(d)

      response["host"] = {}
      response["host"]["cpu"] = []
      response["host"]["memory"] = []
      response["host"]["network"] = []
      response["board"] = {}
      response["board"]["fpga"] = []

      d = {}
      d["version"] = mcc.fpga.bitstream_version()
      response["board"]["fpga"].append(d) 

      for i, value in enumerate(mcc.host.get_cpu_status()):
         d = {}
         d["usage"] = value
         response["host"]["cpu"].append(d)

      mem = mcc.host.get_memory_status()
      d = {}
      d["total"] = round(mem.total / 1e6, 0)
      d["available"] = round(mem.available / 1e6, 0)
      d["available_p"] = round(mem.available/mem.total*100, 2)
      d["used"] = round(mem.used/ 1e6, 0)
      d["used_p"] = round(mem.used/mem.total*100, 2)
      response["host"]["memory"].append(d)

      for intf, el in mcc.host.get_network_status().items():
         d = {}
         d["interface"] = intf
         d["rx_speed"] = el["rx_speed"]
         d["tx_speed"] = el["tx_speed"]
         d["mac"] = el["mac"]
         d["ip"] = el["ip"]
         response["host"]["network"].append(d)

      if mcc.version == 2:

         response["board"]["rails"] = []
         response["board"]["sensors"] = []

         for i, el in enumerate(mcc.boardmon):
            d = {}
            d = el.as_dict()
            response["board"]["rails"].append(d)

         for i, el in enumerate(mcc.sfpmon):
            d = {}
            d = el.as_dict()
            response["board"]["rails"].append(d)

         d = {}
         d["label"] = "SHT40"
         d["temperature"] = round(mcc.sht40.read()[0], 2)
         d["humidity"] = round(mcc.sht40.read()[1], 2)
         response["board"]["sensors"].append(d)

         d = {}
         d["label"] = "BMP585"
         d["temperature"] = round(mcc.bmp585.read()[0], 2)
         d["pressure"] = round(mcc.bmp585.read()[1]/100, 2)
         response["board"]["sensors"].append(d)


   return json_response(result=response)
      
if __name__ == "__main__":
   app.run()
