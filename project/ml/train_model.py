import pandas as pd
import numpy as np   
import os
import joblib
import warnings

# Sklearn imports for 20+ algorithms
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Classifiers
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier, 
                              AdaBoostClassifier, ExtraTreesClassifier, 
                              BaggingClassifier, HistGradientBoostingClassifier)
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.linear_model import (LogisticRegression, RidgeClassifier, SGDClassifier, 
                                 Perceptron, PassiveAggressiveClassifier)
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis

# Filter warnings for cleaner output
warnings.filterwarnings("ignore")

def train_model():
    # Use the generated dataset for high accuracy
    data_path = r"..\dataset\cpu_dataset.csv"
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Please run generate_dataset.py first.")
        return

    df = pd.read_csv(data_path)
    # print(f"Dataset loaded: {len(df)} rows")

    # Features: n_proc, avg_bt, var_bt, avg_at, avg_pr, time_quantum
    FEATURES = ["n_proc", "avg_bt", "var_bt", "avg_at", "avg_pr", "time_quantum"] 
    TARGET = "best_algo"

    X = df[FEATURES]
    y = df[TARGET]

    # Handle negative values if any for MultinomialNB (which only takes non-negative)
    X_min = X.min().min()
    X_non_neg = X - min(0, X_min)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_nn, X_test_nn, _, _ = train_test_split(X_non_neg, y, test_size=0.2, random_state=42)

    # 22 ML Algorithms
    models = {
        "1. Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "2. Decision Tree": DecisionTreeClassifier(random_state=42),
        "3. Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "4. Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "5. K-Nearest Neighbors": KNeighborsClassifier(),
        "6. AdaBoost": AdaBoostClassifier(random_state=42),
        "7. Gaussian Naive Bayes": GaussianNB(),
        "8. Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "9. Bagging Classifier": BaggingClassifier(random_state=42),
        "10. Hist Gradient Boosting": HistGradientBoostingClassifier(random_state=42),
        "11. Ridge Classifier": RidgeClassifier(random_state=42),
        "12. SGD Classifier": SGDClassifier(random_state=42),
        "13. Perceptron": Perceptron(random_state=42),
        "14. Passive Aggressive": PassiveAggressiveClassifier(random_state=42),
        "15. Bernoulli NB": BernoulliNB(),
        "16. Multinomial NB": MultinomialNB(),
        "17. MLP Classifier (NN)": MLPClassifier(max_iter=1000, random_state=42),
        "18. Linear SVC": LinearSVC(max_iter=1000, random_state=42),
        "19. SVC (RBF)": SVC(kernel='rbf', probability=True, random_state=42),
        "20. LDA": LinearDiscriminantAnalysis(),
        "21. QDA": QuadraticDiscriminantAnalysis(),
        "22. Extra Tree (Single)": ExtraTreeClassifier(random_state=42)
    }

    results = []
    best_model = None
    best_acc = 0
    best_name = ""

    print("\n" + "="*40)
    print("      SCIKIT-LEARN MODEL COMPARISON")
    print("="*40)
    print(f"{'Model Name':<25} | {'Accuracy':<10}")
    print("-"*40)

    for name, model in models.items():
        try:
            # Use non-negative data for MultinomialNB
            if "Multinomial NB" in name:
                model.fit(X_train_nn, y_train)
                preds = model.predict(X_test_nn)
            else:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
            acc = accuracy_score(y_test, preds)
            results.append((name, acc))
            print(f"{name:<25} | {acc*100:6.2f}%")
            
            if acc > best_acc:
                best_acc = acc
                best_model = model
                best_name = name
        except Exception as e:
            # print(f"Error training {name}: {e}")
            pass

    print("="*40)
    print(f"\nBest : {best_name}")
    print(f"ACCURACY: {best_acc*100:.2f}%")
    print("="*40)

    # Save the best performing model
    joblib.dump(best_model, "cpu_scheduler_model.pkl")
    joblib.dump(FEATURES, "model_features.pkl")
    print(f"\nSaved the best model ({best_name}) to cpu_scheduler_model.pkl")

if __name__ == "__main__":
    train_model()

