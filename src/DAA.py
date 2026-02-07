import math


def generatePrefForCP(ev_list, cp_list, dist_matrix):
    pref_cp = {cp.ID: [] for cp in cp_list}
    
    for cp in cp_list:
        for ev in ev_list:
            charge_desired = ev.alpha * ev.B_full
            B_ij = ev.B_res - (dist_matrix[(ev.global_ID, cp.global_ID)]) /ev.m # remaining charge after reaching c_j
            if B_ij <= 0:
                continue
            psi_ij = charge_desired - B_ij 
            pref_cp[cp.ID].append((ev.ID, psi_ij))
        pref_cp[cp.ID].sort(key=lambda x: x[1], reverse=True) # Sort by score
        pref_tmp = [prefTuple[0] for prefTuple in pref_cp[cp.ID]] # capture only EV ID
        pref_cp[cp.ID] = pref_tmp
    return pref_cp
        
        
# def generatePrefForEV(ev_list, cp_list, dist_matrix, time_matrix):
#     pref_ev = {}
#     #print("Preference list of EV (CP ID, Distance d_ij, time to reach t0_ij, psi, r_i, gamma):")
#     for ev in ev_list:
#         ev.compute_preference(cp_list, dist_matrix, time_matrix)
#         # ev.compute_preference_new(cp_list, dist_matrix, time_matrix, beta1=1, beta2=1)
#         pref_ev[ev.ID] = ev.pref
#         pref_tmp = [prefTuple[0] for prefTuple in pref_ev[ev.ID]] # capture only CP ID
#         pref_ev[ev.ID] = pref_tmp
#     return pref_ev
    
    
        
        
def matchDAA(ev_list, cp_list, pref_e, dist_matrix, time_matrix, q):
    pref_c = generatePrefForCP(ev_list, cp_list, dist_matrix)   # pref ov CPs
    # pref_e = generatePrefForEV(ev_list, cp_list, dist_matrix, time_matrix)  # pref of EVs
    
    
    cp_ids = [cp.ID for cp in cp_list]  #equivalent to u
    ev_ids = [ev.ID for ev in ev_list]  #equivalent to f
    
    # initialization of the matched dictionary
    matched_c = {}
    matched_e = {}
    for c_i in cp_ids:
        matched_c[c_i] = []
    for e_i in ev_ids:
        matched_e[e_i] = []
    
    unmatched = ev_ids.copy()
    while len(unmatched) > 0:
        unmatched_e = unmatched.copy()
        unmatched = []
        for e_i in unmatched_e:
            pref = pref_e[e_i]
            if len(pref) == 0:
                continue
            for c_i in pref:
                #print(c_i,"\n")
                pref_e[e_i].remove(c_i)
                # if there is capacity for the acceptors/rejectors, match them
                if len(matched_c[c_i]) < cp_list[c_i].q:
                    matched_c[c_i].append(e_i)
                    matched_e[e_i]=c_i
                    break
                    
                # else if capacity is full, check for replacement 
                # based on the preference of the worst assigned proposer and 
                # the incoming proposer
                else:
                    worst_index_in_pref = -1
                    worst_index_in_matched = -1
                    # find the index of worst assigned proposer 
                    # in the matched list 
                    # by traversing it in reverse order
                    for e_r in reversed(pref_c[c_i]):
                        if e_r in matched_c[c_i]:
                            worst = e_r
                            worst_index_in_pref = pref_c[c_i].index(worst)
                            worst_index_in_matched = matched_c[c_i].index(worst)
                            break
                    # if proposer is in the preference list of acceptor/rejector
                    if e_i in pref_c[c_i]:
                        # if the proposer has high preference (lower index) then
                        # replace the worst assigned proposer in the matched list 
                        # of the acceptor/rejector
                        if pref_c[c_i].index(e_i) < worst_index_in_pref:
                            e_removed = matched_c[c_i][worst_index_in_matched]
                            unmatched.append(e_removed)
                            matched_c[c_i][worst_index_in_matched] = e_i
                            matched_e[e_i] = [c_i]
                            break
                        
                        
    for  c_j in cp_ids:   
        ev_at_c = matched_c[c_j]
        matched_c[c_j] = []             
        for e_i in ev_at_c:
            ev = ev_list[e_i]
            cp = cp_list[c_j]
            # compute req. charge at jth CP
            charge_desired = ev.alpha * ev.B_full
            B_ij = ev.B_res - (dist_matrix[(ev.global_ID, cp.global_ID)]) /ev.m # remaining charge after reaching c_j
            if B_ij <= 0:
                continue
            psi_ij = charge_desired - B_ij 
            
            
            delta_ij = 0 # effective maximum allowed duration for charging that satisfies SLA
            t1_ij = math.ceil(psi_ij/ min(ev.r_i, cp.r_j)) # time to recharge the EV
            t0_ij = math.floor(time_matrix[(ev.global_ID, cp.global_ID)])
            if cp.t_free_j > t0_ij:
                delta_ij = t1_ij + ev.gamma - (cp.t_free_j - t0_ij)
            else:
                delta_ij = t1_ij + ev.gamma
            
            tuple_s = (e_i, t1_ij, psi_ij, delta_ij)
            matched_c[c_j].append(tuple_s)  # tuple_s = (s_i, t1_ij, psi_ij, delta_ij) 
    return matched_e, matched_c