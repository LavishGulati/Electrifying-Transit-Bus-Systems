import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import json

# Data configuration file
with open('configuration.json', encoding='utf-8') as fh:
	data = json.load(fh)

# Load data
data["N_0"] = np.loadtxt("Input_Files/Input_node_indx_10.txt", dtype=int)
data["N_1"] = np.loadtxt("Input_Files/Input_node_indx_11.txt", dtype=int)
data["N_2"] = np.loadtxt("Input_Files/Input_node_indx_14.txt", dtype=int)
data["N_3"] = np.loadtxt("Input_Files/Input_node_indx_24.txt", dtype=int)
node_connection = np.loadtxt("Input_Files/Input_node_connection.txt", dtype=int)
intersection_nodes = np.loadtxt("Input_Files/Input_intersection_idx.txt", dtype=int)
data['c_inv'] = np.loadtxt("Input_Files/Input_C_inv.txt")[0]
data['c_cab'] = np.loadtxt("Input_Files/Input_C_cable.txt")[0]

#energy consumption parameter input
e_fix = {}
e_fix[0] = np.loadtxt("Input_Files/Input_c_fix_10.txt")
e_fix[1] = np.loadtxt("Input_Files/Input_c_fix_11.txt")
e_fix[2] = np.loadtxt("Input_Files/Input_c_fix_14.txt")
e_fix[3] = np.loadtxt("Input_Files/Input_c_fix_24.txt")

e_unit = {}
e_unit[0] = np.loadtxt("Input_Files/Input_c_unit_10.txt")
e_unit[1] = np.loadtxt("Input_Files/Input_c_unit_11.txt")
e_unit[2] = np.loadtxt("Input_Files/Input_c_unit_14.txt")
e_unit[3] = np.loadtxt("Input_Files/Input_c_unit_24.txt")

t = {}
t[0] = np.loadtxt("Input_Files/Input_t_10.txt")
t[1] = np.loadtxt("Input_Files/Input_t_11.txt")
t[2] = np.loadtxt("Input_Files/Input_t_14.txt")
t[3] = np.loadtxt("Input_Files/Input_t_24.txt")

data['p'] = np.loadtxt("Input_Files/Input_P.txt")[0]


def printInFile(loc, data):
	with open(loc, 'w', encoding='utf-8') as f:
		f.write(str(data))

printInFile('Output/assigned_data.txt', data)



#############################################################################

# 4.1 Objective: Network Representation

# Number of nodes
data["num_N"] = 794

# N: List of node indexes
data["N"] = []
for i in range(1,data["num_N"]+1):
	data["N"].append(i)
printInFile('Output/nodes.txt', data['N'])

# R: List of Route Indexes
data["R"] = [0, 1, 2, 3]

# A: List of tuples (i,j)
data["A"] = []
for i in data["N"]:
	connection = node_connection[i-1]
	for j,c in enumerate(connection):
		if c:
			data["A"].append((i,j+1))
printInFile('Output/links.txt', data['A'])

# A_r: Edges in N_r
for route in data['R']:
	data["A_"+str(route)] = []
	for i in data["N_"+str(route)]:
		for j in data["N_"+str(route)]:
			if i != j and node_connection[i-1][j-1]:
				data["A_"+str(route)].append((i,j))
	printInFile('Output/A_'+str(route)+'.txt', data['A_'+str(route)])


# nodes - numpy array
# links = list of tuples
def create_network(nodes,links):
	# Directed Graph
	G = nx.DiGraph()
	
	# Add Nodes
	G.add_nodes_from(nodes)
	
	# Add directed links aka edges
	G.add_edges_from(links)
	
	#return created Graph
	return G

# Network Graph
def plot_network(G):
	pos = nx.layout.spring_layout(G, k=0.3*1/np.sqrt(len(G.nodes())), iterations=20)
	plt.figure(3, figsize=(30, 30))
	nx.draw(G, pos=pos)
	nx.draw_networkx_labels(G, pos=pos)
	plt.show()

#Create graph with nodes and links
data["G"] = create_network(data["N"], data["A"])

# Visualize sample graph
# plot_network(data["G"])

data["N_s"] = []
for i,c in enumerate(intersection_nodes):
	if c:
		data["N_s"].append(i+1)
printInFile('Output/intersection_nodes.txt', data['N_s'])



#############################################################################

# 4.2 Objective: Investment Cost of the DWCF

# Link (i,j) is deployed with an inductive cable

# Sets x_i_j as random values
# Inductive cable deployment as binary value in link(i,j)
# (0 - NO, 1 - YES)
def get_xij(A):
	data['x'] = {}
	for (i,j) in A:
		# Parameter to objetive function in original scenario
		data["x"][(i,j)] = np.random.choice([0,1])
	return

get_xij(data["A"])

# Total length of the inductive cables
# Arguments
# l = Length of the link in the bus network
# x_ij = Binary flag for cable deployment between i and j
def get_inductive_cable_len(l, A):
	ind_cab_len = 0
	for (i,j) in A:
		ind_cab_len += data["l"]*data["x"][(i,j)]
	return ind_cab_len

data["ind_cab_len"] = get_inductive_cable_len(data['l'],data['A'])
printInFile('Output/ind_cab_len.txt', data['ind_cab_len'])

# y_i denotes if node i is the start node of a series of adjacent links deployed with inductive cable
# Parameter to objective function in original scenario
def get_y_i_sum(N):
	y_i_sum = 0
	data['y'] = {}
	for i in N:
		data["y"][i] = np.random.choice([0,1])
		y_i_sum += data['y'][i]
	return y_i_sum

data['y_i_sum'] = get_y_i_sum(data['N'])

data["x_wi_sum"] = 0
for node in data["N_s"]:
	for (w,i) in data["A"]:
		if i == node and w != node:
			data["x_wi_sum"] += data['x'][(w,i)]

# z_i: Represent if an intersection node i is connected with a link deployed with inductive cable
# Parameter to objective function in original scenario
def get_z_i_sum(N_s):
	data['z_i_sum'] = 0
	data['z'] = {}
	for i in N_s:
		data["z"][i] = np.random.choice([0,1])
		data['z_i_sum'] += data["z"][i]
	return

get_z_i_sum(data['N_s'])

data["cost_inv_cab"] = data["c_inv"]*(data['y_i_sum']-data["x_wi_sum"]+data['z_i_sum'])
data["cost_inv_cab"] += data['c_cab']*data["ind_cab_len"]
printInFile('Output/cost_inv_cab.txt', data['cost_inv_cab'])



#############################################################################

# 4.3 Objective: Cost for  Energy Consumption

# e_fix & e_unit are predetermined parameters estimated based on the electric bus travel speed

data['e_fix'] = {}
for route in data['R']:
	id = 0
	data['e_fix'][route] = {}
	for (i,j) in data['A_'+str(route)]:
		data['e_fix'][route][(i,j)] = e_fix[route][id]
		id += 1
printInFile('Output/e_fix.txt', data['e_fix'])

data['e_unit'] = {}
for route in data['R']:
	id = 0
	data['e_unit'][route] = {}
	for (i,j) in data['A_'+str(route)]:
		data['e_unit'][route][(i,j)] = e_unit[route][id]
		id += 1
printInFile('Output/e_unit.txt', data['e_unit'])

# b_r is Battery size for Route r
# Parameter to objective function in original scenario
data['b'] = {}
for route in data['R']:
	data['b'][route] = np.random.random()*660
printInFile('Output/b_r.txt', data['b'])

# d_rfij represent the energy consumption of the electric bus traveling through the link (i,j) with frequency F
data['d'] = {}
for route in data['R']:
	data['d'][route] = {}
	for (i,j) in data['A_'+str(route)]:
		data['d'][route][(i,j)] = data['e_fix'][route][(i,j)] + \
			data['e_unit'][route][(i,j)]*data['b'][route]
printInFile('Output/d_rfij.txt', data['d'])

# Total cost arisen by energy consumption

# m_r  represents the number of electric buses on route r 
# f_r  represents the operation frequency on each day for a bus. 
# T is the total operation time of electric buses studied

data['total_cost_ec'] = 0
for route in data['R']:
	for (i,j) in data['A_'+str(route)]:
		data["total_cost_ec"] += data['f'][str(route)]*data['m'][str(route)]*data['d'][route][(i,j)]
printInFile('Output/total_cost_ec.txt', data['total_cost_ec'])



#############################################################################

# 4.4 Constraint: Certain Level of SOC of Battery

#  p represent the energy supply rate of the power transmitter after considering the energy loss

#  t_rij represent the travel time of electric buses on route r to travel through link (i,j)
data['t'] = {}
for route in data['R']:
	id = 0
	data['t'][route] = {}
	for (i,j) in data['A_'+str(route)]:
		data['t'][route][(i,j)] = t[route][id]
		id += 1
printInFile('Output/t_rfij.txt', data['t'])

# s_rfij represent the amount of energy supply to electric buses on route r  to travel through link (i,j)
data['s'] = {}
for route in data['R']:
	data['s'][route] = {}
	for (i,j) in data['A_'+str(route)]:
		data['s'][route][(i,j)] = data['p']*data['t'][route][(i,j)]*data['x'][(i,j)]
printInFile('Output/s_rfij.txt', data['s'])

#Energy level of u_rj
for route in data['R']:
	start = True
	for (i,j) in data['A_'+str(route)]:
		if start:
			data['u_'+str(route)+'_'+str(i)] = np.random.random()*660
			start = False
		data['u_'+str(route)+'_'+str(j)] = data['u_'+str(route)+'_'+str(i)] - \
			data['d'][route][(i,j)] + data['s'][route][(i,j)]



#############################################################################

# 4.5 Model: Electric Buses for Rotation
f = open("z1.lp", "w")
f.write("Minimize\n")
f.write("obj: ")

# Objective function 1
obj1 = ""
for node in data["N"]:
	obj1 += " + " + str(data["c_inv"]) + " y_" + str(int(node))

for node in data["N_s"]:
	for (w,i) in data["A"]:
		if i == node and w != node:
			obj1 += " - " + str(data["c_inv"]) + " x_" + str(int(w)) + "_" + str(int(node))

for node in data["N_s"]:
	obj1 += " + " + str(data["c_inv"]) + " z_" + str(int(node))

for (i,j) in data["A"]:
	obj1 += " + " + str(data["c_cab"]*data["l"]) + " x_" + str(int(i)) + "_" + str(int(j))

f.write(obj1+"\n")

f.write("Subject To\n")

# Constraint 1
for node in data["N"][0:-1]:
	c1 = ""
	for(i,j) in data["A"]:
		if i == node and j != node:
			c1 += " + x_" + str(int(i)) + "_" + str(int(j))
	c1 += " - y_" + str(int(node))
	c1 += " >= 0"
	# end node of route 14, i=452 or n_node-1 do not make sense for x variable.
	if node != 453:
		f.write(c1+"\n")

# Constraint 2
for node in data["N"]:
	for (w,i) in data["A"]:
		if i == node and w != i:
			c2 = "x_" + str(int(w)) + "_" + str(int(i)) + " + y_" + str(int(i))
			c2 += " <= 1"
			f.write(c2+"\n")

# Constraint 3
for i in data['N'][1:-1]:
	for j in data['N'][2:]:
		if node_connection[i-1][j-1]:
			c3 = ''
			for w in data['N']:
				if node_connection[w-1][i-1]:
					c3 += ' - x_'+str(w)+'_'+str(i)
			c3 += ' + x_'+str(i)+'_'+str(j) + ' - y_'+str(i)
			c3 += ' <= 0'
			f.write(c3+'\n')

# Constraint 4
for node in data["N_s"]:
	c4 = "z_"+str(int(node))
	for (w,i) in data["A"]:
		if i == node and w != node:
			c4 += " - x_"+str(int(w))+"_"+str(int(node))
	c4 += " <= 0"
	f.write(c4+"\n")

# Constraint 5
for node in data["N_s"]:
	for (w,i) in data["A"]:
		if node == i and w != node:
			c5 = "z_"+str(int(node)) + " - x_"+str(int(w))+"_"+str(int(node))
			c5 += " >= 0"
			f.write(c5+"\n")

# Constraint 5_2
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		c5_2 = "d_"+str(route)+"_"+str(i)+"_"+str(j)
		if data["e_unit"][route][(i,j)] == 0:
			continue
		elif data["e_unit"][route][(i,j)] < 0:
			c5_2 += " + "+str(0-data["e_unit"][route][(i,j)])+" b_"+str(route)
		elif data["e_unit"][route][(i,j)] > 0:
			c5_2 += " - "+str(data["e_unit"][route][(i,j)])+" b_"+str(route)
		c5_2 += " = "+str(float(data['e_fix'][route][(i,j)]))
		f.write(c5_2+"\n")

# Constraint 6
for route in data["R"]:
	for i in data["N_"+str(route)]:
		c6 = "u_"+str(route)+"_"+str(i)
		c6 += " - "+str(data["δup"]) + " b_"+str(route)
		c6 += " <= 0"
		f.write(c6+"\n")

# Constraint 7
for route in data["R"]:
	for i in data["N_"+str(route)]:
		c7 = "u_"+str(route)+"_"+str(i)
		c7 += " - "+str(data["δlow"]) + " b_"+str(route)
		c7 += " >= 0"
		f.write(c7+"\n")

# Constraint 8
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		c8 = "s_"+str(route)+"_"+str(i)+"_"+str(j)
		c8 += " - "+str(data["p"]*data["t"][route][(i,j)])+" x_"+str(i)+"_"+str(j)
		c8 += " = 0"
		f.write(c8+"\n")

# Constraint 9
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		c9 = "u_"+str(route)+"_"+str(j) + " - u_"+str(route)+"_"+str(i)
		c9 += " + d_"+str(route)+"_"+str(i)+"_"+str(j)
		c9 += " - s_"+str(route)+"_"+str(i)+"_"+str(j)
		c9 += " = 0"
		f.write(c9+"\n")

# Constraint 10

# Constraint 11
for route in data["R"]:
	c11 = "b_"+str(route)
	c11 += " <= "
	c11 += str(data['B'])
	f.write(c11+"\n")

# General Variables
f.write("General\n")
var = ""

# u_r_i
for route in data["R"]:
	for i in data["N_"+str(route)]:
		var += ' u_'+str(route)+"_"+str(i)

# s_r_i_j
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		var += ' s_'+str(route)+"_"+str(i)+"_"+str(j)

# d_r_i_j
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		var += ' d_'+str(route)+"_"+str(i)+"_"+str(j)

# b_r
for route in data["R"]:
	var += ' b_'+str(route)

f.write(var+"\n")

# Binary Variables
f.write("Binary\n")
var = ""

# x_i_j
for (i,j) in data["A"]:
	var += ' x_'+str(int(i))+"_"+str(int(j))

# y_i
for i in data["N"]:
	var += ' y_'+str(int(i))

# z_i
for i in data["N_s"]:
	var += ' z_'+str(int(i))

f.write(var+"\n")
f.write("End\n")



#############################################################################

# 4.6 Model: Fixed Electric Bus Routes

f = open("z2.lp", "w")
f.write("Minimize multi-objectives\n")

# Objective function 1
f.write("first:\n")
obj1 = ""
for node in data["N"]:
	obj1 += " + " + str(data["c_inv"]) + " y_" + str(int(node))

for node in data["N_s"]:
	for (w,i) in data["A"]:
		if i == node and w != node:
			obj1 += " - " + str(data["c_inv"]) + " x_" + str(int(w)) + "_" + str(int(node))

for node in data["N_s"]:
	obj1 += " + " + str(data["c_inv"]) + " z_" + str(int(node))

for (i,j) in data["A"]:
	obj1 += " + " + str(data["c_cab"]*data["l"]) + " x_" + str(int(i)) + "_" + str(int(j))

f.write(obj1+"\n")

# Objective function 2
f.write("second:\n")
# obj2 = ""
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		obj2 += " + " + str(data['e_price']*365*data["T"]*data["m"][str(route)]*data["f"][str(route)])
# 		obj2 += " d_"+str(int(route))+"_"+str(int(i))+"_"+str(int(j))
obj2 = ""
for route in data["R"]:
	c_unit = 0
	val = data['e_price']*365*data['T']*data["m"][str(route)]*data["f"][str(route)]
	for (i,j) in data["A_"+str(route)]:
		c_unit += data['e_unit'][route][(i,j)]
	if val*c_unit < 0:
		obj2 += ' - '+str(0-val*c_unit)
	else:
		obj2 += ' + '+str(val*c_unit)
	obj2 += ' b_'+str(route)

f.write(obj2+"\n")

f.write("Subject to\n")

# Constraint 1
for node in data["N"][0:-1]:
	c1 = ""
	for(i,j) in data["A"]:
		if i == node and j != node:
			c1 += " + x_" + str(int(i)) + "_" + str(int(j))
	c1 += " - y_" + str(int(node))
	c1 += " >= 0"
	# end node of route 14
	if node != 454:
		f.write(c1+"\n")

# Constraint 2
for node in data["N"]:
	for (w,i) in data["A"]:
		if i == node and w != i:
			c2 = "x_" + str(int(w)) + "_" + str(int(i)) + " + y_" + str(int(i))
			c2 += " <= 1"
			f.write(c2+"\n")

# Constraint 3
for i in data['N'][1:-1]:
	for j in data['N'][2:]:
		if node_connection[i-1][j-1]:
			c3 = ''
			for w in data['N']:
				if node_connection[w-1][i-1]:
					c3 += ' - x_'+str(w)+'_'+str(i)
			c3 += ' + x_'+str(i)+'_'+str(j) + ' - y_'+str(i)
			c3 += ' <= 0'
			f.write(c3+'\n')

# Constraint 4
for node in data["N_s"]:
	c4 = "z_"+str(int(node))
	for (w,i) in data["A"]:
		if i == node and w != node:
			c4 += " - x_"+str(int(w))+"_"+str(int(node))
	c4 += " <= 0"
	f.write(c4+"\n")

# Constraint 5
for node in data["N_s"]:
	for (w,i) in data["A"]:
		if node == i and w != node:
			c5 = "z_"+str(int(node)) + " - x_"+str(int(w))+"_"+str(int(node))
			c5 += " >= 0"
			f.write(c5+"\n")

# Constraint 14
# c14 = ""
# for route in data["R"]:
# 	c14 += " + v_"+str(int(route))
# c14 += " = "+str(data["v_bar"])

# f.write(c14+"\n")


# Constraint 14
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		if data['e_unit'][route][(i,j)] >= 0:
# 			c14 = "d_"+str(route)+"_"+str(i)+"_"+str(j)
# 			if data['e_fix'][route][(i,j)] < 0:
# 				c14 += ' + '+str(0-float(data['e_fix'][route][(i,j)]))+" v_"+str(route)
# 			else:
# 				c14 += ' - '+str(float(data['e_fix'][route][(i,j)]))+" v_"+str(route)
# 			if data["e_unit"][route][(i,j)] < 0:
# 				c14 += " + "+str(0-float(data["e_unit"][route][(i,j)]))+" b_"+str(route)
# 			else:
# 				c14 += " - "+str(float(data["e_unit"][route][(i,j)]))+" b_"+str(route)
# 			c14 += " = 0"
# 			f.write(c14+"\n")
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		c14 = "d_"+str(route)+"_"+str(i)+"_"+str(j)
# 		if data["e_unit"][route][(i,j)] < 0:
# 			c14 += " + "+str(0-float(data["e_unit"][route][(i,j)]))+" b_"+str(route)
# 		else:
# 			c14 += " - "+str(float(data["e_unit"][route][(i,j)]))+" b_"+str(route)
# 		c14 += " = "
# 		c14 += str(float(data['e_fix'][route][(i,j)]))
# 		f.write(c14+"\n")

# Constraint 15
# for route in data["R"]:
# 	for i in data["N_"+str(route)]:
# 		c15 = "u_"+str(route)+"_"+str(i)
# 		c15 += ' - '+str(data["δup"]) + " b_"+str(route)
# 		c15 += " <= 0"
# 		f.write(c15+"\n")

# Constraint 16
# for route in data["R"]:
# 	for i in data["N_"+str(route)]:
# 		c16 = "u_"+str(route)+"_"+str(i)
# 		c16 += ' - '+str(data["δlow"]) + " b_"+str(route)
# 		c16 += " >= 0"
# 		f.write(c16+"\n")

# Constraint 17
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		c17 = "s_"+str(route)+"_"+str(i)+"_"+str(j)
# 		c17 += ' - '+str(data["p"]*data["t"][route][(i,j)])+" x_"+str(i)+"_"+str(j)
# 		c17 += " = 0"
# 		f.write(c17+"\n")
for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		if data['e_unit'][route][(i,j)] >= 0:
			c17 = str(data['e_unit'][route][(i,j)])+' b_'+str(route)
			c17 += ' - '+str(data["p"]*data["t"][route][(i,j)])+" x_"+str(i)+"_"+str(j)
			c17 += " >= "
			c17 += str(0-data['e_fix'][route][(i,j)])
			f.write(c17+"\n")

for route in data["R"]:
	for (i,j) in data["A_"+str(route)]:
		c17 = str(data['e_unit'][route][(i,j)]+data["δlow"]-data["δup"])+' b_'+str(route)
		c17 += ' - '+str(data["p"]*data["t"][route][(i,j)])+" x_"+str(i)+"_"+str(j)
		c17 += " <= "
		c17 += str(0-data['e_fix'][route][(i,j)])
		f.write(c17+"\n")

# Constraint 18
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		c18 = "u_"+str(route)+"_"+str(j) + " - u_"+str(route)+"_"+str(i)
# 		c18 += " + d_"+str(route)+"_"+str(i)+"_"+str(j)
# 		c18 += " - s_"+str(route)+"_"+str(i)+"_"+str(j)
# 		c18 += " + " + str(data["M"]) + " v_"+str(route)
# 		c18 += " >= "
# 		c18 += str(data["M"]) 
# 		f.write(c18+"\n")

# Constraint 19
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		c19 = "u_"+str(route)+"_"+str(j) + " - u_"+str(route)+"_"+str(i)
# 		c19 += " + d_"+str(route)+"_"+str(i)+"_"+str(j)
# 		c19 += " - s_"+str(route)+"_"+str(i)+"_"+str(j)
# 		c19 += " - "+str(data["M"]) + " v_"+str(route)
# 		c19 += " <= "
# 		c19 += " -" + str(data["M"])
# 		f.write(c19+"\n")

# Constraint 20
# for route in data["R"]:
# 	c20 = "b_"+str(route)
# 	c20 += " >= 0"
# 	f.write(c20+"\n")
for route in data["R"]:
	c20 = "b_"+str(route)
	c20 += " >= "+str(data['B_min'])
	f.write(c20+"\n")

# Constraint 21
# for route in data["R"]:
# 	c21 = "b_"+str(route)
# 	c21 += ' - '+str(data["M"])+" v_"+str(route)
# 	c21 += " <= 0"
# 	f.write(c21+"\n")
for route in data["R"]:
	c21 = "b_"+str(route)
	c21 += " <= "+str(data['B_max'])
	f.write(c21+"\n")

# General Variables
f.write("General\n")
var = ""

# u_r_i
# for route in data["R"]:
# 	for i in data["N_"+str(route)]:
# 		var += ' u_'+str(route)+"_"+str(i)

# s_r_i_j
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		var += ' s_'+str(route)+"_"+str(i)+"_"+str(j)

# d_r_i_j
# for route in data["R"]:
# 	for (i,j) in data["A_"+str(route)]:
# 		var += ' d_'+str(route)+"_"+str(i)+"_"+str(j)

# b_r
for route in data["R"]:
	var += ' b_'+str(route)

f.write(var+"\n")

# Binary Variables
f.write("Binary\n")
var = ""

# x_i_j
for (i,j) in data["A"]:
	var += ' x_'+str(int(i))+"_"+str(int(j))

# y_i
for i in data["N"]:
	var += ' y_'+str(int(i))

# z_i
for i in data["N_s"]:
	var += ' z_'+str(int(i))

# v_r
# for route in data["R"]:
# 	var += ' v_'+str(route)

f.write(var+"\n")
f.write("End\n")