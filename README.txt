I. configuration.json contains the various predetermined parameters used in  the model.
    l = Length of the link in the bus network
    δup, δlow = upper and lower limit coefficients for the battery
    B = Maximal battery size
    B_min = Minimum battery size allowed
    B_max = Maximum battery size allowed
    v_bar = Represent if a bus line is selected to electrify
    M = Maximal battery size
    T = Lifespan of electric bus lines studied
    e_price = Cost per unit of energy consumption
    m = Number of buses in a bus line
    f = Frequency of buses per day in a bus line

---

II. Model_implementation_with_input.py - Contains the mathematical model

    A. Imported libraries
        1. matplotlib: To plot network graph G
        2. networkx: To instantiate network graph G
        3. numpy, json: Utilities for the program
    
    B. Input data
        1. data : JSON object which holds all the required data for the model
        2. N_r (0 <= r < 4) : Node indexes in route r
        3. node_connection : n x n matrix representing presence edge between a pair of nodes
                             if mat[i][j] == 1: edge present between node i+1 and j+1
                             if mat[i][j] == 0: edge not present between node i+1 and j+1
        4. intersection_nodes : Node indexes of intersection nodes (nodes more than one incoming links)
        5. c_inv : Cost of one inverter
        6. c_cab : Cost of unit cable length
        7. e_fix[r] (0 <= r < 4) : fixed part of energy consumption that is determined after the data preprocessing
        8. e_unit[r] (0 <= r < 4): energy consumption for carrying the battery pack and is linearly related to the battery size
        9. t[r] (0 <= r < 4): Travel time of the bus travel through a link in the network
        10. p : Energy supply rate of the power transmitter

    C. Utility functions
        * printInFile(loc, data): Prints the supplied data object in a file at location specified by loc
        * create_network(nodes, links): Creates networkx graphs with specified nodes and links
        * plot_network(G): Plots a networkx graph G

---

# 4.1
    * num_N specifies the total number of nodes present in the network
    * According to num_N, N is initialized as a list of [1,2,...,num_N] representing all the nodes present in the network
    * R represents the route indexes [0,1,..,num_R-1]
    * A is a list of tuples (i,j) representing there is an edge between ith node and jth node
        Calculate A:
            for each row i in node_connection
                for each column j in node_connection
                    if mat[i][j] == 1:
                        A.append(i+1, j+1)
    * A_r (0 <= r < 4) represents all the links in route r
        Calculate A_r:
            Similar as A with condition that i,j belong to N_r
    * G is a tuple of (N, A) i.e. all nodes and links of the network
    * N_s: List of all intersection nodes
        Calculate N_s:
            Just loop over intersection_nodes and append in N_s

---

# 4.2
    * x[(i,j)] represents x_i_j [if link (i,j) is deployed with the inductive cable]
        It is to be supplied as a variable in 4.6
        Right now, taken as random binary value
        Calculate x:
            Loop over all links (i,j) in A and assign random binary value
    
    * ind_cab_len represents the total length of inductive cable
        Calculate ind_cab_len:
            loop over all links (i,j) in A:
                ind_cab_len += l*x_i_j
            OR
            ind_cab_len = l*summ(x_i_j) for all links (i,j)
    
    * y[i] if a node i is the start node of some links deployed with the inductive cable
        It is to be supplied as a variable in 4.6
        Right now, taken as random binary value
        Calculate y:
            Loop over all nodes i in N and assign random binary value
    
    * y_i_sum represents summ(y_i) for each node i
    
    * x_wi_sum represents sum of all x[(w,i)] where i is an intersection node
        Calculate x_wi_sum:
            loop over each node i in N_s
                loop over each link (w,i) in A
                    x_wi_sum += x[(w,i)]
    
    * z[i] represents if intersection node i is connected with a link deployed with inductive cable
        It is to be supplied as a variable in 4.6
        Right now, taken as random binary value
        Calculate z:
            Loop over all nodes i in N_s and assign random binary value
    
    * z_i_sum represents summ(z_i) for each intersection node i
        Calculate z_i_sum:
            loop over each intersection node i
                z_i_sum += z[i]

    * cost_inv_cab represents total cost for installing these inverters and inductive cables
        Calculate cost_inv_cab:
            cost_inv_cab = c_inv*(y_i_sum-x_wi_sum+z_i_sum) + c_cab*ind_cab_len
                where ind_cab_len = l*summ(x[(i,j)])

---        

# 4.3
    * e_fix[r][(i,j)] represents predetermined parameter e_fix_r_i_j to be taken from input file
        Calculate e_fix:
            Loop over each route r
                Loop over each link (i,j) in route r
                    assign e_fix[r][(i,j)] according to input e_fix[r]
    
    * e_unit[r][(i,j)] represents predetermined parameter e_unit_r_i_j to be taken from input file
        Calculation similar to e_fix
    
    * b[r] represents battery of route r
        It is to be supplied as a variable in 4.6
        Right now, taken as random value between 0 to B
        Calculate b:
            Loop over each route r
                assign random value to b[r]
    
    * d[r][(i,j)] represents energy consumption value d_r_i_j
        Calculate d:
            loop over each route r
                loop over each link (i,j) in route r
                    data[r][(i,j)] = e_fix[r][(i,j)] + e_unit[r][(i,j)]*b[r]
    
    * total_cost_ec represents total cost due to energy consumption
        Calculate total_cost_ec:
            loop over each route r
                loop over each link (i,j) in route r
                    total_cost_ec += 365*T*e_unit*f[r]*m[r]*d[r][(i,j)]

---

# 4.4
    * t[r][(i,j)] represents travel time of the bus travel through a link in the network t_r_i_j
        To be taken as input
        Calculate t:
            Loop over each route r
                Loop over each link (i,j) in route r
                    assign t[r][(i,j)] according to input t[r]
    
    * s[r][(i,j)] represents amount of energy supply to electric buses on route r to travel through link (i, j)
        Calculate s:
            loop over each route r
                loop over each link (i,j) in route r
                    s[r][(i,j)] = p*t[r][(i,j)]*x[(i,j)]

    * u_r_i represents energy level of bus on route r and node i
        Calculate u:
            Loop over each route r
                Assign u_r_i as random value where i is first node of first link in A_r (i.e. starting node)
                for each link (i,j) in route r
                    u_r_j = u_r_i - d[r][(i,j)] + s[r][(i,j)]

---

# 4.5
    * open("z1.lp", "w") --> Initialize z1.lp file for single-objective model in 4.5
    * f.write("Minimize\n") --> Minimize the objective function 
    * f.write("obj: ") --> Name of the objective function

    * Calculate obj1:
        c_inv*summ(y_i) - c_inv*summ(x_w_i) + c_inv*summ(z_i) + c_cab*l*summ(x_i_j)
            where c_inv, c_cab, l are constants
                  y_i, x_i_j, z_i are variables

    * f.write("Subject To\n") --> Specify beginning of constraints

    * Constraint 1:
        summ(x_i_j) - y_i >= 0
            where x_i_j, y_i are variables
    
    * Constraint 2:
        x_w_i + y_i <= 1
            where x_w_i, y_i are variables
    
    * Constraint 3:
        - summ(x_w_i) + x_i_j - y_i <= 0
            where x_i_j, y_i are variables
    
    * Constraint 4:
        z_i - summ(x_w_i) <= 0
            where z_i, x_w_i are variables
    
    * Constraint 5:
        z_i - x_w_i >= 0
            where z_i, x_w_i are variables
    
    * Constraint 5_2:
        d_r_i_j = e_fix_r_i_j + e_unit_r_i_j * b_r
            where d_r_i_j, b_r are variables
                  e_fix_r_i_j, e_unit_r_i_j are constants
            NOTE: Special care for signs of e_fix_r_i_j and e_unit_r_i_j need to be taken care of due to format of lp file
    
    * Constraint 6:
        u_r_i - δup * b_r <= 0
            where u_r_i, b_r are variables
                  δup is constant
    
    * Constraint 7:
        u_r_i - δlow * b_r >= 0
            where u_r_i, b_r are variables
                  δlow is constant
    
    * Constraint 8:
        s_r_i_j - p * t_r_i_j * x_i_j = 0
            where s_r_i_j, x_i_j are variables
                  p, t_r_i_j are constants
    
    * Constraint 9:
        u_r_j - u_r_i + d_r_i_j - s_r_i_j = 0
            where u_r_i, d_r_i_j, s_r_i_j are variables
    
    * Constraint 11:
        b_r <= B
            where b_r is variable
                  B is constant
    
    * f.write("General\n") --> Specifies continuous variables
        u_r_i, s_r_i_j, d_r_i_j, b_r
    
    * f.write("Binary\n") --> Special binary variables (can only take values 0 or 1)
        x_i_j, y_i, z_i

---

# 4.6
    * open("z2.lp", "w") --> Initialize z2.lp file for bi-objective model in 4.6
    * f.write("Minimize multi-objectives\n") --> Minimize both objective functions
    * f.write("first:\n") --> Name of the first objective function

    * Calculate first:
        c_inv*summ(y_i) - c_inv*summ(x_w_i) + c_inv*summ(z_i) + c_cab*l*summ(x_i_j)
            where c_inv, c_cab, l are constants
                  y_i, x_i_j, z_i are variables

    * f.write("second:\n") --> Name of the second objective function

    * Calculate second:
        summ(365 * T * e_price * m_r * f_r * e_unit_r_i_j * b_r)
            where T, e_price, m_r, f_r, e_unit_r_i_j are constants
                  b_r is variable

    * f.write("Subject To\n") --> Specify beginning of constraints

    * Constraint 1:
        summ(x_i_j) - y_i >= 0
            where x_i_j, y_i are variables
    
    * Constraint 2:
        x_w_i + y_i <= 1
            where x_w_i, y_i are variables
    
    * Constraint 3:
        - summ(x_w_i) + x_i_j - y_i <= 0
            where x_i_j, y_i are variables
    
    * Constraint 4:
        z_i - summ(x_w_i) <= 0
            where z_i, x_w_i are variables
    
    * Constraint 5:
        z_i - x_w_i >= 0
            where z_i, x_w_i are variables
    
    * Constraint 17_1:
        e_unit_r_i_j * b_r - p * t_r_i_j * x_i_j >= - e_fix_r_i_j
            where e_unit_r_i_j, p, t_r_i_j, e_fix_r_i_j are constants
                  b_r, x_i_j are variables
    
    * Constraint 17_2:
        (e_unit_r_i_j + δlow - δup) * b_r - p * t_r_i_j * x_i_j <= - e_fix_r_i_j
            where e_unit_r_i_j, δlow, δup, p, t_r_i_j, e_fix_r_i_j are constants
                  b_r, x_i_j are variables
    
    * Constraint 20
        b_r >= B_min
            where b_r is variable
                  B_min is constant
    
    * Constraint 21
        b_r <= B_max
            where b_r is variable
                  B_max is constant

    * f.write("General\n") --> Specifies continuous variables
        b_r
    
    * f.write("Binary\n") --> Special binary variables (can only take values 0 or 1)
        x_i_j, y_i, z_i