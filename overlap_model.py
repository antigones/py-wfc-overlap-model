import random as rd
import numpy as np
from copy import deepcopy



class OverlapModel:

    def __init__(self, size, rules):
        self.size = size
        self.rules = rules
        self.matrix = [[set(self.rules.keys()) for _ in range(self.size)] for _ in range(self.size)]
        self.entropies = {(x,y):self.shannon_entropy(self.matrix[x][y]) for x in range(self.size) for y in range(self.size)}
        self.steps = list()
        #self.stats = list()

    def check_finished(self):
        return all(e == 1 for e in self.entropies.values())
    
    def shannon_entropy(self,tile):
        # number of allowed patterns
        # weights = [self.weights[x] for x in tile]
        # entropy = np.log(np.sum(weights)) - (np.sum(weights * np.log(weights)) / np.sum(weights))
        return len(tile)
        #return entropy
    
    def propagate(self, x, y):
        in_wave = set()
        in_wave.add((x,y))

       
        while len(in_wave) > 0:
            to_visit_x, to_visit_y = in_wave.pop()
            neighbours = self.get_neighbours(to_visit_x, to_visit_y, self.size, self.size)
            for neighbour in neighbours:
                nx,ny = neighbour
                # propagate by pushing compatible tiles to all neighbours
                ammissible_values_for_neighbours = set()
                for elm in self.matrix[to_visit_x][to_visit_y]:
                    tile_rules = self.rules[elm]
                    rx,ry = nx-to_visit_x,ny-to_visit_y
                    if (rx,ry) in tile_rules.keys():
                        ammissible_values_for_neighbours=ammissible_values_for_neighbours.union(tile_rules[(rx,ry)])
                if len(ammissible_values_for_neighbours) == 0:
                    raise Exception('Something really strange happened here')
                intsx: set = self.matrix[nx][ny].intersection(ammissible_values_for_neighbours)
                if len(intsx) == 0:
                    raise Exception('Could not collapse!')
                if intsx != self.matrix[nx][ny]:
                    in_wave.add((nx,ny)) # only queue changed tiles

                self.matrix[nx][ny] = intsx
                self.entropies[(nx,ny)] = self.shannon_entropy(self.matrix[nx][ny])
                
    def choose_tile_value(self, tile):
        x, y = tile
        tile_set = self.matrix[x][y]
        #chosen_values = rd.choices(population=list(tile_set),k=1)
        #chosen_value = chosen_values[0]
        chosen_value = rd.choice(list(tile_set))
        return chosen_value

    def get_neighbours(self,i,j,height,width):
        return [(x,y) for x, y in [
                (i-1, j),   # n
                (i, j-1),   # w
                (i+1, j),   # s
                (i, j+1),   # e
            ]
        if 0 <= x < width and 0 <= y < height]
    
    def solve(self):
        self.stats = list()
        i = 0
        while not self.check_finished():
            #self.steps.append(deepcopy(self.matrix))
            #self.stats.append((i, sum(1 for e in self.entropies.values() if e == 0))) # iteration, # collapsed tiles
            # micro-change entropies
            not_visited_entropies = {k:v-(rd.random() / 1000) for k,v in self.entropies.items() if v > 1}
            min_entropy_tile = min(not_visited_entropies, key=not_visited_entropies.get)
            min_x, min_y = min_entropy_tile
            chosen_elm = self.choose_tile_value(min_entropy_tile)
            self.matrix[min_x][min_y] = {chosen_elm}
            self.entropies[(min_x,min_y)] = self.shannon_entropy(self.matrix[min_x][min_y])
            try:
                self.propagate(min_x, min_y)
            except:
                return False, self.matrix, self.steps, self.stats
            i+=1
        
        self.steps.append(deepcopy(self.matrix))
        # self.stats.append((i, sum(1 for e in self.entropies.values() if e == 0))) # iteration, # collapsed tiles
        return True, self.matrix, self.steps