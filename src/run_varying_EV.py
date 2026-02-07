import os


import time
import random
import csv

time_seed = time.time()
#random.seed(time_seed)
random.seed(123)
Debug = False


# from copy import deepcopy
# import json
from initialize import initialize, initialEndowment
from evaluate import evaluateAssignment_sum_of_assigned_indices, evaluateAssignment_total_satisfaction
from matching_at_RSU import match, PCG, PCD, PCL
# import networkx as nx
# from evaluate import compute_satisfaction_score
# from V2VDisCS import V2VDisCS
# from DAA import matchDAA
from reactTTC import initialize, compute_initial_matched_rank, ttc, run_baseline_PCD_PCG_PCL, run_matchDAA, run_V2VDisCS

if __name__ == "__main__":
    n_ev_max = 60   # considering n_ev are non-compliant
    alpha = 0.5 # required in prospect theory satisfaction formula
    linear = False # Linear satisfaction formula
    initial_endowment_method = PCL # we can use PCD, PCG, PCL
    q = 2
    max_itr = 10
    
    base_file = "jd200_1" # base file name
    csv_file = os.path.join("..", "results", "results_varying_EV.csv".format(base_file))
    

    for n_ev in range(15, n_ev_max + 1, 5):
        for itr in range(max_itr):
            print("\n Itr: ", itr, " n_ev: ", n_ev)
            ## Initialize
            ev_list, cp_list, Pref_full_tuples, PrefList_onlyCPid, dist_matrix, time_matrix  = initialize(base_file, n_ev, q)
            
            ## Initial Endowment
            initial_match_s, initial_match_c = initialEndowment(ev_list, cp_list, Pref_full_tuples, initial_endowment_method)    
            
            EV_initial_matched_rank = compute_initial_matched_rank(PrefList_onlyCPid, initial_match_s)
            
            
            ## Run TTC: n_ev, ev_list, cp_list, PrefList_onlyCPid, initial_match_s, initial_match_c, EV_initial_matched_rank, alpha, linear=False
            start_time = time.time()
            final_match_s = ttc(n_ev, ev_list, cp_list, PrefList_onlyCPid, initial_match_s, initial_match_c, EV_initial_matched_rank, alpha, linear)
            end_time = time.time()
            elapsed_time_TTC = (end_time - start_time) * 1000
            match_s_TTC = dict(sorted(final_match_s.items()))
            
            ## Run baselines
            start_time = time.time()
            match_s_PCD, match_c_PCD = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCD)    
            end_time = time.time()
            elapsed_time_PCD = (end_time - start_time) * 1000
            
            
            start_time = time.time()
            match_s_PCG, match_c_PCG = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCG)    
            end_time = time.time()
            elapsed_time_PCG = (end_time - start_time) * 1000
            
            start_time = time.time()
            match_s_PCL, match_c_PCL = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCL)  
            end_time = time.time()
            elapsed_time_PCL = (end_time - start_time) * 1000
            
            
            n_cp = len(cp_list)
            start_time = time.time()
            match_s_V2VDis, match_c_V2VDis = run_V2VDisCS(n_ev, n_cp, ev_list, cp_list, q, time_matrix, dist_matrix)
            end_time = time.time()
            elapsed_time_V2VDis = (end_time - start_time) * 1000
            
            start_time = time.time()
            match_s_DAA, match_c_DAA = run_matchDAA(ev_list, cp_list, PrefList_onlyCPid, dist_matrix, time_matrix, q)
            end_time = time.time()
            elapsed_time_DAA = (end_time - start_time) * 1000
            
            
            ## Evaluation:: sum_of_assigned_indices
            print("Initial Endowment computed using: ", initial_endowment_method)
            print("::Sum of assigned indices (lower score means better choice)::")
            
            score_TTC_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_TTC)
            print("TTC score: ", score_TTC_SI)
            
            # PCD
            score_PCD_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCD)
            print("PCD score: ", score_PCD_SI)
            
            # PCG
            score_PCG_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCG)
            print("PCG score: ", score_PCG_SI)
            
            # PCL
            score_PCL_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCL)
            print("PCL score: ", score_PCL_SI)
            
            # V2VDis
            score_V2VDis_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_V2VDis)
            print("V2VDis score: ", score_V2VDis_SI)
            
            # DAA
            score_DAA_SI = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_DAA)
            print("DAA score: ", score_DAA_SI)
            
            
            ## Evaluation:: total_satisfaction Linear
            print("::Total satisfaction Linear (higher score means better choice)::")
            
            score_TTC_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_TTC, EV_initial_matched_rank, alpha, linear=True)
            print("TTC score: ", score_TTC_TS_Lin)
            
            # PCD
            score_PCD_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCD, EV_initial_matched_rank, alpha, linear=True)
            print("PCD score: ", score_PCD_TS_Lin)
            
            # PCG
            score_PCG_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCG, EV_initial_matched_rank, alpha, linear=True)
            print("PCG score: ", score_PCG_TS_Lin)
            
            # PCL
            score_PCL_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCL, EV_initial_matched_rank, alpha, linear=True)
            print("PCL score: ", score_PCL_TS_Lin)
            
            # V2VDis
            score_V2VDis_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_V2VDis, EV_initial_matched_rank, alpha, linear=True)
            print("V2VDis score: ", score_V2VDis_TS_Lin)
            
            # DAA
            score_DAA_TS_Lin = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_DAA, EV_initial_matched_rank, alpha, linear=True)
            print("DAA score: ", score_DAA_TS_Lin)
            
            ## Evaluation:: total_satisfaction
            print("::Total satisfaction Prospect Theory Function (higher score means better choice)::")
            
            score_TTC_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_TTC, EV_initial_matched_rank, alpha)
            print("TTC score: ", score_TTC_TS_PT)
            
            # PCD
            score_PCD_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCD, EV_initial_matched_rank, alpha)
            print("PCD score: ", score_PCD_TS_PT)
            
            # PCG
            score_PCG_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCG, EV_initial_matched_rank, alpha)
            print("PCG score: ", score_PCG_TS_PT)
            
            # PCL
            score_PCL_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCL, EV_initial_matched_rank, alpha)
            print("PCL score: ", score_PCL_TS_PT)
            
            # V2VDis
            score_V2VDis_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_V2VDis, EV_initial_matched_rank, alpha)
            print("V2VDis score: ", score_V2VDis_TS_PT)
            
            # DAA
            score_DAA_TS_PT = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_DAA, EV_initial_matched_rank, alpha)
            print("DAA score: ", score_DAA_TS_PT)
            
            
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
            
                # Write the header only if the file doesn't exist
                if not file_exists:
                    writer.writerow(['itr', 'Initial Endowment', 'Method', 'Total EV', 'CP Queue', 'execution time', 'Sum of assigned indices', 'Total satisfaction Linear', 'Total satisfaction PT' ])
                
                writer.writerow([itr, initial_endowment_method, 'ReACT-TTC', n_ev, q, elapsed_time_TTC, score_TTC_SI, score_TTC_TS_Lin, score_TTC_TS_PT])
                writer.writerow([itr, initial_endowment_method, 'PCD', n_ev, q, elapsed_time_PCD, score_PCD_SI, score_PCD_TS_Lin, score_PCD_TS_PT])
                writer.writerow([itr, initial_endowment_method, 'PCG', n_ev, q, elapsed_time_PCG, score_PCG_SI, score_PCG_TS_Lin, score_PCG_TS_PT])
                writer.writerow([itr, initial_endowment_method, 'PCL', n_ev, q, elapsed_time_PCL, score_PCL_SI, score_PCL_TS_Lin, score_PCL_TS_PT])
                writer.writerow([itr, initial_endowment_method, 'V2VDis', n_ev, q, elapsed_time_V2VDis, score_V2VDis_SI, score_V2VDis_TS_Lin, score_V2VDis_TS_PT])
                writer.writerow([itr, initial_endowment_method, 'DAA', n_ev, q, elapsed_time_DAA, score_DAA_SI, score_DAA_TS_Lin, score_DAA_TS_PT])