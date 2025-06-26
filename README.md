
# mcc-ws

## Introduction

MCC board JSON web service allows web pages and HTTP clients to interact with MCC board

## Description

mcc-ws accepts two JSON commands:

* power
* status

### 'power' command

A list of POE ports can be provided in `ports` key to power on or power off using `value` key.

request:

```json
{
  "command": "power",
  "ports": [0,1,2,3,4,5],
  "value": 1
}
```

response:

```json
{
  "result":
  {
    "ports":[
      {"id":0,"status":"on"},
      {"id":1,"status":"on"},
      {"id":2,"status":"on"},
      {"id":3,"status":"on"},
      {"id":4,"status":"on"},
      {"id":5,"status":"on"}
    ]
  },
  "status":200
}
```


### 'status' command

Full overview on POE controllers, switch ports and SFPs status is returned.

request:

```json
{
  "command": "status"
}

```

response:

```json
{
  "result":
  {
    "controller":[
      {"id":0,"temperature":46.5,"voltage":51.82},
      {"id":1,"temperature":45.2,"voltage":51.8}
    ],
    "ports":[
      {"class":"unknown","current":0.0,"detection":"open circuit","id":0,"power":0.0,"status":"on","voltage":0.0},
      {"class":"unknown","current":0.0,"detection":"open circuit","id":1,"power":0.0,"status":"on","voltage":0.0},
      {"class":"unknown","current":0.0,"detection":"open circuit","id":2,"power":0.0,"status":"on","voltage":0.0},
      {"class":"unknown","current":0.0,"detection":"open circuit","id":3,"power":0.0,"status":"on","voltage":0.0},
      {"class":"unknown","current":0.0,"detection":"open circuit","id":4,"power":0.0,"status":"on","voltage":0.0},
      {"class":"unknown","current":0.0,"detection":"open circuit","id":5,"power":0.0,"status":"on","voltage":0.0},
      {"class":"Class 0","current":18.25,"detection":"RGOOD","id":6,"power":0.95,"status":"on","voltage":51.84},
      {"class":"Class 0","current":32.35,"detection":"RGOOD","id":7,"power":1.68,"status":"on","voltage":51.84}
    ],
    "sfp":[
      {"datecode":"200818","id":0,"model":"UF-RJ45-1G      1.0","serial":"X20092807618","vendor":"UBNT"}
    ]
  },
"status":200
}
```

## Usage

Best friend for a web service is a JavaScript client, but if you are on a shell ```curl``` is a great alternative

```bash
curl --header "Content-Type: application/json"  --request POST --data '{"command": "power", "ports": [0,1,2,3,4,5], "value": 1}' http://mcc.gmh:8000/api
```


```bash
curl --header "Content-Type: application/json"  --request POST --data '{"command": "status"}' http://mcc.gmh:8000/api

```

