# Some game rules

class gameobject:
    id=-1
    type = ""
    health = 0
    action = ""
    x =-1
    y=-1

Objects= ['PLAYER','MONSTER','STONE','BIGSTONE','BULLET','BOMB']
Commands=['PLANTBOMB','FIREBULLET']

MaxSpeed = {'PLAYER' : 3,
            'MONSTER' : 3,
            'STONE': 0,
            'BIGSTONE': 0,
            'BULLET' :10}

#Every object is a square and size is the length of one side

Size = {'PLAYER' : 30,
        'MONSTER': 30,
        'STONE': 30,
        'BIGSTONE':75,
        'BULLET':1,
        'BOMB':2,
        'BOMBRADIUS':75}

