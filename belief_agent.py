# Belief Revision Agent

class BeliefRevisionAgent:
    def __init__(self):
        self.belief_base = set()

    def add_belief(self, belief):
        self.belief_base.add(belief)

    def remove_belief(self, belief):
        if belief in self.belief_base:
            self.belief_base.remove(belief)

    def entails(self, query):
        clauses = set()
        for belief in self.belief_base:
            clauses.update(self.to_cnf(belief))
        clauses.update(self.to_cnf(self.negate(query)))

        new = set()
        while True:
            n = len(clauses)
            pairs = [(list(clauses)[i], list(clauses)[j]) for i in range(n) for j in range(i+1, n)]
            for (ci, cj) in pairs:
                resolvents = self.resolve(ci, cj)
                if frozenset() in resolvents:
                    return True  # contradiction found
                new.update(resolvents)
            if new.issubset(clauses):
                return False  # no contradiction
            clauses.update(new)

    def revise(self, new_belief):
        # Revise the belief base by incorporating the new belief
        if self.is_inconsistent_with(new_belief):
            self.contract(self.negate(new_belief))
        self.add_belief(new_belief)

    def is_inconsistent_with(self, new_belief):
        # Check if adding new_belief causes inconsistency
        temp_agent = BeliefRevisionAgent()
        temp_agent.belief_base = self.belief_base.copy()
        temp_agent.add_belief(new_belief)
        return temp_agent.entails("False")  # Check if contradiction occurs

    def contract(self, belief):
        # Basic contraction: remove beliefs that cause direct inconsistency
        conflicting_beliefs = {b for b in self.belief_base if b == self.negate(belief)}
        for b in conflicting_beliefs:
            self.remove_belief(b)

    def negate(self, belief):
        # Negate a belief
        belief = belief.strip()
        if belief.startswith('~'):
            return belief[1:]
        else:
            return '~' + belief

    def to_cnf(self, belief):
        # Very simple CNF conversion
        belief = belief.replace(' ', '')
        if '->' in belief:
            left, right = belief.split('->')
            return [frozenset([self.negate(left), right])]
        elif belief.startswith('~(') and belief.endswith(')'):
            inner = belief[2:-1]
            if '&' in inner:
                parts = inner.split('&')
                return [frozenset([self.negate(parts[0])]), frozenset([self.negate(parts[1])])]
            elif '|' in inner:
                parts = inner.split('|')
                return [frozenset([self.negate(parts[0]), self.negate(parts[1])])]
        elif '&' in belief:
            parts = belief.split('&')
            return [frozenset([parts[0]]), frozenset([parts[1]])]
        elif '|' in belief:
            parts = belief.split('|')
            return [frozenset(parts)]
        else:
            return [frozenset([belief])]

    def resolve(self, ci, cj):
        resolvents = set()
        for di in ci:
            for dj in cj:
                if di == self.negate(dj):
                    new_clause = (ci.union(cj)) - {di, dj}
                    resolvents.add(frozenset(new_clause))
        return resolvents
    

if __name__ == "__main__":
    print("Belief Revision Agent - AGM Postulates Test")

    agent = BeliefRevisionAgent()
    
    # Initial beliefs
    agent.add_belief("p")
    agent.add_belief("p -> q")
    print("\nInitial belief base:", agent.belief_base)

    # Success Postulate Test: revising with q
    agent.revise("q")
    print("\nAfter revising with 'q' (Success Postulate):", agent.belief_base)

    # Inclusion Postulate Test
    print("\nInclusion Postulate: 'q' should be included:", "q" in agent.belief_base)

    # Vacuity Postulate Test
    agent2 = BeliefRevisionAgent()
    agent2.add_belief("p")
    print("\nBelief base before revising with 'p' (Vacuity):", agent2.belief_base)
    agent2.revise("p")
    print("Belief base after revising with 'p' (Vacuity):", agent2.belief_base)

    # Consistency Postulate Test
    agent3 = BeliefRevisionAgent()
    agent3.add_belief("p")
    agent3.revise("r")
    print("\nBelief base after revising with 'r' (Consistency):", agent3.belief_base)

    # Extensionality Postulate Test
    agent4 = BeliefRevisionAgent()
    agent4.add_belief("p")
    agent4.revise("p")
    
    agent5 = BeliefRevisionAgent()
    agent5.add_belief("p")
    agent5.revise("p")

    print("\nExtensionality Postulate: bases should be the same:", agent4.belief_base == agent5.belief_base)

