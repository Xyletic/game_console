# Create a class used for navigation within the game.
class Node:
    def __init__(self, x, y, g_cost=0, h_cost=0):
        self.x = x
        self.y = y
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = self.g_cost + self.h_cost
        self.parent = None
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    
class Navigation:
    def __init__(self, grid_spacing, game_area):
        self.grid_spacing = grid_spacing
        self.game_area = game_area
    
    def find_path(self, origin, goal, wall_positions):
        self.closed_set = set([(w.sprite.x, w.sprite.y) for w in wall_positions])
        open_set = {(origin.x, origin.y): Node(origin.x, origin.y)}
        self.goal = goal
        
        while open_set:
            current = min(open_set.values(), key=lambda o: o.f_cost)
            # if current is goal or a maximum of 50 items within the open set, return path
            if current.x == goal.x and current.y == goal.y or len(open_set) > 20:
                self.closed_set = None
                return self.reconstruct_path(current)
            
            open_set.pop((current.x, current.y))
            self.closed_set.add((current.x, current.y))
            
            for n in self.get_neighbors(current):
                if n in self.closed_set:
                    continue
                
                if n not in open_set:
                    neighbor = Node(n[0], n[1])
                    neighbor.g_cost = current.g_cost + self.distance(current, neighbor)
                    neighbor.h_cost = self.distance(neighbor, Node(goal.x, goal.y))
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current
                    open_set[(n)] = neighbor
            #print(len(open_set))
        return None
    
    def reconstruct_path(self, end_node):
        path = []
        current = end_node
        while current is not None:
            parent = current.parent
            if parent is not None:
                if parent.x == current.x:
                    if parent.y > current.y:
                        path.append(270)
                    else:
                        path.append(90)
                else:
                    if parent.x > current.x:
                        path.append(180)
                    else:
                        path.append(0)
            current = current.parent
        return list(reversed(path))
    

    def get_neighbors(self, node):
        neighbors = []
        for dx, dy in [(self.grid_spacing, 0), (0, self.grid_spacing), (-self.grid_spacing, 0), (0, -self.grid_spacing)]:
            x, y = node.x + dx, node.y + dy
            if self.is_valid_position(x, y):
                neighbors.append((x, y))
        if(len(neighbors) < 3):
            return neighbors
        else:
            # find the cheapest h_cost neighbor and return only that one
            neighbor = neighbors[0]
            neighbor_h_cost = abs(neighbor[0] - self.goal.x) + abs(neighbor[1] - self.goal.y)
            for n in neighbors:
                h_cost = abs(n[0] - self.goal.x) + abs(n[1] - self.goal.y)
                if h_cost < neighbor_h_cost:
                    neighbor = n
                    neighbor_h_cost = h_cost
            return [neighbor]

    
    def get_neighbor_coords(self, node):
        neighbors = []
        for dx, dy in [(self.grid_spacing, 0), (0, self.grid_spacing), (-self.grid_spacing, 0), (0, -self.grid_spacing)]:
            x, y = node.x + dx, node.y + dy
            if self.is_valid_position(x, y):
                neighbors.append((x, y))
        return neighbors
    
    def is_valid_position(self, x, y):
        #check if position is within game area and not in closed set
        if (x, y) in self.closed_set:
            return False
        return self.game_area.x <= x <= self.game_area.x + self.game_area.width and self.game_area.y <= y <= self.game_area.y + self.game_area.height
    
    def distance(self, node1, node2):
        return (abs(node1.x - node2.x) + abs(node1.y - node2.y))