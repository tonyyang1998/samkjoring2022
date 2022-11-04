import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
rnd=np.random
rnd.seed(0)

nr_passengers=3
nr_drivers=1

#plot & coordinates
xc = [8,12,16,20,30,32,40, 42]
yc = [12,18,8,16,20,12,10,18]

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
T_k = {i: 10000 for i in range(nr_drivers+nr_passengers)}
"""T_ij = {(0, 1): 6, (0, 2): 8, (0, 3): 12, (0, 4): 100, (0, 5): 100, (0, 6): 100, (0, 7): 100,
        (1, 0): 6, (1, 2): 7, (1, 3): 5, (1, 4): 100, (1, 5): 15, (1, 6): 100, (1, 7): 100,
        (2, 0): 8, (2, 1): 7, (2, 3): 4, (2, 4): 15, (2, 5): 100, (2, 6): 100, (2, 7): 100,
        (3, 0): 12, (3, 1): 5, (3, 2): 4, (3, 4): 10, (3, 5): 7, (3, 6): 15, (3, 7): 100,
        (4, 0): 100, (4, 1): 100, (4, 2): 15, (4, 3): 10, (4, 5): 7, (4, 6): 8, (4, 7): 6,
        (5, 0): 100, (5, 1): 15, (5, 2): 100, (5, 3): 7, (5, 4): 7, (5, 6): 4, (5, 7): 100,
        (6, 0): 100, (6, 1): 100, (6, 2): 100, (6, 3): 15, (6, 4): 8, (6, 5): 4, (6, 7): 5,
        (7, 0): 100, (7, 1): 100, (7, 2): 100, (7, 3): 100, (7, 4): 6, (7, 5): 100, (7, 6): 5}"""
T_ij = {(i,j): np.hypot(xc[i]-xc[j], yc[i] - yc[j]) for i,j in A_k}
print(T_ij)
Q_k = {i: 4 for i in range(nr_drivers)}
A_k1 = {4:100, 5:100, 6: 100, 7: 100}
A_k2 = {4:1000, 5:1000, 6: 1000, 7: 1000}
M = 1000


model=Model('RRP')

pairs=[(k,i,j) for k in D for i in N_k for j in N_k]
driver_node=[(k, i) for k in D for i in N_k]
x = model.addVars(pairs, vtype=GRB.BINARY, name ='x_kij')
model.update()
z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
model.update()
t = model.addVars(driver_node, vtype=GRB.CONTINUOUS, name='t_ki')
model.update()

model.modelSense = GRB.MINIMIZE
model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A_k for k in D))
#model.modelSense = GRB.MAXIMIZE
#model.setObjective(quicksum(z[i] for i in NP))

model.update()
#routing constraints
model.addConstrs(quicksum(x[k,i,j] for j in NP + [7]) == 1 for i in o_k.values() for k in D)
model.update()

model.addConstrs(quicksum(x[k,i,j] for i in [0]+ ND) == 1 for j in d_k.values() for k in D)
model.update()
model.addConstrs((quicksum(x[k,i,j] for j in N_k[1:]) == quicksum(x[k,j,i] for j in N_k[:-1])) for k in D for i in N_k[1:-1])
model.update()
model.addConstrs((quicksum(x[k,i,j] for j in N_k) - quicksum(x[k,nr_passengers+i,j] for j in N_k))==0 for k in D for i in NP)
model.update()
model.addConstrs((quicksum(x[k,i,j] for k in D for j in N_k))-z[i]==0 for i in NP)
model.update()

#ny constraint
model.addConstrs((quicksum(x[k,i,j] for k in D for i in N_k)) <= 1 for j in N_k)
model.update()


#precedence constraint
model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)
model.update()

#time constraint
model.addConstrs(t[(k,i)]+T_ij[(i,j)] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for i in N_k for j in N_k if i!=j)
model.update()

model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NP)
model.update()
model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NP)
model.update()


model.addConstrs(A_k1[k1]<=t[k, k1] for k in D for k1 in d_k.values())
model.update()
model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())
model.update()

model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NP)
model.update()
model.addConstrs(t[k,k1] - t[k, k2] <= T_k[k] for k in D for k1 in d_k.values() for k2 in o_k.values())
model.update()

#capacity constraint
model.addConstrs(quicksum(x[k,i,j] for i in NP for j in N_k) <= Q_k[k] for k in D)
model.update()

model.Params.TimeLimit=30
model.optimize()
obj = model.getObjective()
for i in model.getVars():
        print(i, i.x)


"""model.computeIIS()
model.write('model.MPS')
model.write('model.lp')
model.write('model.ilp')"""

active_arcs=[a for a in A_k if x[0, a[0], a[1]].x >0.99]

for i,j in active_arcs:
        plt.plot([xc[i], xc[j]], [yc[i],yc[j]], c='g', zorder=0)
plt.plot(xc[0], yc[0], c='r', marker='s')
plt.scatter(xc[1:], yc[1:], c='b')

plt.show()
print(active_arcs)

print("Hei")
for k1 in d_k.values():
        print(k1)
        for k in D:
                print(A_k1[k1])
                print(t[k, k1])
                print(A_k1[k1] <= t[k, k1])
                print(t[k, k1])
                print(A_k2[k1])
                print(t[k, k1]<=A_k2[k1])

