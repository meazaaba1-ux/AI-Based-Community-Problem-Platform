
import csv
from pathlib import Path
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB

# Find the dataset in this folder
folder = Path(__file__).parent
dataset_path = folder / "dataset.csv"
model_path = folder / "problem_classifier.pkl"

# Load the training examples
with dataset_path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(
        (line for line in file if line.strip())
    )
    rows = list(reader)

# Prepare descriptions and category labels
descriptions = [row["description"].strip() for row in rows]
categories = [row["category"].strip() for row in rows]

if not descriptions or any(not text for text in descriptions):
    raise ValueError("The dataset contains empty descriptions.")

if len(descriptions) != len(categories):
    raise ValueError("Descriptions and categories do not match.")

# Build the text-classification model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

# Train the model using all 25 examples
model.fit(descriptions, categories)

# Save the trained model
with model_path.open("wb") as file:
    pickle.dump(model, file)

print("AI model trained successfully!")
print("Training examples:", len(descriptions))
print("Categories:", sorted(set(categories)))
print("Saved model to:", model_path)
