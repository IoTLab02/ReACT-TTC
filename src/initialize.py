import os




from helper import preProcess, create_EVobjects, create_CPobjects, debug_print
import time
import random
import csv
import json
import pickle
from matching_at_RSU import match, PCG, PCD, PCL



time_seed = time.time()
#random.seed(time_seed)
random.seed(123)
Debug = False

"""
n_ev: No. of non-compliant EVs
n_cp_in_fast: No. of Fast In-network Charging Points
n_cp_in_regular: No. of Regular In-network Charging Points
n_cp_out_fast: No. of Fast Partner-network Charging Points
n_cp_out_regular: No. of Regular Partner-network Charging Points
q: Queue size at CP
gamma: SLA time for EVs  (Keeping fixed in TTC paper)

"""
def initialize(base_file, n_ev, q = 2, n_cp_in_fast = 5, n_cp_in_regular = 10, n_cp_out_fast = 5, n_cp_out_regular = 10, gamma = 25):   
    # # user input
    # n_ev_min = 30
    # n_ev_max = 60
    # n_cp_in_fast = 5
    # n_cp_in_regular = 10
    # n_cp_out_fast = 5
    # n_cp_out_regular = 10
    # q = q # quota of each CP
    # max_itr = 10 # maximum iteration
    # csv_file = 'results_NoChOrder_varying_EV_4.csv'
    # n_ev = 10 # number of EVs
    
    # b1 = 5
    # b2 = 5
    
    # base_file = "jd200_1" # base file name
    # csv_file = os.path.join("..", "results", "results_NoChOrder_varying_EV_4.csv".format(base_file))
    
    # Initialize Charging points (Static for the whole experiment)
    raw_CP_data, raw_EV_data, dist_matrix, time_matrix = preProcess(base_file)
    
    # Initialize Charging points (Static for the whole experiment)
    cp_list = create_CPobjects(raw_CP_data, n_cp_in_fast, n_cp_in_regular, n_cp_out_fast, n_cp_out_regular, q)
    
    
    ev_list = create_EVobjects(raw_EV_data, n_ev, gamma) # create list of EVs
    Pref = {}
    for ev in ev_list:
        #ev.compute_preference(cp_list) # SMEVCA preference
        ev.compute_preference_new(cp_list, dist_matrix, time_matrix) # New Preference
        Pref[ev.ID] = ev.pref
        #print(ev.ID, " => ", ev.pref) 
        
        
    

    # write the whole preference list in a JSON file for SMEVCA extension and other baselines
    with open("pref_full.json", "w", encoding="utf-8") as f:
        for ev_id, items in Pref.items():
            json.dump({"id": ev_id, "pref": items}, f)  # tuples become lists here
            f.write("\n")
    
    # Read the preference list from the JSON file
    # Pref2 = {}
    # with open("pref_full.json", "r", encoding="utf-8") as f:
    #     for line in f:
    #         rec = json.loads(line)
    #         Pref2[rec["id"]] = [tuple(t) for t in rec["pref"]]  # convert lists back to tuples

    
    # Store the preferred CP IDs for EV (only for TTC)
    PrefList_onlyCPid = {int(ev_id): [t[0] for t in tup_list] for ev_id, tup_list in Pref.items()} 
    
    # write preference list in a JSON file
    with open("pref_onlyCPid.json", "w", encoding="utf-8") as f:
        json.dump(PrefList_onlyCPid, f)

            
    # # Read the preference list from the JSON file
    # PrefList_onlyCPid2 = {}
    # with open("pref_onlyCPid.json", "r", encoding="utf-8") as f:
    #     PrefList_onlyCPid2 = {int(k): v for k, v in json.load(f).items()}
    
    
    # Dump all the EV and CP lists for the baselines
    # --- dump ---
    with open("ev_list.pkl", "wb") as f:
        pickle.dump(ev_list, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # --- load ---
    # with open("ev_list.pkl", "rb") as f:
    #     ev_list2 = pickle.load(f)
    
    return ev_list, cp_list, Pref, PrefList_onlyCPid, dist_matrix, time_matrix

# matching_fn can be PCD, PCG or PCL
def initialEndowment(ev_list, cp_list, Pref, matching_fn):
    # Initial assignment (We can use PCG, PCD or PCL)
    matched_s, matched_c = match(ev_list, cp_list, Pref, matching_fn)
    # print(matched_s) # contains {si: c_j, ...}
    # print(matched_c) # contains {cj: (s_i, t1_ij, psi_ij, delta_ij),...} 
    assignedEVs_at_CP = {}
    for c_j, si_list in matched_c.items():
        assigned_si_set = set() 
        for si_tuple in si_list:
            assigned_si_set.add(si_tuple[0])
        assignedEVs_at_CP[c_j] = assigned_si_set
    return matched_s, assignedEVs_at_CP


    

if __name__ == "__main__":
    n_ev = 50
    ev_list, cp_list, Pref_full_tuples, PrefList_onlyCPid,  = initialize(n_ev)
    initial_match_s, initial_match_c = initialEndowment(ev_list, cp_list, Pref_full_tuples, PCL)
    # evaluateAssignment(PrefList_onlyCPid, initial_match_s)
    
    

            
    
    
  