from pathlib import Path
import pickle

folder = Path(__file__).parent
model_path = folder / "problem_classifier.pkl"

with model_path.open("rb") as file:
    model = pickle.load(file)

test_reports = [
    "A deep crack has appeared on the main road.",
    "People are throwing rubbish near the hospital.",
    "The water supply has stopped in our village.",
    "The streetlight is broken near the school.",
    "Rainwater cannot flow because the drain is blocked."
]
print("AI Community Problem Classification")
print("-" * 40)
print("Number of test reports:", len(test_reports))

for description in test_reports:
    prediction = model.predict([description])[0]
    print("Report:", description)
    print("Predicted category:", prediction)
    print()
