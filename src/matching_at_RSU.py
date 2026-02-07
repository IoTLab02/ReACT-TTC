
from agents import EV, CP
from typing import List, Dict, Any
import random
import math
import copy

import time

time_seed = time.time()
# random.seed(time_seed)
random.seed(123)


# random preference
def randomChoice(L, q):
    """
    Parameters
    ----------
    L : A list of candidates.
        It is a list of tuples (s_i, t1_ij, psi_ij, delta_ij)
    q : int
        Effective quota for c_j.

    Returns
    -------
    Assignment of EV for c_j. Maintains the sequence.
    Each assignment is a list of tuples (s_i, t1_ij, psi_ij, delta_ij).

    """
    coalition = []
    for i in range(q):
        if len(L) > 0:
            x = random.choice(L)
            coalition.append(x)
            L.remove(x)
    #print("coalition: ", coalition)
    return coalition


def computeUtility(A):
    """
    Find the utility of an assignment set A
    """
    min_delta = 9999
    total_charging_time = 0
    utility = 0
    #tuple_s: (s_i, t1_ij, psi_ij, delta_ij)
    for tuple_s in A:
        delta = tuple_s[3]
        if delta < min_delta:
            min_delta = delta
        total_charging_time = total_charging_time + tuple_s[1]
    Delta_r = min_delta - total_charging_time
    if Delta_r >= 0:
        for tuple_s in A:
            utility = utility + tuple_s[2]/tuple_s[3]
    else:
        for tuple_s in A:
            utility = utility - tuple_s[3]/tuple_s[2]
    return utility
        
    

# Local preferred coalition
def PCL(L, q):
    """
    Parameters
    ----------
    L : A list of candidates.
        It is a list of tuples (s_i, t1_ij, psi_ij, delta_ij)
    q : int
        Effective quota for c_j.

    Returns
    -------
    Assignment of EV for c_j. Assigned EVs do not need to maintain the sequence.
    Each assignment is a list of tuples (s_i, t1_ij, psi_ij, delta_ij).

    """
    sorted_L = sorted(L, key=lambda x: x[2]/x[3], reverse=True)
    
    A_r = set(sorted_L[:q])
    A_r_dash = set(sorted_L[q:])
    utility_max = computeUtility(A_r)
    for tuple_s in A_r:
        replacement = 0
        flag = 0
        for tuple_s_dash in A_r_dash:
            utility_2 = computeUtility(A_r - {tuple_s} | {tuple_s_dash})
            if utility_2 > utility_max:
                utility_max = utility_2
                replacement = tuple_s_dash
                flag = 1
                
        if flag != 0:
            A_r = A_r - {tuple_s} | {replacement}
            A_r_dash = A_r_dash - {replacement} | {tuple_s}
        # else:
        #     utility_1 = computeUtility(A_r - {tuple_s})
        #     if utility_1 > utility_max:
        #         A_r = A_r - {tuple_s}
    for tuple_s in A_r:
        utility_1 = computeUtility(A_r - {tuple_s})
        if utility_1 > utility_max:
            utility_max = utility_1
            A_r = A_r - {tuple_s}
        
    
    return list(A_r)



# Greedy preferred coalition
def PCG(L, q):
    """
    Parameters
    ----------
    L : A list of candidates.
        It is a list of tuples (s_i, t1_ij, psi_ij, delta_ij)
    q : int
        Effective quota for c_j.

    Returns
    -------
    Assignment of EV for c_j. Maintains the sequence.
    Each assignment is a list of tuples (s_i, t1_ij, psi_ij, delta_ij).

    """
    t_e = 0
    A_j = []
    sorted_L = sorted(L, key=lambda x: x[2] / x[3], reverse=True)
    #print("tuple_s: (s_i, t1_ij, psi_ij, delta_ij)")
    for tuple_s in sorted_L:
        #print(tuple_s, " : rato= ", tuple_s[2]/tuple_s[3])
        if len(A_j) >= q:
            break
        t1_ij = tuple_s[1] # charging time
        if t_e + t1_ij <= tuple_s[3]: # if charging can be done before effective deadline
            A_j.append(tuple_s)
            t_e = t_e + t1_ij
            #charge_transferred = charge_transferred + tuple_s[2]
    return A_j

# Dynamic Programming preferred coalition
def PCD(L, q):
    """
    Parameters
    ----------
    L : A list of candidates.
        It is a list of tuples (s_i, t1_ij, psi_ij, delta_ij)
    q : int
        Effective quota for c_j.

    Returns
    -------
    Assignment of EV for c_j. Maintains the sequence.
    Each assignment is a list of tuples (s_i, t1_ij, psi_ij, delta_ij).

    """
    #sorted_L = sorted(L, key=lambda x: x[2], reverse=True)
    sorted_L = sorted(L, key=lambda x: x[2] / x[3], reverse=True)
    l_max = max([x[3] for x in L ]) # max delta_ij
    #print(l_max)
    n_row = len(L)
    n_col = l_max
    D_j = [[0 for _ in range(n_col + 1)] for _ in range(n_row + 1)]
    A_j = [[[] for _ in range(n_col + 1)] for _ in range(n_row + 1)]
    k  = 0
    #print("tuple_s: (s_i, t1_ij, psi_ij, delta_ij)")
    for _tuple in sorted_L:
        #print(_tuple)
        k = k + 1
        t1_kj = _tuple[1]
        psi_kj = _tuple[2]
        delta_kj = _tuple[3]
        for l in range(l_max + 1):
            if (t1_kj <= l) and (l <= delta_kj): # check the deadline constraints
                if psi_kj + D_j[k-1][l - t1_kj] >= D_j[k-1][l]: # check if the total charge transfer will increase
                    if len(A_j[k-1][l - t1_kj]) + 1 <= q: # check if adding s_k crosses quota
                        D_j[k][l] = psi_kj + D_j[k-1][l - t1_kj]
                        A_j[k][l] = copy.deepcopy(A_j[k-1][l - t1_kj])
                        A_j[k][l].append(_tuple)
                else:
                    D_j[k][l] = D_j[k-1][l]
                    A_j[k][l] = A_j[k-1][l]
            else:
                D_j[k][l] = D_j[k-1][l]
                A_j[k][l] = A_j[k-1][l]
    
    max_energy_transferred = max(D_j[n_row])
    best_coalition_index = D_j[n_row].index(max_energy_transferred)
    pref_coalition = A_j[n_row][best_coalition_index]
    # print("Dj:\n", D_j)
    # print("Aj:\n", A_j)
    return pref_coalition
        
    
    

def preferredCoalition(W, P, q, r_j, t_free_j, func):
    #L = W.copy()
    L = copy.deepcopy(W)
    for (s_i, d_ij, t0_ij, psi_ij, r_i, gamma_i) in P:
        """
        Parameters
        ----------
        s_i: EV ID
        d_ij: distance from the EV to c_j
        t0_ij: time to reach c_j
        psi_ij: charge requirement of s_i at c_j
        gamma_i: max waiting time as per SLA
        """
        delta_ij = 0 # effective maximum allowed duration for charging that satisfies SLA
        t1_ij = math.ceil(psi_ij/ min(r_i, r_j)) # time to recharge the EV
        if t_free_j > t0_ij:
            delta_ij = t1_ij + gamma_i - (t_free_j - t0_ij)
        else:
            delta_ij = t1_ij + gamma_i
        
        if delta_ij > 0:
            L.append((s_i, t1_ij, psi_ij, delta_ij)) # we store a new tuple with 
        
    #coalition = randomChoice(L, q)
    coalition = func(L, q)
    return coalition
        
    

def match(ev_list: List[EV], cp_list: List[CP], Pref: Dict[int, List[Any]], func):
    """
    Match function. Runs at RSU

    Parameters
    ----------
    ev_list (List[EV]): List of EV.
    cp_list (List[CP]): List of CP.
    Pref (Dict[int, List[Any]]): Preference list of all EV. 
        Stored in a dictionary where key is the EV ID.
     
    """
    # initialization
    matched_s = {} # matched dictionary for EV
    matched_c = {} # matched dictionary for CP
    P = {} # current proposer list for all CP
    W = {} # waiting list for all CP
    matched_s_list = [] # list of already matched EV
    _Pref = copy.deepcopy(Pref) # without deep copy removal of an element delets element in the original
    for s in ev_list:
        s_i = s.ID
        matched_s[s_i] = []
    for c in cp_list:
        c_i = c.ID
        matched_c[c_i] = []
        P[c_i] = []
        W[c_i] = []
    
    while(True):
        S_dash = [s_i for s_i in matched_s if s_i not in matched_s_list and len(_Pref[s_i]) != 0] 
        if len(S_dash) > 0:
            for s_i in S_dash:
                # print(_Pref[s][0])
                choice_tuple = _Pref[s_i][0] # (c_j, d_ij or utility, t0_ij, psi_ij, r_i, gamma_i) Get the best CP choice
                _Pref[s_i].remove(choice_tuple) # remove the CP from pref. list
                choice_CP_ID = choice_tuple[0]
                updated_tuple = (s_i,) + choice_tuple[1:] # (s_i, d_ij or utility, t0_ij, psi_ij, r_i, gamma_i) # update with the EV ID
                P[choice_CP_ID].append(updated_tuple) # Add the s_i with its attributes in the current proposer list
            # print("proposer list: ", P)
            for c in cp_list:
                c_i = c.ID
                if len(P[c_i]) > 0: # if there is any new proposal
                    #print("CP ID: ", c_i)
                    pref_coalition = preferredCoalition(W[c_i], P[c_i], c.q, c.r_j, c.t_free_j, func)
                    # remove the old s_i from the matched_s_list
                    if len(W[c_i]) > 0:
                        # print("W[", c_i,"]: ", W[c_i])
                        for (s_i, t1_ij, psi_ij, delta_ij) in W[c_i]:
                            # print("s_i: ", s_i)
                            # print("Pre - matched_s_list: ", matched_s_list)
                            matched_s_list.remove(s_i)
                    for s_tuple in pref_coalition:
                        matched_s_list.append(s_tuple[0])
                        # print("matched_s_list: ", matched_s_list)
                    W[c_i] = pref_coalition
                    P[c_i] = []
        else:
            for c in cp_list:
                c_i = c.ID
                for tuple_s in W[c_i]: # tuple_s = (s_i, t1_ij, psi_ij, delta_ij) 
                    # print("EV: ", c_i, "")
                    matched_c[c_i].append(tuple_s)
                    s_i = tuple_s[0]
                    matched_s[s_i] = c_i
            return matched_s, matched_c
        
    
