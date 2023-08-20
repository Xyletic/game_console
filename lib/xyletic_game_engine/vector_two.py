import math

class Vector2:
    def ZERO():
        return Vector2(0, 0)
    
    def __init__(self, x : float = 0, y : float = 0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5

    def normalize(self):
        magnitude = self.magnitude()
        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude

    def distance_to(self, other):
        return (self - other).magnitude()
    
    def angle_to(self, other):
        return math.atan2(other.y - self.y, other.x - self.x)
    
