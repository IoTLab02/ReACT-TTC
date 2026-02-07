
from math import pow

def compute_satisfaction_score(initial_rank, current_rank, alpha, L = 2, beta=0.5, linear=False):
    if initial_rank == 0 or current_rank>initial_rank:   # we can avoid -ve z by adding if current_rank>initial_rank then 0
        return 0

    z = (initial_rank - current_rank) / initial_rank   # When the rank starts from 1, then z = (initial_rank - current_rank) / (initial_rank - 1)

    if linear == False:
        # print("Linear false:", linear, "z: ", z)
        if z >= 0:
            score = pow(z, alpha)
        else:
            score = (-1) * L * pow(-z, beta)
            # print("z: ", z, "score: ", score)
    else:
        # print("Linear true:", linear, "z: ", z)
        score = z
    return score

def compute_satisfaction_loss(initial_rank, current_rank, alpha, L = 2, beta=0.5, linear=False):
    current_satisfaction = compute_satisfaction_score(initial_rank, current_rank, alpha, L = 2, beta=0.5, linear=False)
    next_rank = current_rank + 1
    satisfaction_of_next_choice = compute_satisfaction_score(initial_rank, next_rank, alpha, L = 2, beta=0.5, linear=False)
    loss = current_satisfaction - satisfaction_of_next_choice
    return loss


# # Old formula
# def compute_satisfaction_score(initial_rank, current_rank, alpha, L = 2, beta=0.5, linear=False):
    
#     z = (1 - (current_rank + 1) / (initial_rank + 1))
#     # print("z: ", z, "current_rank: ", current_rank, "initial_rank: ", initial_rank)
#     if linear == False:
#         if z >= 0:
#             score = pow(z, alpha)
#         else:
#             score = (-1) * L * pow(-z, beta)
#             # print("z: ", z, "score: ", score)
#     else:
#         score = z
#     return score


"""
Simple measurement: lower value is better
"""
def evaluateAssignment_sum_of_assigned_indices(PrefList_onlyCPid, match_s):
    score = 0
    for s_i, assignedCP in match_s.items():
        # print("EV ID: ", s_i, " assignedCP: ",  assignedCP, " PrefList_onlyCPid[s_i]: ", PrefList_onlyCPid[s_i])
        if assignedCP != []:
            if assignedCP not in PrefList_onlyCPid[s_i]:    # assigned CP not in Pref list
                assigned_to_pref_index = len(PrefList_onlyCPid[s_i]) 
            else:
                assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
            
            # assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
            score = score + assigned_to_pref_index
        else:   # No CP assigned by the algo (It may happen with PCD, PCG, PCL)
            score = score + len(PrefList_onlyCPid[s_i]) # if not assigned, then it is assigned to null which is the last element in the pref list
        
    return score

    
def evaluateAssignment_total_satisfaction(PrefList_onlyCPid, match_s, EV_initial_matched_rank, alpha, linear=False):
    score = 0
    for s_i, assignedCP in match_s.items():
        initial_rank = EV_initial_matched_rank[s_i]
        assigned_to_pref_index = 9999
        # print("EV ID: ", s_i, " assignedCP: ",  assignedCP, " PrefList_onlyCPid[s_i]: ", PrefList_onlyCPid[s_i])
        if assignedCP != []:
            if assignedCP not in PrefList_onlyCPid[s_i]:    # assigned CP not in Pref list
                assigned_to_pref_index = len(PrefList_onlyCPid[s_i])
                
            else:
                assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
            # assigned_to_pref_index = PrefList_onlyCPid[s_i].index(assignedCP)
        else:
            assigned_to_pref_index = len(PrefList_onlyCPid[s_i]) # if not assigned, then it is assigned to null which is the last element in the pref list
        score = score + compute_satisfaction_score(initial_rank, assigned_to_pref_index, alpha, linear=linear)
    return score