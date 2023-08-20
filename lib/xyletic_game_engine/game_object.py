from xyletic_game_engine.vector_two import Vector2
from xyletic_game_engine.collision_rectangle import CollisionRectangle

class GameObject:
    def __init__(self, x, y, width, height, sprite):
        self.sprite = sprite
        self.collision_box = CollisionRectangle(x, y, width, height)
        # Other common properties

    @property
    def position(self):
        return Vector2(self.collision_box.x, self.collision_box.y)

    def update(self):
        pass

    def check_collision(self, other_object):
        return (self.collision_box.x < other_object.collision_box.x + other_object.collision_box.width and
                self.collision_box.x + self.collision_box.width > other_object.collision_box.x and
                self.collision_box.y < other_object.collision_box.y + other_object.collision_box.height and
                self.collision_box.y + self.collision_box.height > other_object.collision_box.y)
    
    def draw(self):
        #self.sprite.x = round(self.collision_box.x)
        #self.sprite.y = round(self.collision_box.y)
        pass