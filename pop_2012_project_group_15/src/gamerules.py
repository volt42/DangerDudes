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

Size = {'PLAYER' : 50,
        'MONSTER': 50,
        'STONE': 50,
        'BIGSTONE':100,
        'BULLET':1,
        'BOMB':5,
        'BOMBRADIUS':150}

