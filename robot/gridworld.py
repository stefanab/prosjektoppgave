__author__ = 'keithd'
import bbcon as bbc # Behavior-based controller
import cellgrid as cg
from prims1 import *
from fileops import *

_grid0_path = "./Grids/grid1.grd"

# *************** Gridworld ********************

# By choosing the agenttype, celltype and con(troller)type, you can run all sorts of different
# scenarios in the basic Gridworld framework.

class Gridworld(cg.Cellgrid):

    def __init__(self,x,y,act = 1,atype="Agent",celltype='Gcell',contype='GridCon',fid=None,stoch=False):
        self.agents =n_of(act,(lambda : eval(atype)(contype=contype,stoch=stoch)))
        self.active_agents = []
        self.gridfile = None
        cg.Cellgrid.__init__(self,x,y,celltype=celltype)
        if fid: self.file_load_grid(fid)

    # I seem to need a local copy of this method, since cellgrid.py doesn't import gridworld.py and thus
    # doesn't recognize the Gcell class.  So this gets called by Cellgrid.__init__
    def create_grid(self):
        self.grid = [[eval(self.celltype)(x,y,self) for y in range(self.dims[1])] for x in range(self.dims[0])]

    def file_load_grid(self,fname):
        self.gridfile = _grid0_path #build_default_file_path(fname,'grid')
        lines = load_file_lines(self.gridfile)
        for x in range(self.dims[0]):
            line = tokenize(lines[x])
            for y in range(self.dims[1]):
                self.set_cell_contents(x,y,line[y])

    def run_loop(self):
        self.active_agents = list(self.agents) # Shallow copy of the list
        while self.active_agents:
            self.run_one_timestep()
            self.pp()


    def run_one_timestep(self):
        inactives = []
        for a in self.active_agents:
            if not(a.run_one_timestep()):
             inactives.append(a)
        for ia in inactives: self.active_agents.remove(ia)

    # This prints rows, beginning with all cells with x = 0 across the TOP
    def pp(self):
        for x in range(self.dims[0]):
            row = ''
            for y in range(self.dims[1]):
                c = self.get_cell(x,y)
                s =  str(c.get_contents())
                s+= "@ " if c.agents else "  "
                row += s
            print(row)


# ******** Gcell **********

class Gcell(cg.Cell):

    def __init__(self,x,y,grid,contents = None):
        cg.Cell.__init__(self,x,y,grid,contents=contents)
        self.agents = [] # list of agents in the cell

    def add_agent(self,agent): self.agents.append(agent)
    def remove_agent(self,agent): self.agents.remove(agent)

# *************** Agent *********************
# Agents don't have an explicit front or back, so all coordinates are allocentric (N,S,E,W,NE,SE,SW,NW) as opposed to
# egocentric (front,back,left,right,etc.)  However, the "dir" slot of the agent indicates the current
# direction that it's moving...so if you assume that it always FACES the direction that it moves, then there is
# an implicit front/back to the agent.

class Agent():

    def __init__(self,contype='GridCon',stoch=False):
        self.cell = None  # Gridworld cell in which it resides
        self.active = True
        self.sensors = []
        self.motors = []
        self.dir = (1,1) # Direction that it's currently facing, as determined by previous move
        self.create_sensors()
        self.create_motors()
        self.controller = eval(contype)(self,stoch=stoch)

    def set_cell(self,c): self.cell = c
    def get_cell(self): return self.cell

    def get_dir(self):  return self.dir
    def set_dir(self,d): self.dir = d

    def add_sensor(self,s): self.sensors.append(s)
    def add_motor(self,m): self.motors.append(m)

    def create_sensors(self):
        for dir in cg._hood8_offsets_:
            self.add_sensor(Sensor(self,dir))

    def update_sensors(self):
        for s in self.sensors: s.update()
    def reset_sensors(self):
        for s in self.sensors: s.reset()

    def get_sensors(self): return self.sensors
    def get_motors(self): return self.motors

    # Produce all cells that the agent senses: the "sensed (neighbor)hood"
    def get_sensed_hood(self):
        c = self.cell; g = c.grid
        return [g.get_cell2(c.x+s.dir[0], c.y+s.dir[1]) for s in self.sensors]

    def create_motors(self):
        self.add_motor(Motor(0))
        self.add_motor(Motor(1))

    # Sensors are updated and reset by the controller, so there's no need to do it here.
    def run_one_timestep(self):
        self.active = self.controller.run_one_timestep()
        if self.active: self.move()
        return self.active

    def put_in_cell(self,cell):
        self.set_cell(cell)
        cell.add_agent(self)

    def move(self):
        dx = round(self.motors[0].get_value())
        dy = round(self.motors[1].get_value())
        c = self.cell
        c2 = c.grid.get_cell2(c.x+dx,c.y+dy)
        if c2:
            self.set_dir ((dx,dy))
            self.put_in_cell(c2)
            c.remove_agent(self)


# *************** Sensor ******************
# These are simple sensors that read the contents of cells in the agent's neighborhood.  The "dir" property of
# each sensor determines which neighbor cell to read.

class Sensor():

    def __init__(self,agent,dir):
        self.agent = agent
        self.dir = dir # direction from agent in allocentric coords, e.g. (-1,0) = north, (1,-1) = Southwest
        self.value = None
        self.updated = False

    def reset(self):
        self.updated = False
        self.value = None

    def get_value(self): return self.value

    def update(self):
        if not(self.updated):
            self.compute_value()
            self.updated = True

    def compute_value(self):
        dx,dy = self.dir
        c = self.agent.get_cell()
        self.value = c.grid.get_cell_contents2(c.x + dx , c.y + dy)

# **************** Motor *******************
# This simple object controls either the up-down or left-right movement of an agent.  Two motors combine to
# give the final movement direction of the agent.

class Motor():

    def __init__(self,axis):
        self.axis = axis # axis = 0 => vertical (1st dimension), axis = 1 => horizontal
        self.value = None # Legal values in real range [-1, 1] but are scaled to integers (-1,0,1) just prior to mvmt.

    def set_value(self,val): self.value = val
    def get_value(self): return self.value

# ******** GRIDCON (Gridworld Controller) *************
# Each agent should have one of these.

class GridCon(bbc.BBCon):

    def __init__(self,agent,tdur=0.5,stoch=False):
        bbc.BBCon.__init__(self,agent,tdur=tdur,stoch=stoch)
        self.configure()

    def init_sensobs_and_motobs(self):
        self.sensobs = [bbc.Sensob(s) for s in self.agent.get_sensors()]
        self.motobs = [bbc.Motob(m) for m in self.agent.get_motors()]

    # Create the appropriate sensobs and motobs
    def configure(self):
        self.init_sensobs_and_motobs()
        # Create the behaviors
        wanderer = Wander(self,pri=1)
        find_goal = Reach_Final_Goal(self,self.sensobs,target=9,pri=100)
        avoider = Avoid_Value(self,self.sensobs,target=5,pri=10)
        seek_goal = Seek_Value(self,self.sensobs,target=9,pri=50)
        seek_trail = Seek_Value(self,self.sensobs,target=1,pri=3)
        skirt_wall = Skirt_Value(self,self.sensobs,target=8,pri=2)
        limit_steps = bbc.Step_Limit_Halt(self,msteps=25,pri=100)
        self.behaviors = [wanderer,seek_trail,avoider,skirt_wall,limit_steps,seek_goal,find_goal]

# *********** GRIDCON2 ********************
# This controller has a trigger for it's goal-seeking behaviors: it has to see a 2 in a neighbor cell.

class GridCon2(GridCon):

    def __init__(self,agent,tdur=0.5,stoch=False):
        bbc.BBCon.__init__(self,agent,tdur=tdur,stoch=stoch)
        self.configure()

    def configure(self):
        self.init_sensobs_and_motobs()
        wander = Wander(self,pri=1)
        find_goal = Reach_Final_Goal(self,self.sensobs,target=9,trigger=2,act=False,pri=100)
        seek_goal = Seek_Value(self,self.sensobs,target=9,trigger=2,act=False,pri=50)
        seek_trail = Seek_Value(self,self.sensobs,target=1,pri=10)
        skirt_wall = Skirt_Value(self,self.sensobs,target=8,pri=1)
        limit_steps = bbc.Step_Limit_Halt(self,msteps=40,pri=100)
        self.behaviors = [wander, seek_trail, skirt_wall, limit_steps, seek_goal, find_goal]

# ******** SPECIAL BEHAVIORS FOR GRIDWORLD *************************************************

class Gridworld_Behavior(bbc.Behavior):

    def __init__(self): True

    def get_agent_cell(self): return self.bbcon.get_agent().get_cell()

# **** WANDER *******

class Wander(Gridworld_Behavior):

    def __init__(self,bbcon,sensobs=[],trigger=None,act=True,pri=1):
        bbc.Behavior.__init__(self,bbcon,sensobs=sensobs,act=act,pri=pri)
        self.trigger = trigger #Don't activate until this value seen.  Trigger = None => always active.


    def sense_and_act(self):
        self.set_motor_requests((n_of(2,(lambda : randelem([-1,0,1])))))
        self.set_match_degree(1)

class Value_Driven_Behavior(Gridworld_Behavior):

    def __init__(self,bbcon,sensobs=[],target=1,trigger=None,act=True,pri=1):
        bbc.Behavior.__init__(self,bbcon,sensobs=sensobs,act=act,pri=pri)
        self.target = target
        self.trigger = trigger


     # Relevant sensors are those having the target (or trigger) as their value.
    def relevant_sensobs(self,val=None):
        tval = val if val else self.target
        rs = []
        for s in self.sensobs:
            if s and s.get_value() == tval: rs.append(s)
        return rs

    def relevant_sensob_dirs(self,val=None):
        return [s.sensor.dir for s in self.relevant_sensobs(val=val)]

    # When there is more than one direction that has the behavior's target, then choose the one that
    # has the highest dot product with the agent's current direction (i.e., is most similar to the current
    # direction).  If there is exactly one direction, then ignore the agent's current direction.

    def best_biased_sensob_dir(self,val=None):
        def dot(d1,d2): return d1[0]*d2[0] + d1[1]*d2[1] # calc dot product of two vectors (of -1, 0, 1)
        adir = self.bbcon.get_agent().get_dir()  # current direction of the agent, which we'd like to stay close to.
        dirs = self.relevant_sensob_dirs(val=val)
        if dirs:
            best_dir = dirs[0];
            best_dot = dot(dirs[0],adir) if len(dirs) > 1 else 2
        for d in dirs[1:]:
            new_dot = dot(d,adir)
            if new_dot > best_dot:
                best_dot = new_dot; best_dir = d
        return [best_dir,best_dot*4] if dirs else [None,0]

    # This returns the average direction vector along with the number of relevant neighbors.
    def avg_relevant_sensob_dirs(self,val=None):
        dirs = self.relevant_sensob_dirs(val=val)
        dl = len(dirs)
        sumx = 0; sumy = 0
        for d in dirs:
            sumx += d[0]; sumy += d[1]
        return [(sumx/dl, sumy/dl), dl] if dirs else [None,0]

    # This finds the average vector dir from current cell to relevant sensed values (i.e., those with the target
    # value), modifies that vector (differently for each subclass), and then converts that into a motor request.
    # The match_degree is simply the fraction of sensors that exhibit the target value.

    def do_activation_test(self):
        cell = self.get_agent_cell()
        return True if (not(self.trigger) or self.relevant_sensobs(val=self.trigger)) else False

    def sense_and_act(self):
        #dir,count = self.avg_relevant_sensob_dirs(val=self.target)
        dir,count = self.best_biased_sensob_dir(val=self.target)
        if dir:
            newdir = self.modify_target_dir(dir)
            self.set_motor_requests(list(newdir))
            self.set_match_degree(count / 8)

    def modify_target_dir(self,dir): return self.round_target_dir(dir)
    def round_target_dir(self,dir): return (round(dir[0]), round(dir[1]))

# **** REACH_FINAL_GOAL ******
# Recognize that the agent is in the SAME cell as goal/target item.

class Reach_Final_Goal(Value_Driven_Behavior):

    def __init__(self,bbcon,sensobs=[],target=1,trigger=None,act=True,pri=1):
        Value_Driven_Behavior.__init__(self,bbcon,sensobs=sensobs,target=target,trigger=trigger,act=act,pri=pri)

    def sense_and_act(self):
        if self.target == self.get_agent_cell().get_contents():
            self.request_halt()
            self.set_match_degree(1.0)
        else:
            self.set_match_degree(0)

# **** SEEK_VALUE ************
# Move INTO cells with the target value

class Seek_Value(Value_Driven_Behavior):

    def __init__(self,bbcon,sensobs=[],target=1,trigger=None,act=True,pri=1):
        Value_Driven_Behavior.__init__(self,bbcon,sensobs=sensobs,target=target,trigger=trigger,act=act,pri=pri)

# ***** AVOID_VALUE *********
# Move AWAY from (opposite) cells with the target value

class Avoid_Value(Value_Driven_Behavior):

    def __init__(self,bbcon,sensobs=[],target=1,trigger=None,act=True,pri=1):
        Value_Driven_Behavior.__init__(self,bbcon,sensobs=sensobs,target=target,trigger=trigger,act=act,pri=pri)


    def modify_target_dir(self,dir): return self.round_target_dir(cg.opposite_dir(dir))

# ******** SKIRT_VALUE ******
# Move TANGENTIAL to (along) cells with the target value.

class Skirt_Value(Value_Driven_Behavior):

    def __init__(self,bbcon,sensobs=[],target=1,trigger=None,act=True,pri=1):
        Value_Driven_Behavior.__init__(self,bbcon,sensobs=sensobs,target=target,trigger=trigger,act=act,pri=pri)

    def modify_target_dir(self,dir): return self.round_target_dir(cg.cw_tangent_dir(dir))


# ********** MAIN *******************

def gtest(x=10,y=10,fid='grid1',ct='GridCon2',stoch=False):
    gw = Gridworld(x,y,fid=fid,contype=ct,stoch=stoch)
    a = gw.agents[0]
    a.put_in_cell(gw.get_cell(0,0))
    # gw.randfill([0,1,5,8])
    # gw.get_cell(4,4).set_contents(9) # The goal cell
    gw.pp()
    gw.run_loop()
    return gw