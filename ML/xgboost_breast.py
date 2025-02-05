import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score
import xgboost as xgb

"""
PRECISION XGBOOST SUR BREAST-CANCER 96.49%
{'colsample_bytree': 0.4, 'gamma': 0.2, 'learning_rate': 0.3, 'max_depth': 4, 'min_child_weight': 3}
"""

df_x = pd.read_csv("Data/breast-cancer/breast-cancer.csv", delimiter=' ')
df_y = pd.read_csv("Data/breast-cancer/labels_breast-cancer.csv")
df = pd.concat([df_x, df_y], axis=1)

X = df.drop(["diagnosis"],axis=1)
Y = df["diagnosis"]
X_train, X_test, y_train, y_test = train_test_split(X, Y, train_size=0.8, test_size=0.2, random_state=0)


params={
 "learning_rate"    : [0.05, 0.10, 0.15, 0.20, 0.25, 0.30 ],
 "max_depth"        : [ 3, 4, 5, 6, 8, 10, 12, 15],
 "min_child_weight" : [ 1, 3, 5, 7 ],
 "gamma"            : [ 0.0, 0.1, 0.2 , 0.3, 0.4 ],
 "colsample_bytree" : [ 0.3, 0.4, 0.5 , 0.7 ]   
}

"""XGB_model = xgb.XGBClassifier()
xgb_cv_model  = GridSearchCV(XGB_model,params, cv = 10, n_jobs = -1, verbose = 2).fit(X_train, y_train)
print(xgb_cv_model.best_params_)
model = xgb.XGBClassifier(**xgb_cv_model.best_params_).fit(X_train, y_train)"""
model = xgb.XGBClassifier(colsample_bytree=0.4, gamma=0.2, learning_rate=0.3, max_depth=4, min_child_weight=3)
score = cross_val_score(model, X, Y, cv=10)
score.mean()
model.fit(X_train,y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))