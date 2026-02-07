import numpy as np
import pandas as pd
import math


def V2VDisCS(n_ev, n_cp, ev_list, cp_list, q, time_matrix, dist_matrix):
    
    matched_s = {} # matched dictionary for EV
    matched_c = {} # matched dictionary for CP
    for s in ev_list:
        s_i = s.ID
        matched_s[s_i] = []
    for c in cp_list:
        c_i = c.ID
        matched_c[c_i] = []
    
    N_Donor = n_cp
    N_Acceptor = n_ev
    
    
    # Set large values only where the pair is reachable
    T_max = np.max([math.floor(time_matrix[(e_i.global_ID, c_j.global_ID)]) for e_i in ev_list for c_j in cp_list])
    Cu_max = np.max([c_j.ucost for c_j in cp_list])
    # R_max = 1   # We consider reliability is 1 for all CPs
    rate_max = np.max([c_j.r_j for c_j in cp_list])
    # charge_max = np.max(charge_req) # Not required as a CP can provide the full charge if required
    
    # Initialize score and rank matrices
    Scores = np.full((N_Acceptor, N_Donor), np.inf)
    # Ranks = np.full((N_Acceptor, N_Donor), np.inf)
    
    # Generate per-acceptor random weights for 5 criteria, normalized to sum to 1
    Weights = np.random.rand(N_Acceptor, 5)
    Weights = Weights / Weights.sum(axis=1, keepdims=True)  # Normalize rows
    
    # Calculate normalized scores for reachable donor–acceptor pairs
    for i in range(N_Acceptor):
        w = Weights[i]  # weight vector for current acceptor
        for j in range(N_Donor):
            # if reachable[i, j]:
            norm_Cu = cp_list[j].ucost / Cu_max
            norm_T = math.floor(time_matrix[(ev_list[i].global_ID, cp_list[j].global_ID)]) / T_max
            # norm_R = R_min[j] / R_max
            norm_R = 1  # All CPs are reliable
            norm_rate = cp_list[j].r_j / rate_max
            #norm_charge = charge_req[j] / charge_max
            norm_charge = 1 # considered 1 as unlike V2V doner, all CP can provide the full charge.

            # Weighted score (lower is better)
            Scores[i, j] = (norm_Cu * w[0] +
                            norm_R * w[1] +
                            norm_rate * w[2] +
                            norm_T * w[3] +
                            norm_charge * w[4])
        
    
    
    for i in range(N_Acceptor):
        donor_scores = [(j, Scores[i, j]) for j in range(N_Donor)]
        donor_scores_sorted = sorted(donor_scores, key=lambda x: x[1])  # Sort by score
        for (j, score) in donor_scores_sorted:
            if len(matched_c[j]) < q:
                ev = ev_list[i]
                cp = cp_list[j]
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
                
                tuple_s = (i, t1_ij, psi_ij, delta_ij)
                matched_c[j].append(tuple_s)  # tuple_s = (s_i, t1_ij, psi_ij, delta_ij) 
                matched_s[i] = j
                break
    return matched_s, matched_c
    
