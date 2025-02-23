
# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score
from sklearn.preprocessing import StandardScaler



# Load data
df = pd.read_csv('/content/data-export.csv')

# Extract first row as column names
new_header = df.iloc[0]
data = df[1:].copy()  # Exclude the first row

# Assign new headers
data.columns = new_header
data.reset_index(drop=True, inplace=True)

# Rename columns with generic names
data.rename(columns={'Unnamed: 1': 'Session primary channel group (Default channel group)',
                     'Unnamed: 2': 'Date + hour (YYYYMMDDHH)'}, inplace=True)

# Convert 'Date + hour (YYYYMMDDHH)' to datetime format
data['Date + hour (YYYYMMDDHH)'] = pd.to_datetime(data['Date + hour (YYYYMMDDHH)'], format='%Y%m%d%H', errors='coerce')

# Define numeric columns
numeric_cols = ['Users', 'Sessions', 'Engaged sessions', 'Average engagement time per session',
                'Engaged sessions per user', 'Events per session', 'Engagement rate', 'Event count']

# Convert numeric columns to proper dtype
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Handle missing values only in numeric columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())



data = data.assign(
    Hour=data['Date + hour (YYYYMMDDHH)'].dt.hour,
    Day=data['Date + hour (YYYYMMDDHH)'].dt.day,
    Weekday=data['Date + hour (YYYYMMDDHH)'].dt.weekday,
    Weekend=(data['Date + hour (YYYYMMDDHH)'].dt.weekday >= 5).astype(int),
    Sessions_per_User=data['Sessions'] / (data['Users'] + 1),  # Avoid division by zero
    Engagement_per_Session=data['Engaged sessions'] / (data['Sessions'] + 1)
)


# Plot Users and Sessions over time
plt.figure(figsize=(14, 7))
sns.lineplot(data=data, x='Date + hour (YYYYMMDDHH)', y='Users', label='Users', color='blue')
sns.lineplot(data=data, x='Date + hour (YYYYMMDDHH)', y='Sessions', label='Sessions', color='green')
plt.title('Total Users and Sessions Over Time')
plt.xlabel('Date and Hour')
plt.ylabel('Count')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.show()

# Correlation Heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(data[numeric_cols].corr(), annot=True, cmap='coolwarm', linewidths=0.5)
plt.title("Feature Correlation Heatmap")
plt.show()


# Define features (X) and target (y)
X = data[['Hour', 'Day', 'Weekday', 'Weekend', 'Sessions', 'Engagement_per_Session']]
y = data['Users']

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Regressor
rf_regressor = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
rf_regressor.fit(X_train, y_train)

# Predict and evaluate model performance
y_pred_reg = rf_regressor.predict(X_test)
print(f"MAE (User Prediction): {mean_absolute_error(y_test, y_pred_reg)}")


# Define High Engagement as Engagement Rate > 0.5
data['High Engagement'] = (data['Engagement rate'] > 0.5).astype(int)

# Define features (X) and target (y)
X = data[['Hour', 'Day', 'Weekday', 'Weekend', 'Sessions', 'Engagement_per_Session']]
y = data['High Engagement']

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
rf_classifier.fit(X_train, y_train)

# Predict and evaluate model performance
y_pred_class = rf_classifier.predict(X_test)
print(f"Classification Accuracy (High Engagement Prediction): {accuracy_score(y_test, y_pred_class)}")


channel_performance = data.groupby('Session primary channel group (Default channel group)').agg({
    'Users': 'sum',
    'Sessions': 'sum',
    'Engaged sessions': 'sum',
    'Engagement rate': 'mean',
    'Events per session': 'mean'
})

# Normalize Engagement Rate and Events per Session
channel_performance['Normalized Engagement Rate'] = channel_performance['Engagement rate'] / channel_performance['Engagement rate'].max()
channel_performance['Normalized Events per Session'] = channel_performance['Events per session'] / channel_performance['Events per session'].max()

# Bar plot for channel performance
fig, ax = plt.subplots(3, 1, figsize=(12, 18))

ax[0].bar(channel_performance.index, channel_performance['Users'], label='Users', alpha=0.8)
ax[0].bar(channel_performance.index, channel_performance['Sessions'], label='Sessions', alpha=0.6)
ax[0].set_title('Users and Sessions by Channel')
ax[0].set_ylabel('Count')
ax[0].legend()

ax[1].bar(channel_performance.index, channel_performance['Normalized Engagement Rate'], color='orange')
ax[1].set_title('Normalized Engagement Rate by Channel')
ax[1].set_ylabel('Normalized Rate')

ax[2].bar(channel_performance.index, channel_performance['Normalized Events per Session'], color='green')
ax[2].set_title('Normalized Events per Session by Channel')
ax[2].set_ylabel('Normalized Count')

plt.tight_layout()
plt.show()

