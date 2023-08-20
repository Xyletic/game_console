from xyletic_game_engine.motion_vector import MotionVector
from xyletic_game_engine.game_object import GameObject

class DynamicObject(GameObject):
    def __init__(self, x, y, width, height, sprite, speed=0, direction_angle=0):
        super().__init__(x, y, width, height, sprite)
        self.velocity = MotionVector(speed, direction_angle)

    def update(self, delta_time):
        super().update()
        displacement = self.velocity #* delta_time
        self.collision_box.x += displacement.x
        self.collision_box.y += displacement.y
        # Other update logic

    # Override - check if we collided with the other object or we would have collided with the other object from our previous position to our current position
    def check_collision(self, other_object):
        # Check if object is None
        if other_object is None:
            return False
        
        # Calculate the bounding area based on inverted velocity and size
        bounding_x = self.collision_box.x - min(0, self.velocity.x)
        bounding_y = self.collision_box.y - min(0, self.velocity.y)
        bounding_width = self.collision_box.width + abs(self.velocity.x)
        bounding_height = self.collision_box.height + abs(self.velocity.y)

        # Check if the other object is outside the bounding area
        if (other_object.collision_box.x + other_object.collision_box.width < bounding_x or
            other_object.collision_box.x > bounding_x + bounding_width or
            other_object.collision_box.y + other_object.collision_box.height < bounding_y or
            other_object.collision_box.y > bounding_y + bounding_height):
            return False

        # Normal collision check (or other narrow phase checks if needed)
        return super().check_collision(other_object) or self.check_advanced_collision(other_object)
    
    # Check if we have "jumped" over the other object from our previous position to our current position. Our velocity could be faster than the size of the objects.
    def check_advanced_collision(self, other_object):
        # Determine the number of steps based on the greater velocity component
        steps = int(max(abs(self.velocity.x) / self.collision_box.width, abs(self.velocity.y) / self.collision_box.height))

        # Incremental steps for x and y
        step_x = self.velocity.x / steps
        step_y = self.velocity.y / steps

        # Temporary positions
        temp_position_x = self.collision_box.x
        temp_position_y = self.collision_box.y

        # Check collision at each step
        for step in range(steps + 1):
            # Check collision at the temporary position
            if (temp_position_x < other_object.collision_box.x + other_object.collision_box.width and
                temp_position_x + self.collision_box.width > other_object.collision_box.x and
                temp_position_y < other_object.collision_box.y + other_object.collision_box.height and
                temp_position_y + self.collision_box.height > other_object.collision_box.y):
                return True

            # Increment the temporary positions by the step sizes
            temp_position_x += step_x
            temp_position_y += step_y

        return False
    
    def draw(self):
        self.sprite.x = round(self.collision_box.x)
        self.sprite.y = round(self.collision_box.y)
        #super().draw()
        # Other draw logic
        pass