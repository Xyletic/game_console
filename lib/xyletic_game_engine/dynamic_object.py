from xyletic_game_engine.motion_vector import MotionVector
from xyletic_game_engine.game_object import GameObject

class DynamicObject(GameObject):
    def __init__(self, x, y, width, height, sprite, speed=0, direction_angle=0):
        super().__init__(x, y, width, height, sprite)
        self.start_speed = speed
        self.start_direction_angle = direction_angle
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

        # Normal collision check (or other narrow phase checks if needed)
        return super().check_collision(other_object) or self.check_advanced_collision(other_object)
    
    # Check if we have "jumped" over the other object from our previous position to our current position. Our velocity could be faster than the size of the objects.
    def check_advanced_collision(self, other_object):
        # Determine the number of steps based on the greater velocity component
        steps = int(max(abs(self.velocity.x) / self.collision_box.width, abs(self.velocity.y) / self.collision_box.height))
        if(steps <= 0):
            return False
        # Incremental steps for x and y
        step_x = self.velocity.x / steps
        step_y = self.velocity.y / steps

        # Temporary positions
        temp_position_x = self.collision_box.x
        temp_position_y = self.collision_box.y

        # Check collision at each step
        for _ in range(steps + 1):
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

    def reset(self):
        super().reset()
        self.velocity = MotionVector(self.start_speed, self.start_direction_angle)