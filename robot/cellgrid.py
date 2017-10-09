__author__ = 'keithd'

from prims1 import *

# Index offsets for neighborhoods of sizes 4 and 8.  Both begin in the north and move clockwise.  The grid has
# origin (0,0) in the upper left hand corner.  Holding the first coordinate constant produces a ROW in 2d.
#  So point (3,7) is in the 4th row (from the top) and 8th column (going left to right).

_hood4_offsets_ = [(-1,0),(0,1),(1,0),(0,-1)]
_hood8_offsets_ = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
_direction_pairs_ = {'N': (-1,0), 'NE': (-1,1), 'E': (0,1), 'SE': (1,1), 'S': (1,0),
                     'SW': (1,-1), 'W': (0,-1), 'NW': (-1,-1)}

class Cellgrid():

    def __init__(self,numx,numy,celltype='Cell'):
        self.dims = (numx,numy)
        self.celltype = celltype
        self.toroidal = True # If true => wrap-around on sides and top/bottom
        self.create_grid()

    def xmax(self): return self.dims[0]
    def ymax(self): return self.dims[1]

    def create_grid(self):
        self.grid = [[eval(self.celltype)(x,y,self) for y in range(self.dims[1])] for x in range(self.dims[0])]

    def get_cell(self,x,y): return self.grid[x][y]
    # This version accounts for wrap-around
    def get_cell2(self,x,y):
        xmax,ymax = self.dims
        if not(self.toroidal) and (not(0 <= x < xmax) or not(0 <= y < ymax)):
            return None
        else:
            x = x % xmax; y = y % ymax  # Use modulo to do wrap-around
            return self.get_cell(x,y)

    def get_cell_contents(self,x,y): return self.get_cell(x,y).get_contents()
    def set_cell_contents(self,x,y,c): self.get_cell(x,y).set_contents(c)

    def get_cell_contents2(self,x,y):
        c = self.get_cell2(x,y)
        return c.get_contents() if c else None

    # Get the 4-cell neighborhood: North, East, South, West
    def get_hood4(self,x,y): return [self.get_cell2(x+p[0],y+p[1]) for p in _hood4_offsets_]
    def get_hood4_vals(self,x,y): return [self.get_cell_contents2(x+p[0],y+p[1]) for p in _hood4_offsets_]

    # Get the 8-cell neighborhood: N,NE,E,SE,S,SW,W,NW
    def get_hood8(self,x,y): return [self.get_cell2(x+p[0],y+p[1]) for p in _hood8_offsets_]
    def get_hood8_vals(self,x,y): return [self.get_cell_contents2(x+p[0],y+p[1]) for p in _hood8_offsets_]

    def randfill(self,choices):
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                self.set_cell_contents(x,y,randelem(choices))

    # This prints rows, beginning with all cells with x = 0 across the TOP
    def pp(self):
        for x in range(self.dims[0]):
            row = ''
            for y in range(self.dims[1]):
                row += str(self.get_cell_contents(x,y)) + ' '
            print(row)

# ************** Cell *************************

class Cell():

    def __init__(self,x,y,grid,contents = None):
        self.x = x; self.y = y
        self.grid = grid
        self.contents = contents

    def get_hood4(self): return self.grid.get_hood4(self.x,self.y)
    def get_hood8(self): return self.grid.get_hood8(self.x,self.y)

    # Calc direction vector from one cell to another
    def cell_dir(self,cell2):
        xmax,ymax = self.grid.dims
        return ((cell2.x - self.x) % xmax, (cell2.y - self.y) % ymax)

    def get_contents(self): return self.contents
    def set_contents(self,c): self.contents = c

# ****** Auxiliary Functions ******

# pair = (dx, dy), a 2d direction vector
def opposite_dir(pair): return (-pair[0],-pair[1])
def cw_tangent_dir(pair): return  (pair[1],-pair[0])  # Clockwise tangent (90 degrees)
def ccw_tangent_dir(pair): return (-pair[1],pair[0])  # Counter clockwise tangent (90 degrees)

