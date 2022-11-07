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
N = [i for i in range(nr_passengers*2+nr_drivers*2)]
NP = N[int(len(D)):int(len(N)/2)]
ND = N[int(len(N)/2):-int(len(D))]

#ny
A = [(i, j) for i in N for j in N if i!=j]
print(A)

#gammel
N_k = N
A_k = [(i, j) for i in N_k for j in N_k if i!=j]


'''Parameters'''
o_k = {}
d_k = {}
T_k = {}
T_ij = {(i,j): np.hypot(xc[i]-xc[j], yc[i] - yc[j]) for i,j in A}
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

"""Generate NK, NPK, NDK, AK"""

def generate_NK():
        NK = {}
        for drivers in drivers_json:
                nodes = []
                for paths in T_ij:
                        if paths[0] == drivers_json[drivers]['id']:
                                """origin og destination noden for driver. Hvis disse to ikke er i listen nodes,
                                 og hvis driver ikke rekker å komme seg til destination innen gitt timewindow"""
                                if paths[0] not in nodes and ((paths[0] + nr_passengers * 2 + nr_drivers) not in nodes) \
                                        and T_ij[(paths[0],paths[0] + nr_passengers * 2 + nr_drivers)] < A_k2[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers]:
                                        nodes.append(paths[0])
                                        nodes.append(paths[0] + nr_passengers * 2 + nr_drivers)
                                """pick up and delivery noder for passengers. Hvis pick up noden ikke er i listen, 
                                og den tilhørende delivery noden ikke er innenfor den korteste veien"""
                                if paths[1] not in nodes and ((paths[1] + nr_passengers) in ND) and (paths[1] + nr_passengers < len(N)-1) \
                                        and (T_ij[paths] < A_k2[paths[1] + nr_passengers]):
                                        nodes.append(paths[1])
                                if paths[1] not in nodes and paths[1] in ND and (T_ij[paths] < A_k2[paths[1]]):
                                        nodes.append(paths[1])
                                if drivers_json[drivers]['max_ride_time'] < T_ij[paths] and paths[1] in ND and paths[1] in nodes:
                                        nodes.remove(paths[1])
                                        nodes.remove(paths[1] - nr_passengers)
                nodes.sort()
                NK[drivers_json[drivers]['id']] = nodes
        return NK

NK = generate_NK()

def generate_NPK():
        NPK={}

        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in NP:
                                nodes.append(node)
                NPK[drivers]=nodes
        return NPK

NPK = generate_NPK()
def generate_NDK():
        NDK={}
        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in ND:
                                nodes.append(node)
                NDK[drivers]=nodes

        return NDK

NDK = generate_NDK()

print(NK)
AK = {k: [(i, j) for i in NK[k] for j in NK[k] if i!=j] for k in NK}


"""Helper functions"""
driver_origin_nodes = {k: o_k[k] for k in D}
driver_destination_nodes = {k: d_k[k] for k in D}
print([(k,i,j) for k in D for (i, j) in AK[k]])

'''Variables'''
model=Model('RRP')
x = model.addVars([(k,i,j) for k in D for (i, j) in AK[k]], vtype=GRB.BINARY, name ='x_kij')
model.update()
z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
model.update()



t = model.addVars([(k, i) for k in D for i in NK[k]], vtype=GRB.CONTINUOUS, name='t_ki')
model.update()

'''Model'''
#model.modelSense = GRB.MINIMIZE
#model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A for k in D), GRB.MINIMIZE)
#model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i in N for j in N for k in D if i!=j), GRB.MINIMIZE)
model.modelSense = GRB.MAXIMIZE
model.setObjective(quicksum(z[i] for i in NP))
model.update()


def add_constraints():
        '''Constraints'''
        '''Routing constraits'''
        model.addConstrs(quicksum(x[k,i,j] for j in NPK[k] + [driver_destination_nodes[k]]) == 1 for k in D for i in [driver_origin_nodes[k]])
        model.addConstrs(quicksum(x[k,i,j] for i in [driver_origin_nodes[k]] + NDK[k]) == 1 for k in D for j in [driver_destination_nodes[k]])
        model.addConstrs((quicksum(x[k,i,j] for j in NK[k][nr_drivers:] if j!=i) == quicksum(x[k,j,i] for j in NK[k][:-nr_drivers] if j!=i)) for k in D for i in NK[k][nr_drivers:-nr_drivers])
        model.addConstrs((quicksum(x[k,i,j] for j in NK[k] if j!=i) - quicksum(x[k,nr_passengers+i,j] for j in ND + [driver_destination_nodes[k]] if j!=(i + nr_passengers)))==0 for k in D for i in NPK[k])
        model.addConstrs((quicksum(x[k,i,j] for k in D for j in NK[k] if j!=i)) - z[i]==0 for i in NP)

        #ny constraint 1 (test ut å ta bort) ENDRING
        model.addConstrs((quicksum(x[k,i,j] for k in D for i in NK[k] if j!=i)) <= 1 for j in NP + ND)

        #ny constraint 2 (endre i rapporten) ENDRING
        model.addConstr((quicksum(x[k,i,j] for k in D for i in N for j in driver_origin_nodes.values() if j!=i and (j not in driver_origin_nodes.values() and i not in driver_origin_nodes.values()))) == 0)
        #ny constraint 3
        model.addConstr((quicksum(x[k,i,j] for k in D for i in driver_destination_nodes.values() for j in N if j!=i and (j not in driver_destination_nodes.values() and i not in driver_destination_nodes.values()))) == 0)

        '''Precedence constraint'''
        model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)

        '''Time constraint'''
        model.addConstrs(t[(k,i)]+T_ij[(i,j)] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for (i, j) in AK[k])
        model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NPK[k])
        model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NPK[k])

        nodes_without_destinations = {}
        for k in D:
                liste = []
                for i in NK[k]:
                        destinations = list(driver_destination_nodes.values())
                        if i not in destinations:
                                liste.append(i)
                nodes_without_destinations[k]=liste

        #ENDRET
        model.addConstrs(A_k1[k1]<=t[k, k2] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        #ENDRET
        model.addConstrs(t[k, k2]<=A_k2[k1] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NPK[k])

        print(driver_destination_nodes)
        model.addConstrs(t[k,driver_destination_nodes[k]] - t[k, driver_origin_nodes[k]] <= T_k[k] for k in D)

        #ny timewindow constraint:

        model.addConstrs(x[k,i,j]*A_k1[j]<=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        model.addConstrs(x[k,i,j]*A_k2[j]>=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        #model.addConstrs(A_k1[k1]<=(t[k, k1]+T_ij[] for k in D for k1 in d_k.values())
        #model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())

        '''Capacity constraint'''
        model.addConstrs(quicksum(x[k,i,j] for i in NPK[k] for j in NK[k] if j!=i) <= Q_k[k] for k in D)
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

        for k in D:
                active_arcs=[a for a in AK[k] if x[k, a[0], a[1]].x >0.99]
                arc_sum=0
                for i,j in active_arcs:
                        plt.plot([xc[i], xc[j]], [yc[i],yc[j]], c='g', zorder=0)

                for i in range(len(active_arcs)):
                        arc_sum += T_ij[active_arcs[i]]

        plt.plot(xc[0], yc[0], c='r', marker='s')
        plt.plot(xc[1], yc[1], c='r', marker='s')
        plt.plot(xc[-1],yc[-1], c='r', marker = 's')
        plt.plot(xc[-nr_drivers],yc[-nr_drivers], c='r', marker = 's')
        plt.scatter(xc[1:len(xc)-nr_drivers], yc[1:len(yc)-nr_drivers], c='b')
        plt.show()
        print(active_arcs)
        print(arc_sum)

visualize()





