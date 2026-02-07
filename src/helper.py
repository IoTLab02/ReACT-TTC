from agents import EV, CP
import random
import os
import pandas as pd


random.seed(123)


def debug_print(Debug, message):
    if Debug:
        print(message)
        

def create_CPobjects(raw_CP_data, n_cp_in_fast, n_cp_in_regular, n_cp_out_fast, n_cp_out_regular, q):
    n_cp = n_cp_in_fast + n_cp_in_regular + n_cp_out_fast + n_cp_out_regular
    if len(raw_CP_data) < n_cp:
        raise ValueError("Dataset has less CP info than required")
    CPs = []
    
    selected_CP_info = random.sample(sorted(raw_CP_data), n_cp)
    
    count = 0
    for (global_id, lat, long) in selected_CP_info:
        theta = 0
        eta = 0
        ucost = 0.4
        if count < n_cp_in_fast: # In Fast
            theta = 1   # fast
            eta = 0     # In-net
            ucost_lower = 0.4 # unified cost lower limit
            ucost_upper = 0.5 # unified cost upper limit
        elif count < n_cp_in_fast + n_cp_in_regular:    #In Regular
            theta = 0   # regular
            eta = 0     # In-net
            ucost_lower = 0.2 # unified cost lower limit
            ucost_upper = 0.25 # unified cost upper limit
        elif count < n_cp_in_fast + n_cp_in_regular + n_cp_out_fast:    # Out Fast 
            theta = 1   # fast
            eta = 1     # Out-net
            ucost_lower = 0.5 # unified cost lower limit
            ucost_upper = 0.7 # unified cost upper limit
        else:   # Out Regular
            theta = 0   # regular
            eta = 1     # Out-net  
            ucost_lower = 0.3 # unified cost lower limit
            ucost_upper = 0.45 # unified cost upper limit
        
        ucost = random.uniform(ucost_lower, ucost_upper)
        cp = CP(local_ID=count, global_ID = global_id, lat = lat, lon = long, theta=theta, eta=eta, ucost=ucost, q=q)
        CPs.append(cp)
        count = count + 1
    return CPs


def create_CPobjects_SMEVCA_cost_order(raw_CP_data, n_cp_in_fast, n_cp_in_regular, n_cp_out_fast, n_cp_out_regular, q):
    n_cp = n_cp_in_fast + n_cp_in_regular + n_cp_out_fast + n_cp_out_regular
    if len(raw_CP_data) < n_cp:
        raise ValueError("Dataset has less CP info than required")
    CPs = []
    
    selected_CP_info = random.sample(raw_CP_data, n_cp)
    
    count = 0
    for (global_id, lat, long) in selected_CP_info:
        theta = 0
        eta = 0
        ucost = 0.4
        if count < n_cp_in_fast: # In Fast
            theta = 1   # fast
            eta = 0     # In-net
            ucost_lower = 0.4 # unified cost lower limit
            ucost_upper = 0.5 # unified cost upper limit
        elif count < n_cp_in_fast + n_cp_in_regular:    #In Regular
            theta = 0   # regular
            eta = 0     # In-net
            ucost_lower = 0.2 # unified cost lower limit
            ucost_upper = 0.25 # unified cost upper limit
        elif count < n_cp_in_fast + n_cp_in_regular + n_cp_out_fast:    # Out Fast 
            theta = 1   # fast
            eta = 1     # Out-net
            ucost_lower = 0.7 # unified cost lower limit
            ucost_upper = 0.8 # unified cost upper limit
        else:   # Out Regular
            theta = 0   # regular
            eta = 1     # Out-net  
            ucost_lower = 0.55 # unified cost lower limit
            ucost_upper = 0.65 # unified cost upper limit
        
        ucost = random.uniform(ucost_lower, ucost_upper)
        cp = CP(local_ID=count, global_ID = global_id, lat = lat, lon = long, theta=theta, eta=eta, ucost=ucost, q=q)
        CPs.append(cp)
        count = count + 1
    return CPs

def create_EVobjects(raw_EV_data, n_ev, gamma):
    EVs = []
    selected_EV_info = random.sample(sorted(raw_EV_data), n_ev)
    
    for (global_id, lat, long) in selected_EV_info:
        local_id = len(EVs)  # Local ID is the index in the deliveries array
        EVs.append(EV(local_id, global_id, lat, long, gamma))
    return EVs
    

def preProcess(base_file):
    # Read the CSV file
    # csv_file = 'combined_data.csv'  # Replace with your CSV file path
    csv_path = os.path.join("..", "data", "combined_data_{}.csv".format(base_file))  # Relative path
    data = pd.read_csv(csv_path)
    
    
    raw_CP_data = set()
    raw_EV_data = set()
    
    for index, row in data.iterrows():
        lat = row['lat']
        long = row['lng']
        global_id = row['ID']  # Assuming 'index' column is the global ID

        if row['type'] == 'c':  # EV
            raw_EV_data.add((global_id, lat, long))
            
        elif row['type'] == 'd' or row['type'] == 'f':  # CP
            raw_CP_data.add((global_id, lat, long))
    
    
    # time_matrix and dist are the dictionary where key is the tuple of 2 global IDs
    # Although the dist in the .csv is in Km, we scale it down and consider it in mile (we do not do real conversion here). 
    dist_matrix = {}
    time_matrix = {}
    dist_file_path = os.path.join("..", "data", "distance_matrix_{}.csv".format(base_file))  # Relative path
    df = pd.read_csv(dist_file_path, index_col=0)

    # Convert to dictionary with (x, y) as key and distance as value
    dist_matrix = {(int(row), int(col)): (float(df.loc[row, col])/1000)/15  # scaled down by 1/15
                     for row in df.index
                     for col in df.columns} # Store distance in Km

    duration_file_path = os.path.join("..", "data", "time_matrix_{}.csv".format(base_file))  # Relative path
    df_dur = pd.read_csv(duration_file_path, index_col=0)
    # Convert to duration with (x, y) as key and distance as value
    time_matrix = {(int(row), int(col)): float(df_dur.loc[row, col])/15 # scaled down by 1/15
                     for row in df_dur.index
                     for col in df_dur.columns} # Store travel duration in min


    
    # return CPs, EVs, dist_matrix, time_matrix
    return raw_CP_data, raw_EV_data, dist_matrix, time_matrix

