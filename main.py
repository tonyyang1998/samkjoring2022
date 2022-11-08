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
A = [(i, j) for i in N for j in N if i!=j]

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


def preprocess_nodes_NK():
        """
        :return: {k: [nodes]} - set of preprocessed feasible nodes for driver k to visit
        """
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
                                """If the time to travel directly arc from a driver node to """
                                if drivers_json[drivers]['max_ride_time'] < T_ij[paths] and paths[1] in ND and paths[1] in nodes:
                                        nodes.remove(paths[1])
                                        nodes.remove(paths[1] - nr_passengers)
                nodes.sort()
                NK[drivers_json[drivers]['id']] = nodes
        return NK

NK = preprocess_nodes_NK()

def generate_NPK(NK):
        """
        :param NK: {k: [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k: [nodes]} - set of feasible pick up nodes for driver k to visit
        """
        NPK={}
        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in NP:
                                nodes.append(node)
                NPK[drivers]=nodes
        return NPK

def generate_NDK(NK):
        """
        :param NK: {k: [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k: [nodes]} - set of feasible pick up nodes for driver k to visit
        """
        NDK={}
        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in ND:
                                nodes.append(node)
                NDK[drivers]=nodes
        return NDK

NPK = generate_NPK(NK)
NDK = generate_NDK(NK)

"""Helper functions"""
driver_origin_nodes = {k: o_k[k] for k in D}
driver_destination_nodes = {k: d_k[k] for k in D}

def check_origin_node(node):
        """
        :param node: Integer - a node
        :return: Boolean - True if node is a origin node, False otherwise
        """
        return node in driver_origin_nodes.values()

def check_destination_node(node):
        """
        :param node: Integer - a node
        :return: Boolean - True if node is a destination node, False otherwise
        """
        return node in driver_destination_nodes.values()

def from_delivery_to_pickup_arc(arc):
        """
        :param arc: (i, j) - arc from node i to node j
        :return: Boolean - returns True if i is a delivery node AND j is a pick up node in arc (i, j)
        """
        return arc[0] in ND and arc[1] in NP

def generate_AK(NK):
        """ Remove all arcs (i, j) where j are origin nodes, i are destination nodes, and i j in (i, j) where i are pick up nodes and j are delivery nodes
        :param NK: {k, [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k, [arcs]} - returns a set of feasible arcs (i, j) for driver k to travel with.
        """
        result={}
        AK = {k: [(i, j) for i in NK[k] for j in NK[k] if i != j] for k in NK}
        for driver in AK:
                arcs = []
                for arc in AK[driver]:
                        if not check_origin_node(arc[1]):
                                if not check_destination_node(arc[0]):
                                        if not from_delivery_to_pickup_arc(arc):
                                                arcs.append(arc)
                result[driver]=arcs
        return result

AK = generate_AK(NK)

print("D:", D)
print("N:", N)
print("NP:", NP)
print("ND:", ND)
print("A:", A)
print("NK:", NK)
print("NPK:", NPK)
print("NDK:", NDK)
print("AK:", AK)

model=Model('RRP')

def set_variables():
        """Add variables"""
        x = model.addVars([(k,i,j) for k in D for (i, j) in AK[k]], vtype=GRB.BINARY, name ='x_kij')
        model.update()
        z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
        model.update()
        t = model.addVars([(k, i) for k in D for i in NK[k]], vtype=GRB.CONTINUOUS, name='t_ki')
        model.update()
        return x, z, t

x, z ,t = set_variables()

def set_objective():
        '''Model'''
        #model.modelSense = GRB.MINIMIZE
        #model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A for k in D), GRB.MINIMIZE)
        #model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i in N for j in N for k in D if i!=j), GRB.MINIMIZE)
        model.modelSense = GRB.MAXIMIZE
        model.setObjective(quicksum(z[i] for i in NP))
        model.update()

set_objective()

def add_constraints():
        '''Constraints'''
        '''Routing constraits'''
        nodes_without_destinations = {}
        for k in D:
                liste = []
                for i in NK[k]:
                        destinations = list(driver_destination_nodes.values())
                        if i not in destinations:
                                liste.append(i)
                nodes_without_destinations[k] = liste

        model.addConstrs(quicksum(x[k,i,j] for j in NPK[k] + [driver_destination_nodes[k]]) == 1 for k in D for i in [driver_origin_nodes[k]])


        model.addConstrs(quicksum(x[k,i,j] for i in [driver_origin_nodes[k]] + NDK[k]) == 1 for k in D for j in [driver_destination_nodes[k]])
        model.addConstrs((quicksum(x[k,i,j] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) == quicksum(x[k,j,i] for j in NK[k] if j!=i if j not in list(driver_destination_nodes.values()))) for k in D for i in NK[k][1:-1])

        model.addConstrs((quicksum(x[k,i,j] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) - quicksum(x[k,nr_passengers+i,j] for j in ND + [driver_destination_nodes[k]] if j!=(i + nr_passengers)))==0 for k in D for i in NPK[k])
        model.addConstrs((quicksum(x[k,i,j] for k in D for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values()))) - z[i]==0 for i in NP)

        #ny constraint 1 (test ut å ta bort) ENDRING
        model.addConstrs((quicksum(x[k,i,j] for k in D for i in NK[k] if j!=i if i not in list(driver_destination_nodes.values()))) <= 1 for j in NP + ND)


        #ny constraint 2 (endre i rapporten) ENDRING

        model.addConstr((quicksum(x[k,i,j] for k in D for i in N for j in driver_origin_nodes.values() if j!=i and (j not in driver_origin_nodes.values() and i not in driver_origin_nodes.values()))) == 0)

        #model.addConstrs((quicksum(x[k, i, j] for k in D for i in NP + ND + list(driver_destination_nodes.values()) if i!=j)) == 0 for j in list(driver_origin_nodes.values()))


        #ny constraint 3
        model.addConstr((quicksum(x[k,i,j] for k in D for i in driver_destination_nodes.values() for j in N if j!=i and (j not in driver_destination_nodes.values() and i not in driver_destination_nodes.values()))) == 0)
        #model.addConstrs((quicksum(x[k, i, j] for k in D for j in N if i!=j) == 0 for i in list(driver_destination_nodes.values())))
        #model.addConstrs((quicksum(x[k, i, j] for k in D for j in N if i!=j if (i not in list(driver_destination_nodes.values()) and j not in list(driver_destination_nodes.values()))) == 0 for i in list(driver_destination_nodes.values())))


        '''Precedence constraint'''
        model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)

        '''Time constraint'''
        model.addConstrs(t[(k,i)]+T_ij[(i,j)] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for (i, j) in AK[k])
        model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NPK[k])
        model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NPK[k])

        #ENDRET
        model.addConstrs(A_k1[k1]<=t[k, k2] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        #ENDRET
        model.addConstrs(t[k, k2]<=A_k2[k1] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NPK[k])


        model.addConstrs(t[k,driver_destination_nodes[k]] - t[k, driver_origin_nodes[k]] <= T_k[k] for k in D)

        #ny timewindow constraint:

        model.addConstrs(x[k,i,j]*A_k1[j]<=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        model.addConstrs(x[k,i,j]*A_k2[j]>=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        #model.addConstrs(A_k1[k1]<=(t[k, k1]+T_ij[] for k in D for k1 in d_k.values())
        #model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())

        '''Capacity constraint'''
        model.addConstrs(quicksum(x[k,i,j] for i in NPK[k] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) <= Q_k[k] for k in D)
        model.update()

"""Optimize"""
model.Params.TimeLimit=30
add_constraints()
model.optimize()

obj = model.getObjective()
#for i in model.getVars():
 #       print(i, i.x)

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





