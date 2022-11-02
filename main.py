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
print(NP)
print(ND)
print(N_k)
print(A_k)

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
A_k1 = {4:30, 5:30, 6: 15, 7: 30}
A_k2 = {4:60, 5:45, 6: 30, 7: 45}
M=100000


model=Model('RRP')

pairs=[(k,i,j) for k in D for i in N_k for j in N_k]
driver_node=[(k, i) for k in D for i in N_k]
x = model.addVars(pairs, vtype=GRB.BINARY, name ='x_kij')
z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
t = model.addVars(driver_node, vtype=GRB.CONTINUOUS, name='t_ki')

model.modelSense = GRB.MINIMIZE
model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A_k for k in D))

#routing constraints
model.addConstrs(quicksum(x[k,i,j] for j in NP + [7]) == 1 for i in o_k for k in D)
model.addConstrs(quicksum(x[k,i,j] for i in [0] + ND) == 1 for j in d_k for k in D)
model.addConstrs((quicksum(x[k,i,j] for i in N_k[1:]) == quicksum(x[k,i,j] for i in N_k[:-1])) for k in D for j in N_k)

model.addConstrs((quicksum(x[k,i,j] for i in N_k) - quicksum(x[k,nr_passengers+i,j] for i in NP))==0 for k in D for j in N_k)
model.addConstrs((quicksum(x[k,i,j] for k in D for j in N_k))-z[i]==0 for i in NP)

#precedence constraint
model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)

#time constraint
model.addConstrs(t[(k,i)]+T_ij[i,j] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for i in N for j in N if i!=j)
model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NP)
model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NP)

model.addConstrs(A_k1[k1]<=t[k, k1] for k in D for k1 in d_k.values())
model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())

model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NP)
model.addConstrs(t[k,k1] - t[k, k2] <= T_k[k] for k in D for k1 in d_k for k2 in o_k)

#capacity constraints
model.addConstrs(quicksum(x[k,i,j] for i in NP for j in N_k) <= Q_k[k] for k in D)

model.Params.MITGap=0.1
model.Params.TimeLimit=30
model.optimize()




