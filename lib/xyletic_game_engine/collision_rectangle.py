from xyletic_game_engine.vector_two import Vector2

class CollisionRectangle(Vector2):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        super().__init__(x, y)