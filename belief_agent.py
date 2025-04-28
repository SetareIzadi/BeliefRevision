# Belief Revision Agent (with CNF conversion + Resolution)

class BeliefRevisionAgent:
    def __init__(self):
        # Initialize an empty belief base
        self.belief_base = set()

    def add_belief(self, belief):
        # Add a belief to the belief base
        self.belief_base.add(belief)

    def remove_belief(self, belief):
        # Remove a belief from the belief base if it exists
        if belief in self.belief_base:
            self.belief_base.remove(belief)

    def entails(self, query):
        # Check if the belief base entails a query using resolution
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
                    return True
                new.update(resolvents)
            if new.issubset(clauses):
                return False
            clauses.update(new)

    def revise(self, new_belief):
        # Revise the belief base with a new belief ensuring consistency
        temp_base = self.belief_base.copy()
        temp_base.add(new_belief)
        
        if self.is_inconsistent(temp_base):
            self.contract(self.negate(new_belief))
        
        self.add_belief(new_belief)

    def is_inconsistent(self, beliefs):
        # Check if the set of beliefs is inconsistent
        for belief in beliefs:
            if self.negate(belief) in beliefs:
                return True
        return False

    def contract(self, belief):
        # Remove any belief that conflicts with the new belief
        if belief in self.belief_base:
            self.belief_base.remove(belief)

    def negate(self, belief):
        # Negate a belief
        if belief.startswith('~'):
            return belief[1:]
        else:
            return '~' + belief

    def to_cnf(self, belief):
        # Very simple CNF conversion (only basic propositional logic)
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
        # Try to resolve two clauses
        resolvents = set()
        for di in ci:
            for dj in cj:
                if di == self.negate(dj):
                    new_clause = (ci.union(cj)) - {di, dj}
                    resolvents.add(frozenset(new_clause))
        return resolvents

    def print_beliefs(self):
        # Print the current belief base
        print("Current Belief Base:", self.belief_base)

# Example usage
if __name__ == "__main__":
    agent = BeliefRevisionAgent()

    agent.add_belief("A")
    agent.add_belief("A -> B")
    agent.print_beliefs()

    print("Entails B?", agent.entails("B"))

    agent.revise("~A")
    agent.print_beliefs()

    print("Entails A?", agent.entails("A"))