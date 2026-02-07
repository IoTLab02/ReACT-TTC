
from copy import deepcopy
from collections import Counter
import json
from initialize import initialize, initialEndowment
from evaluate import evaluateAssignment_sum_of_assigned_indices, evaluateAssignment_total_satisfaction
from matching_at_RSU import match, PCG, PCD, PCL
import networkx as nx
from evaluate import compute_satisfaction_score, compute_satisfaction_loss
from V2VDisCS import V2VDisCS
from DAA import matchDAA

def delete_pref_element(PrefList_onlyCPid_local, target, next_preference):
    for k, lst in PrefList_onlyCPid_local.items():
        next_preferred_index = next_preference[k]
        
        # delete the CP from Pref list only if it is not already traversed. Otherwise, it will lead to wrong index and wrong result
        PrefList_onlyCPid_local[k] = lst[:next_preferred_index] + [v for v in lst[next_preferred_index :] if v != target] 
    return PrefList_onlyCPid_local

def update_queue_at_CP(cp_list, initial_match_c):
    for c, assigned_evs in initial_match_c.items():
        cp_list[c].q = cp_list[c].q - len(assigned_evs)

def compute_initial_matched_rank(PrefList_onlyCPid, initial_match_s):
    initial_matched_rank = {}
    for s_i, assignedCP in initial_match_s.items():
        if assignedCP != []:
            # if assignedCP not in PrefList_onlyCPid[s_i]:    # assigned CP not in Pref list
            #     assigned_to_pref_index = len(PrefList_onlyCPid[s_i])
            #     print("EV ID: ", s_i, " assignedCP: ",  assignedCP, " PrefList_onlyCPid[s_i]: ", PrefList_onlyCPid[s_i])
                
            # else:
            #     assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
            
            assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
            initial_matched_rank[s_i] = assigned_to_pref_index
        else:
            initial_matched_rank[s_i] = len(PrefList_onlyCPid[s_i]) # if not assigned, then it is assigned to null which is the last element in the pref list
        
    return initial_matched_rank

def resolve_cycle(cycle, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, cp_list_copy):
    for i in range(len(cycle)):
        u = cycle[i]
        v = cycle[(i+1)%len(cycle)]
        current_CP_of_v = current_match_participant_EV[v]
        
        # print("u:",u,"v",v, " current_CP_of_v:", current_CP_of_v)
        if current_CP_of_v != []:   # This check is required for initial empty assignments for EVs
            current_match_CP[current_CP_of_v].remove(v)
            if u >= n_ev:
                cp_list_copy[current_CP_of_v].q = cp_list_copy[current_CP_of_v].q + 1 # update the q
                
        if u < n_ev: # u is not a virtual vertex
            final_match_s[u] = current_CP_of_v
            # current_match_CP[current_CP_of_v].add(u)  # We should not add as u will not participate in the G anymore
            participants.remove(u)
            # We don't need to update queue size q at CP as we already computed the updated queue size at the beginning of the ttc function
            
    
def resolve_all_cycles(all_cycles, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, G, cp_list_copy):
    if len(all_cycles) != 0:
        vertices_in_cycles = [item for sublist in all_cycles for item in sublist]
        
        # filter the overlapping vertices
        overlapping_vertices = [item for item, count in Counter(vertices_in_cycles).items() if count > 1]
        
        # filter the overlapping and non-overlapping cycles
        nonoverlapping_cycles = [sub for sub in all_cycles if not set(overlapping_vertices).intersection(sub)]
        overlapping_cycles = [sub for sub in all_cycles if sub not in nonoverlapping_cycles]
            

        total_sat_loss_overlapping_cycles = []
        for cycle in overlapping_cycles:
            loss = 0
            for i in range(len(cycle)):
                u = cycle[i-1]
                v = cycle[i]
                if u >= n_ev: # There should not be any edge from virtual vertex to any other vertex
                    continue
                if v in overlapping_vertices:
                    # print("u:", u, " v:", v, "edges:", G.edges())
                    loss = loss + G[u][v]['weight']
            
            total_sat_loss_overlapping_cycles.append(loss)
            
        overlapping_cycles_sorted = [val for _, val in sorted(zip(total_sat_loss_overlapping_cycles, overlapping_cycles))]
        
        
        # Resolve non-overlapping cycles
        for cycle in nonoverlapping_cycles:
            resolve_cycle(cycle, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, cp_list_copy)
            G.remove_nodes_from(cycle)
            
        # Resolve overlapping cycles
        deleted_vertices_from_overlapping_cycle = []
        for cycle in overlapping_cycles_sorted:
            if set(deleted_vertices_from_overlapping_cycle).intersection(cycle):
                continue
            resolve_cycle(cycle, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, cp_list_copy)
            deleted_vertices_from_overlapping_cycle = deleted_vertices_from_overlapping_cycle + cycle
            # real_vertices_in_cycle = [v for v in cycle if v < n_ev]
            G.remove_nodes_from(cycle)
    
    
def ttc(n_ev, ev_list, cp_list, PrefList_onlyCPid, initial_match_s, initial_match_c, EV_initial_matched_rank, alpha, linear=False):
    
    cp_list_copy = deepcopy(cp_list)
    update_queue_at_CP(cp_list_copy, initial_match_c)
    participants = [x.ID for x in ev_list]
    cp_id_list = [x.ID for x in cp_list_copy]
    current_match_participant_EV = deepcopy(initial_match_s)
    EV_initial_matched_rank = deepcopy(EV_initial_matched_rank) # stores the index of assigned CP in the pref list
    current_match_CP = deepcopy(initial_match_c)
    final_match_s = {}
    PrefList_onlyCPid_local = deepcopy(PrefList_onlyCPid)
    next_preference = {participant: 0 for participant in participants} #     

    
    G = nx.DiGraph()
    G.add_nodes_from(participants, tag="real")
    next_virtual_node_id = n_ev
    # cp_to_virtual_node_map = {x.ID:[] for x in cp_list_copy } # NOT required
    participants_num = len(participants)
    
    while len(final_match_s) < participants_num:
        
        # Test
        # print("participants: ", participants)
        # print("graph: ", G.edges())
        # weights = nx.get_edge_attributes(G, "weight")
        # print(weights)

        # Create the graph for an iteration
        for participant in participants:
            if len(sorted(G.successors(participant))) > 0: # if the node has outgoing edge, then skip  
                continue
            
            
            assignedCP = current_match_participant_EV[participant]
            next_preferred_index = next_preference[participant] # index for the nrext preferrence in pref list
            
            if next_preferred_index >= len(PrefList_onlyCPid_local[participant]): # if the preference list is exhausted (this check is required for incomplete set of preferences)
                final_match_s[participant] = assignedCP
                participants.remove(participant)
                G.remove_node(participant)
                continue
            
            preferred_CP = PrefList_onlyCPid_local[participant][next_preferred_index]
            
            if assignedCP == preferred_CP: # if the preferred CP is already assigned
                final_match_s[participant] = assignedCP
                participants.remove(participant)
                G.remove_node(participant)
                continue
            
            # satisfaction = compute_satisfaction_score(EV_initial_matched_rank[participant], next_preferred_index, alpha, linear)
            
            # reduction in satisfaction score if we need to go to the next preference from the preferred_CP
            satisfaction_loss = compute_satisfaction_loss(EV_initial_matched_rank[participant], next_preferred_index, alpha, linear)
               
            next_preference[participant] = next_preferred_index + 1
            
            
            
            # Virtual node insertion: 
            if cp_list_copy[preferred_CP].q > 0: # If the preferred CP has empty space
                G.add_node(next_virtual_node_id, tag="virtual", cp=preferred_CP)
                cp_list_copy[preferred_CP].q = cp_list_copy[preferred_CP].q - 1 # reduce the q as a virtual ev is assigned to the CP
                current_match_CP[preferred_CP].add(next_virtual_node_id)
                current_match_participant_EV[next_virtual_node_id] = preferred_CP
                # G.add_edge(participant, next_virtual_node_id, weight=satisfaction_loss)
                next_virtual_node_id = next_virtual_node_id + 1
                
            # Add edges to all EVs currently assigned to preferred_CP (including virtual nodes)
            G.add_weighted_edges_from(([(participant, e, satisfaction_loss) for e in current_match_CP[preferred_CP] if e in G.nodes()]))
                
        
        # Find the cycles (Use the terms : complete cycles)
        all_cycles = sorted(nx.simple_cycles(G))
        resolve_all_cycles(all_cycles, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, G, cp_list_copy)
        
        
                
        
        # Find chains to the virtual vertices (incomplete cycles)
        source_vertices = [v for v in G.nodes if G.in_degree(v) == 0]
        target_vertices = [v for v in G.nodes if v >= n_ev]
        all_chains = []
        if len(target_vertices) > 0 and len(source_vertices) > 0:
            for target in target_vertices:
                for source in source_vertices:
                    paths = list(nx.all_simple_paths(G, source=source, target=target))
                    all_chains.extend(paths)
        
        if len(all_chains) > 0:
            resolve_all_cycles(all_chains, current_match_participant_EV, current_match_CP, participants, final_match_s, n_ev, G, cp_list_copy)
               
                    
         
        
                
        
        # remove the CPs (with q = 0) from the preference list if they have EVs that are not in the graph, that means they got final assignment
        for c in cp_id_list:
            if cp_list_copy[c].q <= 0:
                participating_evs_at_c = [e for e in current_match_CP[c] if e in G.nodes()]
                
                if len(participating_evs_at_c) == 0:
                    # print("deleting CP: ", c, " EVs at it: ", current_match_CP[c] )
                    delete_pref_element(PrefList_onlyCPid_local, c, next_preference)
                    
                    
    return final_match_s



def run_baseline_PCD_PCG_PCL(ev_list1, cp_list1, Pref1, matching_fn):
    # Initial assignment (We can use PCG, PCD or PCL)
    ev_list = deepcopy(ev_list1)
    cp_list = deepcopy(cp_list1)
    Pref = deepcopy(Pref1)
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

def run_V2VDisCS(n_ev, n_cp, ev_list1, cp_list1, q, time_matrix, dist_matrix):
    ev_list = deepcopy(ev_list1)
    cp_list = deepcopy(cp_list1)
    match_s_V2VDis, match_c_V2VDis = V2VDisCS(n_ev, n_cp, ev_list, cp_list, q, time_matrix, dist_matrix)
    return match_s_V2VDis, match_c_V2VDis

def run_matchDAA(ev_list1, cp_list1, PrefList_onlyCPid1, dist_matrix, time_matrix, q):
    ev_list = deepcopy(ev_list1)
    cp_list = deepcopy(cp_list1)
    PrefList_onlyCPid = deepcopy(PrefList_onlyCPid1)
    match_s_DAA, match_c_DAA = matchDAA(ev_list, cp_list, PrefList_onlyCPid, dist_matrix, time_matrix, q)
    return match_s_DAA, match_c_DAA

if __name__ == "__main__":
    n_ev = 50   # considering n_ev are non-compliant
    alpha = 0.5 # required in prospect theory satisfaction formula
    linear = False # Linear satisfaction formula
    initial_endowment_method = PCD # we can use PCD, PCG, PCL
    q = 2
    base_file = "jd200_1" # base file name
    
    ## Initialize
    ev_list, cp_list, Pref_full_tuples, PrefList_onlyCPid, dist_matrix, time_matrix  = initialize(base_file, n_ev, q)
    
    ## Initial Endowment
    initial_match_s, initial_match_c = initialEndowment(ev_list, cp_list, Pref_full_tuples, initial_endowment_method)    
    
    EV_initial_matched_rank = compute_initial_matched_rank(PrefList_onlyCPid, initial_match_s)
    
    
    ## Run TTC: n_ev, ev_list, cp_list, PrefList_onlyCPid, initial_match_s, initial_match_c, EV_initial_matched_rank, alpha, linear=False
    final_match_s = ttc(n_ev, ev_list, cp_list, PrefList_onlyCPid, initial_match_s, initial_match_c, EV_initial_matched_rank, alpha, linear)
    sorted_final_match_s = dict(sorted(final_match_s.items()))
    
    
    ## Run baselines
    match_s_PCD, match_c_PCD = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCD)    
    match_s_PCG, match_c_PCG = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCG)    
    match_s_PCL, match_c_PCL = run_baseline_PCD_PCG_PCL(ev_list, cp_list, Pref_full_tuples, PCL)  
    
    n_cp = len(cp_list)
    match_s_V2VDis, match_c_V2VDis = run_V2VDisCS(n_ev, n_cp, ev_list, cp_list, q, time_matrix, dist_matrix)
    
    match_s_DAA, match_c_DAA = run_matchDAA(ev_list, cp_list, PrefList_onlyCPid, dist_matrix, time_matrix, q)
    
    ## Evaluation:: sum_of_assigned_indices
    print("Initial Endowment computed using: ", initial_endowment_method)
    print("::Sum of assigned indices (lower score means better choice)::")
    
    score_TTC = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, sorted_final_match_s)
    print("TTC score: ", score_TTC)
    
    # PCD
    score_PCD = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCD)
    print("PCD score: ", score_PCD)
    
    # PCG
    score_PCG = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCG)
    print("PCG score: ", score_PCG)
    
    # PCL
    score_PCL = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_PCL)
    print("PCL score: ", score_PCL)
    
    # V2VDis
    score_V2VDis = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_V2VDis)
    print("V2VDis score: ", score_V2VDis)
    
    # DAA
    score_DAA = evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s_DAA)
    print("DAA score: ", score_DAA)
    
    
    ## Evaluation:: total_satisfaction Linear
    print("::Total satisfaction Linear (higher score means better choice)::")
    
    score_TTC = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, sorted_final_match_s, EV_initial_matched_rank, alpha, linear=True)
    print("TTC score: ", score_TTC)
    
    # PCD
    score_PCD = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCD, EV_initial_matched_rank, alpha, linear=True)
    print("PCD score: ", score_PCD)
    
    # PCG
    score_PCG = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCG, EV_initial_matched_rank, alpha, linear=True)
    print("PCG score: ", score_PCG)
    
    # PCL
    score_PCL = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCL, EV_initial_matched_rank, alpha, linear=True)
    print("PCL score: ", score_PCL)
    
    # V2VDis
    score_V2VDis = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_V2VDis, EV_initial_matched_rank, alpha, linear=True)
    print("V2VDis score: ", score_V2VDis)
    
    # DAA
    score_DAA = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_DAA, EV_initial_matched_rank, alpha, linear=True)
    print("DAA score: ", score_DAA)
    
    ## Evaluation:: total_satisfaction
    print("::Total satisfaction Prospect Theory Function (higher score means better choice)::")
    
    score_TTC = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, sorted_final_match_s, EV_initial_matched_rank, alpha)
    print("TTC score: ", score_TTC)
    
    # PCD
    score_PCD = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCD, EV_initial_matched_rank, alpha)
    print("PCD score: ", score_PCD)
    
    # PCG
    score_PCG = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCG, EV_initial_matched_rank, alpha)
    print("PCG score: ", score_PCG)
    
    # PCL
    score_PCL = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_PCL, EV_initial_matched_rank, alpha)
    print("PCL score: ", score_PCL)
    
    # V2VDis
    score_V2VDis = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_V2VDis, EV_initial_matched_rank, alpha)
    print("V2VDis score: ", score_V2VDis)
    
    # DAA
    score_DAA = evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s_DAA, EV_initial_matched_rank, alpha)
    print("DAA score: ", score_DAA)

