# Belief Revision Agent

class BeliefRevisionAgent:
    def __init__(self):
        self.belief_base = set()

    def add_belief(self, belief):
        self.belief_base.add(self._clean(belief))

    def remove_belief(self, belief):
        self.belief_base.discard(self._clean(belief))

    def revise(self, new_belief):
        new_belief = self._clean(new_belief)
        if self._is_inconsistent_with(new_belief):
            self._contract(self.negate(new_belief))
        self.add_belief(new_belief)

    def _is_inconsistent_with(self, new_belief):
        temp = BeliefRevisionAgent()
        temp.belief_base = self.belief_base.copy()
        temp.add_belief(new_belief)
        return temp.entails("False")

    def _contract(self, belief):
        belief = self._clean(belief)
        candidates = list(self.belief_base)
        for b in candidates:
            temp = self.belief_base.copy()
            temp.discard(b)
            temp_agent = BeliefRevisionAgent()
            temp_agent.belief_base = temp
            if not temp_agent.entails(belief):
                self.belief_base = temp
                return
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                temp = self.belief_base.copy()
                temp.discard(candidates[i])
                temp.discard(candidates[j])
                temp_agent = BeliefRevisionAgent()
                temp_agent.belief_base = temp
                if not temp_agent.entails(belief):
                    self.belief_base = temp
                    return

    def entails(self, query):
        query = self._clean(query)
        clauses = set()
        for belief in self.belief_base:
            clauses.update(self.to_cnf(belief))
        clauses.update(self.to_cnf(self.negate(query)))

        new = set()
        while True:
            n = len(clauses)
            clause_list = list(clauses)
            for i in range(n):
                for j in range(i + 1, n):
                    resolvents = self.resolve(clause_list[i], clause_list[j])
                    if frozenset() in resolvents:
                        return True  # contradiction found
                    new.update(resolvents)
            if new.issubset(clauses):
                return False
            clauses.update(new)

    def negate(self, belief):
        belief = self._clean(belief)
        return belief[1:] if belief.startswith("~") else "~" + belief

    def to_cnf(self, belief):
        belief = self._clean(belief)
        # Implication: A -> B becomes ~A | B
        if "->" in belief:
            left, right = belief.split("->", 1)
            return [frozenset([self.negate(left), right])]
        # Negated conjunction: ~(A & B) becomes ~A | ~B
        elif belief.startswith("~(") and belief.endswith(")"):
            inner = belief[2:-1]
            if "&" in inner:
                a, b = inner.split("&", 1)
                return [frozenset([self.negate(a)]), frozenset([self.negate(b)])]
            elif "|" in inner:
                a, b = inner.split("|", 1)
                return [frozenset([self.negate(a), self.negate(b)])]
        # Conjunction: A & B becomes {A}, {B}
        elif "&" in belief:
            a, b = belief.split("&", 1)
            return [frozenset([a]), frozenset([b])]
        # Disjunction: A | B becomes {A, B}
        elif "|" in belief:
            a, b = belief.split("|", 1)
            return [frozenset([a, b])]
        # Atomic
        else:
            return [frozenset([belief])]

    def resolve(self, ci, cj):
        resolvents = set()
        for di in ci:
            for dj in cj:
                if di == self.negate(dj):
                    new_clause = ci.union(cj) - {di, dj}
                    resolvents.add(frozenset(new_clause))
        return resolvents

    def _clean(self, belief):
        return belief.replace(" ", "").strip()

# Testing the agent with AGM Postulates
if __name__ == "__main__":
    print("Belief Revision Agent - AGM Postulates Test\n")

    agent = BeliefRevisionAgent()
    agent.add_belief("p")
    agent.add_belief("p -> q")
    print("Initial belief base:", agent.belief_base)

    # Success Postulate
    agent.revise("q")
    print("\nAfter revising with 'q' (Success):", agent.belief_base)
    print("Inclusion: Does it include 'q'?", "q" in agent.belief_base)

    # Vacuity
    agent2 = BeliefRevisionAgent()
    agent2.add_belief("p")
    print("\nBefore revising with 'p' (Vacuity):", agent2.belief_base)
    agent2.revise("p")
    print("After revising with 'p' (Vacuity):", agent2.belief_base)

    # Consistency
    agent3 = BeliefRevisionAgent()
    agent3.add_belief("p")
    agent3.revise("r")
    print("\nAfter revising with 'r' (Consistency):", agent3.belief_base)

    # Extensionality
    agent4 = BeliefRevisionAgent()
    agent4.add_belief("p")
    agent4.revise("p")

    agent5 = BeliefRevisionAgent()
    agent5.add_belief("p")
    agent5.revise("p")

    print("\nExtensionality: Bases equal?", agent4.belief_base == agent5.belief_base)