# File: dfa_logic.py
import json
from collections import defaultdict
from typing import Set, Dict, List, Tuple

class DFA:
    """Represents a Deterministic Finite Automaton (DFA)."""
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[str, Dict[str, str]], start_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def is_valid(self) -> Tuple[bool, str]:
        """Checks if the DFA is valid and complete."""
        if not self.states:
            return False, "States set cannot be empty."
        if self.start_state not in self.states:
            return False, f"Start state '{self.start_state}' is not in the set of states."
        if not self.final_states.issubset(self.states):
            return False, "All final states must be in the set of states."
        
        for state in self.states:
            if state not in self.transitions:
                return False, f"Missing transitions for state '{state}'."
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    return False, f"Missing transition for state '{state}' on symbol '{symbol}'."
                next_state = self.transitions[state][symbol]
                if next_state not in self.states:
                    return False, f"Transition from '{state}' on '{symbol}' leads to an invalid state '{next_state}'."
        return True, "DFA is valid."

    def remove_unreachable_states(self) -> 'DFA':
        """Removes states unreachable from the start state."""
        reachable_states = {self.start_state}
        queue = [self.start_state]
        
        while queue:
            current_state = queue.pop(0)
            if current_state in self.transitions:
                for symbol in self.alphabet:
                    next_state = self.transitions[current_state].get(symbol)
                    if next_state and next_state not in reachable_states:
                        reachable_states.add(next_state)
                        queue.append(next_state)
        
        new_states = self.states.intersection(reachable_states)
        new_final_states = self.final_states.intersection(reachable_states)
        new_transitions = {s: self.transitions[s] for s in reachable_states}
        
        return DFA(new_states, self.alphabet, new_transitions, self.start_state, new_final_states)
        
    def to_dict(self) -> Dict:
        """Serializes the DFA to a dictionary for JSON conversion."""
        return {
            "states": sorted(list(self.states)),
            "alphabet": sorted(list(self.alphabet)),
            "transitions": self.transitions,
            "start_state": self.start_state,
            "final_states": sorted(list(self.final_states))
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DFA':
        """Creates a DFA instance from a dictionary."""
        return cls(
            set(data["states"]),
            set(data["alphabet"]),
            data["transitions"],
            data["start_state"],
            set(data["final_states"])
        )

    def __repr__(self):
        """String representation of the DFA for display."""
        return (
            f"Q (States)      = {sorted(list(self.states))}\n"
            f"Σ (Alphabet)    = {sorted(list(self.alphabet))}\n"
            f"δ (Transitions) = {json.dumps(self.transitions, indent=4)}\n"
            f"q₀ (Start State)  = {self.start_state}\n"
            f"F (Final States)  = {sorted(list(self.final_states))}"
        )

class DFAMinimizer:
    """Performs DFA minimization using the Table-Filling Algorithm."""
    def __init__(self, dfa: DFA):
        self.dfa = dfa

    def minimize(self) -> DFA:
        """Main method to minimize the DFA."""
        # Step 1: Remove unreachable states
        dfa = self.dfa.remove_unreachable_states()

        # Step 2: Initialize the table for distinguishable pairs
        states = sorted(list(dfa.states))
        state_map = {state: i for i, state in enumerate(states)}
        num_states = len(states)
        dist_table = [[False] * num_states for _ in range(num_states)]

        # Step 3: Base case - mark pairs where one is final and the other isn't
        for i in range(num_states):
            for j in range(i + 1, num_states):
                s1_is_final = states[i] in dfa.final_states
                s2_is_final = states[j] in dfa.final_states
                if s1_is_final != s2_is_final:
                    dist_table[i][j] = True
        
        # Step 4: Inductive step - repeatedly mark pairs
        changed = True
        while changed:
            changed = False
            for i in range(num_states):
                for j in range(i + 1, num_states):
                    if not dist_table[i][j]:
                        for symbol in dfa.alphabet:
                            next1 = dfa.transitions[states[i]][symbol]
                            next2 = dfa.transitions[states[j]][symbol]
                            
                            idx1, idx2 = state_map[next1], state_map[next2]
                            row, col = min(idx1, idx2), max(idx1, idx2)

                            if row != col and dist_table[row][col]:
                                dist_table[i][j] = True
                                changed = True
                                break

        # Step 5: Group indistinguishable states into partitions
        partitions = []
        visited = set()
        for i in range(num_states):
            if states[i] in visited:
                continue
            
            current_partition = {states[i]}
            visited.add(states[i])
            for j in range(i + 1, num_states):
                if not dist_table[i][j]:
                    current_partition.add(states[j])
                    visited.add(states[j])
            partitions.append(frozenset(current_partition))

        # Step 6: Construct the new minimized DFA
        partition_map = {state: p for p in partitions for state in p}
        new_state_names = {p: f"q{i}" for i, p in enumerate(partitions)}
        
        new_states = set(new_state_names.values())
        new_start_state = new_state_names[partition_map[dfa.start_state]]
        new_final_states = {new_state_names[p] for p in partitions if not p.isdisjoint(dfa.final_states)}
        new_transitions = defaultdict(dict)
        
        for p in partitions:
            rep_state = next(iter(p)) # Representative state from the partition
            new_name = new_state_names[p]
            for symbol in dfa.alphabet:
                next_state_old = dfa.transitions[rep_state][symbol]
                next_partition = partition_map[next_state_old]
                new_transitions[new_name][symbol] = new_state_names[next_partition]

        return DFA(new_states, dfa.alphabet, dict(new_transitions), new_start_state, new_final_states)