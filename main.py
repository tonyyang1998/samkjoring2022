import json
from gurobipy import *
import pandas as pd

m = Model()
x = m.addVar(vtype=GRB.BINARY, name="x")
y = m.addVar(vtype=GRB.BINARY, name="y")
z = m.addVar(vtype=GRB.BINARY, name="z")

m.update()

m.setObjective(x+y+2*z, GRB.MAXIMIZE)
c1=m.addConstr(x+2*y+3*z<=4)
c2=m.addConstr(x+y>=1)

m.optimize()

m.printAttr('X')