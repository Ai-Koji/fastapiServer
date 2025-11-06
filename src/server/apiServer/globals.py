config = {
    "version": "0.0.0"
    }

# {device_id: {
    # account: {
        # id: id
        # password: password
    # },
    # commands: [
        # {
            #  "type": "start",
            #  "programId": 1 
        # },
        # {
            #  "type": "stop",
            #  "ProcessId": 123
        # } 
    # ] 
    # "sessionID": session_id,
    # "sessionIDDate": time.time()
# }}
devices = {
    1: {
        "account": {
            "id": 1,
            "password": "mg3*#G,v{8$J"
        },
        "commands": [
            {
                "type": "start",
                "programId": 1
            }
        ],
        "sessionID": "",
        "sessionIDDate": 0
    }
}

# {
    # "login": {
        # "password",
        # "sessionId",
        # "sessionIDDate"
    # }
# }
clients = {
    "admin": {
        "password": "admin",
        "sessionId": ""
    }
}

