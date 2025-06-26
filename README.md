# mcc-ws

## Introduction

MCC board JSON web service to allow web pages and HTTP clients to interact with MCC board

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
