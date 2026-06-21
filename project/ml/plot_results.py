import matplotlib.pyplot as plt
import seaborn as sns
import os

# Results from model comparison
results = [
    ("MLP Classifier (NN)", 83.50),
    ("Gaussian Naive Bayes", 83.25),
    ("Random Forest", 83.00),
    ("Extra Trees", 83.00),
    ("AdaBoost", 83.00),
    ("Logistic Regression", 83.00),
    ("Perceptron", 83.00),
    ("LDA", 83.00),
    ("SVC (RBF)", 82.75),
    ("Ridge Classifier", 82.75),
    ("Bernoulli NB", 82.75),
    ("Linear SVC", 82.50),
    ("Gradient Boosting", 82.00),
    ("Multinomial NB", 81.00),
    ("K-Nearest Neighbors", 80.50),
    ("Bagging Classifier", 80.50),
    ("Hist Gradient Boosting", 80.00),
    ("Passive Aggressive", 77.25),
    ("Extra Tree (Single)", 72.00),
    ("Decision Tree", 69.50),
    ("SGD Classifier", 69.25)
]

# Sort results by accuracy
results.sort(key=lambda x: x[1], reverse=True)
models, accuracies = zip(*results)

# Set style
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 8))

# Color palette: custom gradient from cyan to dark purple
colors = sns.color_palette("coolwarm", len(models))

# Horizontal bar plot
bars = ax.barh(models, accuracies, color=colors, edgecolor='none', height=0.6)

# Labels and title
ax.set_title("Machine Learning Models Comparison on CPU Dataset", fontsize=16, fontweight='bold', pad=20, color='cyan')
ax.set_xlabel("Accuracy (%)", fontsize=12, labelpad=10, color='white')
ax.set_xlim(0, 100)

# Grid lines
ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')
ax.set_axisbelow(True)

# Add values to the bars
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", 
            va='center', ha='left', fontsize=10, color='white', fontweight='bold')

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('gray')
ax.spines['bottom'].set_color('gray')
ax.tick_params(colors='white', labelsize=10)

plt.gca().invert_yaxis() # Highest accuracy on top
plt.tight_layout()

# Save the plot
output_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\32650ce2-b077-4c88-8ace-dfae4fbfd98e\accuracy_comparison.png"
plt.savefig(output_path, dpi=300)
print(f"Plot saved successfully at: {output_path}")
