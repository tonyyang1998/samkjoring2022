import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
rnd=np.random
rnd.seed(0)

nr_passengers=3
nr_drivers=1

#plot & coordinates
xc = [1,2,3,4,6,7,8,9]
yc = [4,2,6,3,1,7,2,6]

plt.plot(xc[0],yc[0], c='r', marker = 's')
plt.plot(xc[-nr_drivers],yc[-nr_drivers], c='r', marker = 's')
plt.scatter(xc[1:len(xc)-nr_drivers], yc[1:len(yc)-nr_drivers], c='b')
plt.show()

#sets
D = [i for i in range(nr_drivers)]
N = [i for i in range(1, nr_passengers*2+nr_drivers)]
NP = N[:int(len(N)/2)]
ND = N[int(len(N)/2):]

N_k = [0] + N + [len(N)+1]
A_k = [(i, j) for i in N_k for j in N_k if i!=j]
print(D)
print(N)
print([0] + NP)
print(ND)
print(N_k)

#parameters
o_k = {0:0}
d_k = {0:7}
T_k = {i: 40 for i in range(nr_drivers+nr_passengers)}
T_ij = {(0, 1): 6, (0, 2): 8, (0, 3): 12, (0, 4): 100, (0, 5): 6.100, (0, 6): 7.100, (0, 7): 8.100, (1, 0): 2.6, (1, 2): 7, (1, 3): 2.5, (1, 4): 100, (1, 5): 15, (1, 6): 100, (1, 7): 100,
        (2, 0): 8, (2, 1): 7, (2, 3): 4, (2, 4): 15, (2, 5): 100, (2, 6): 100, (2, 7): 100, (3, 0): 12, (3, 1): 5, (3, 2): 4, (3, 4): 10, (3, 5): 7, (3, 6): 15, (3, 7): 100,
        (4, 0): 100, (4, 1): 100, (4, 2): 15, (4, 3): 10, (4, 5): 7, (4, 6): 8, (4, 7): 6, (5, 0): 100, (5, 1): 15, (5, 2): 100, (5, 3): 7, (5, 4): 7, (5, 6): 4, (5, 7): 100,
        (6, 0): 100, (6, 1): 100, (6, 2): 100, (6, 3): 15, (6, 4): 8, (6, 5): 4, (6, 7): 5, (7, 0): 100, (7, 1): 100, (7, 2): 100, (7, 3): 100, (7, 4): 6, (7, 5): 100, (7, 6): 5}
#T_ij = {(i,j): np.hypot(xc[i]-xc[j], yc[i] - yc[j]) for i,j in A_k}
Q_k = {i: 4 for i in range(nr_drivers)}
A_k1 = {0:30, 1:30, 2: 15, 3: 30}
A_k2 = {0:60, 1:45, 2: 30, 3: 45}


model=Model('RRP')

pairs=[(k,i,j) for k in D for i in N_k for j in N_k]
driver_node=[(k, i) for k in D for i in N_k]
x = model.addVars(pairs, vtype=GRB.BINARY, name ='x_kij')
z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
t = model.addVars(driver_node, vtype=GRB.CONTINUOUS, name='t_ki')

model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A_k for k in D))

#routing constraints
model.addConstrs(quicksum(x[k,i,j] for j in NP + [7]) == 1 for i in o_k for k in D)
model.addConstrs(quicksum(x[k,i,j] for i in [0] + ND) == 1 for j in d_k for k in D)
model.addConstrs((quicksum(x[k,i,j] for i in N_k[1:]) == quicksum(x[k,i,j] for i in N_k[:-1])) for k in D for j in N_k)
model.addConstrs((quicksum()))






