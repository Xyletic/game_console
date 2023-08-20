from xyletic_game_engine.vector_two import Vector2
import math

class MotionVector(Vector2):
    def __init__(self, speed=0, direction_angle=0):
        super().__init__()
        self.speed = speed
        self.max_speed = 0
        self.acceleration = 0
        self.direction_angle = direction_angle  # Now in degrees
        self.update_velocity()

    def update_velocity(self):
        direction_vector = Vector2(math.cos(math.radians(self.direction_angle)), math.sin(math.radians(self.direction_angle)))
        direction_vector *= self.speed
        self.x = direction_vector.x
        self.y = direction_vector.y

    def set_speed(self, speed):
        self.speed = speed
        self.update_velocity()

    def set_direction(self, direction_angle):
        self.direction_angle = direction_angle  # Stored in degrees
        self.update_velocity()

    def set_acceleration(self, acceleration, max_speed):
        self.acceleration = acceleration
        self.max_speed = max_speed
    
    def accelerate(self):
        if self.speed >= self.max_speed:
            return
        #  set speed to speed + acceleration or max speed, whichever is smaller
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        self.update_velocity()
    
    def decelerate(self):
        if self.speed <= 0:
            return
        #  set speed to speed - acceleration or 0, whichever is larger
        self.speed = max(self.speed - self.acceleration, 0)
        self.update_velocity()