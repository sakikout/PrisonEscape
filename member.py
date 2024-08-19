

class Member:
    def __init__(self, name, coordinates, color='GREEN'):
        self.name = name
        self.coordinates = coordinates
        self.color = color

    def getCoordinates(self):
        return self.coordinates
    
    def getName(self):
        return self.name
    
    def getColor(self):
        return self.color
    
    def setName(self, name):
        self.name = name

    def setCoordinate(self, coordinates):
        self.coordinates = coordinates

    def setColor(self, color):
        self.color = color