"""Weighted selection and sensitivity calculation for the assignment."""
criteria = ["usefulness", "reliability", "privacy", "fairness", "cost", "maintainability"]
scores = {
    "Conventional": [4, 5, 5, 4, 5, 5],
    "AI/ML": [5, 3, 3, 3, 3, 3],
    "Blockchain": [3, 4, 3, 4, 2, 2],
    "Combined": [5, 3, 3, 4, 1, 2],
}
weights = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]

def weighted_scores(weights):
    return {name: round(sum(score * weight for score, weight in zip(values, weights)), 2)
            for name, values in scores.items()}


if __name__ == "__main__":
    print("Baseline weights:", dict(zip(criteria, weights)))
    print("Baseline scores:", weighted_scores(weights))
    cost_focus = [0.15, 0.15, 0.15, 0.10, 0.25, 0.20]
    usefulness_focus = [0.40, 0.15, 0.15, 0.15, 0.05, 0.10]
    print("Cost-focused sensitivity:", weighted_scores(cost_focus))
    print("Usefulness-focused sensitivity:", weighted_scores(usefulness_focus))
