config = {
    "version": "0.0.0"
}

devices = {
    # example device
    0: {  # device_id
        "account": {  # device auth info
            "id": 1,
            "password": "mg3*#G,v{8$J"
        },
        "commands": [  # commands to start when it get it
            {
                "type": "start",  #
                "programId": 1,
                "configuration": {
                    # ...
                }
            },
            {
                "type": "stop",  #
                "programId": 1
            }
        ],
        "processInfo": {  # info of some started processes
            1: {  # processId
                "programId": 1,
                "out": ""  # what process output
            }            
        },
        "sessionID": "",
        "sessionIDDate": 0
    }
}

clients = {
    "admin": {
        "password": "admin",
        "sessionID": ""
    }
}

programInfo = {
    1: {
        "name": "back",
        "configurationForm": []  # data in form that needs to input
    }
}