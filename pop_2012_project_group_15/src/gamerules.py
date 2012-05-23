# Some game rules

class gameobject:
    id=-1
    type = ""
    health = 0
    action = ""
    x =-1
    y=-1

MaxSpeed = {'PLAYER' : 6,
            'MONSTER' : 3,
            'STONE': 0,
            'BIGSTONE': 0,
            'BULLET' :10}

#Every object is a square and size is the length of one side

Size = {'PLAYER' : 2,
        'MONSTER': 10,
        'STONE': 3,
        'BIGSTONE':16,
        'BULLET':1}

