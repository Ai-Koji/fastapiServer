config = {
    "version": "0.0.0"
    }

# }}
devices = {
    ### example device ###
    0: { # device_id
        "account": { ### device auth info
            "id": 1,
            "password": "mg3*#G,v{8$J"
        },
        "commands": [ ### commands to start when it get it
            {
                "type": "start", #
                "programId": 1,
                "configuration": {
                    # ...
                }
            },
            {
                "type": "stop", #
                "programId": 1
            }
        ],
        "processInfo": [ ### info of some started processes
            1: { # processId
                "programId": 1,
                "out": "" # what process output
            }            
        ]
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

programInfo = {
    # id: {
    #     "name": "backd",
    #     "configurationForm": [ # data in form that needs to input
            # 1: {
            #     "name": "host"
            #     "infotype": "int"
            # }
    #     ]
    # }
    1: {
        "name": "back",
        "configurationForm": [ # data in form that needs to input
            # TODO: add form here
        ]
    }
}