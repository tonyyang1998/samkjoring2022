import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import json
passengers_json = json.load(open('passengers.json'))
drivers_json = json.load(open('drivers.json'))
rnd=np.random
rnd.seed(0)

nr_passengers = len(passengers_json)
nr_drivers = len(drivers_json)

'''Coordinates '''
xc = []
yc = []

def add_coordinates():
        """Add coordinates"""
        for drivers in drivers_json:
                xc.append(drivers_json[drivers]['origin_xc'])
                yc.append(drivers_json[drivers]['origin_yc'])
        for passengers in passengers_json:
                xc.append(passengers_json[passengers]['origin_xc'])
                yc.append(passengers_json[passengers]['origin_yc'])
        for passengers in passengers_json:
                xc.append(passengers_json[passengers]['destination_xc'])
                yc.append(passengers_json[passengers]['destination_yc'])
        for drivers in drivers_json:
                xc.append(drivers_json[drivers]['destination_xc'])
                yc.append(drivers_json[drivers]['destination_yc'])
add_coordinates()

'''Sets'''
D = [i for i in range(nr_drivers)]
N=[i for i in range(nr_passengers*2+nr_drivers*2)]
NP = N[int(len(D)):int(len(N)/2)]
#NPK =
ND = N[int(len(N)/2):-int(len(D))]
#NDK =
N_k = N
A_k = [(i, j) for i in N_k for j in N_k if i!=j]

'''Parameters'''
o_k = {}
d_k = {}
T_k = {}
T_ij = {(i,j): np.hypot(xc[i]-xc[j], yc[i] - yc[j]) for i,j in A_k}
Q_k = {}
A_k1 = {}
A_k2 = {}
M = 1200

def add_parameters():
        """Add parameters"""
        for drivers in drivers_json:
                o_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id']
                d_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers
                T_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_ride_time']
                Q_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_capacity']
                A_k1[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['lower_tw']
                A_k2[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['upper_tw']
        for passengers in passengers_json:
                T_k[passengers_json[passengers]['id']] = passengers_json[passengers]['max_ride_time']
                A_k1[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['lower_tw']
                A_k2[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['upper_tw']
add_parameters()

"""Helper functions"""
driver_destination_nodes=[]
driver_origin_nodes=[]
for destinations in d_k.values():
        driver_destination_nodes.append(destinations)
for origins in o_k.values():
        driver_origin_nodes.append(origins)

'''Variables'''
model=Model('RRP')
x = model.addVars([(k,i,j) for k in D for (i, j) in A_k], vtype=GRB.BINARY, name ='x_kij')
model.update()
z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
model.update()
t = model.addVars([(k, i) for k in D for i in N_k], vtype=GRB.CONTINUOUS, name='t_ki')
model.update()

'''Model'''
#model.modelSense = GRB.MINIMIZE
#model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A_k for k in D), GRB.MINIMIZE)
model.modelSense = GRB.MAXIMIZE
model.setObjective(quicksum(z[i] for i in NP))
model.update()


def add_constraints():
        '''Constraints'''
        '''Routing constraits'''
        model.addConstrs(quicksum(x[k,i,j] for j in NP + driver_destination_nodes) == 1 for i in o_k.values() for k in D)
        model.addConstrs(quicksum(x[k,i,j] for i in driver_origin_nodes + ND) == 1 for j in d_k.values() for k in D)
        model.addConstrs((quicksum(x[k,i,j] for j in N_k[nr_drivers:] if j!=i) == quicksum(x[k,j,i] for j in N_k[:-nr_drivers] if j!=i)) for k in D for i in N_k[nr_drivers:-nr_drivers])
        model.addConstrs((quicksum(x[k,i,j] for j in N_k if j!=i) - quicksum(x[k,nr_passengers+i,j] for j in ND + driver_destination_nodes if j!=(i+nr_passengers)))==0 for k in D for i in NP)
        model.addConstrs((quicksum(x[k,i,j] for k in D for j in N_k if j!=i))-z[i]==0 for i in NP)

        #ny constraint 1
        model.addConstrs((quicksum(x[k,i,j] for k in D for i in N_k if j!=i)) <= 1 for j in N_k)
        #ny constraint 2
        model.addConstr((quicksum(x[k,i,j] for k in D for i in N_k for j in o_k.values() if j!=i)) == 0)
        #ny constraint 3
        model.addConstr((quicksum(x[k,i,j] for k in D for i in d_k.values() for j in N_k if j!=i)) == 0)

        '''Precedence constraint'''
        model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)

        '''Time constraint'''
        model.addConstrs(t[(k,i)]+T_ij[(i,j)] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for (i, j) in A_k)
        model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NP)
        model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NP)
        model.addConstrs(A_k1[k1]<=t[k, k1] for k in D for k1 in d_k.values())
        model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())
        model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NP)
        model.addConstrs(t[k,k1] - t[k, k2] <= T_k[k] for k in D for k1 in d_k.values() for k2 in o_k.values())

        #ny timewindow constraint:

        model.addConstrs(x[k,i,j]*A_k1[j]<=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NP for j in ND if i!=j)
        model.addConstrs(x[k,i,j]*A_k2[j]>=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NP for j in ND if i!=j)
        #model.addConstrs(A_k1[k1]<=(t[k, k1]+T_ij[] for k in D for k1 in d_k.values())
        #model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())

        '''Capacity constraint'''
        model.addConstrs(quicksum(x[k,i,j] for i in NP for j in N_k if j!=i) <= Q_k[k] for k in D)
        model.update()

"""Optimize"""
model.Params.TimeLimit=30
add_constraints()
model.optimize()

obj = model.getObjective()
for i in model.getVars():
        print(i, i.x)

"""model.computeIIS()
model.write('model.MPS')
model.write('model.lp')
model.write('model.ilp')"""


"""Visualization"""
def visualize():
        active_arcs=[a for a in A_k if x[0, a[0], a[1]].x >0.99]
        arc_sum=0
        for i,j in active_arcs:
                plt.plot([xc[i], xc[j]], [yc[i],yc[j]], c='g', zorder=0)

        for i in range(len(active_arcs)):
                arc_sum += T_ij[active_arcs[i]]

        plt.plot(xc[0], yc[0], c='r', marker='s')
        plt.plot(xc[-1],yc[-1], c='r', marker = 's')
        plt.plot(xc[-nr_drivers],yc[-nr_drivers], c='r', marker = 's')
        plt.scatter(xc[1:len(xc)-nr_drivers], yc[1:len(yc)-nr_drivers], c='b')
        plt.show()
        print(active_arcs)
        print(arc_sum)

visualize()





