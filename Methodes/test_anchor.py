import sys
import os
sys.path.append('../Masterial')
import torch
torch.cuda.empty_cache()
import model
from prepare_dataset import *
from neighbor_generator import *
import json
from anchor import anchor_tabular
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def main():
    if(len(sys.argv) < 2):
        print("Spécifier votre choix: breast ou diabetes")
        exit()
    if sys.argv[1] == "breast":
        #path_data = "Data/breast-cancer"
        #name_json_info = "breast-cancer_info.json"
        #name_json_rules = "breast-cancer_rules.json"
        name_model = "breast_cancer.pt"
        model_dropout = 0.1
        model_input_size = 30
        model_output_size = 2
        dataset = prepare_breast_cancer_dataset()
    elif sys.argv[1] == "diabetes":
        #path_data = "Data/diabetes"
        #name_json_info = "diabetes_info.json"
        #name_json_rules = "diabetes_rules.json"
        name_model = "diabetes.pt"
        model_dropout = 0
        model_input_size = 8
        model_output_size = 2
        dataset = prepare_diabete_dataset()
    else:
        print("Mauvais arguments")
        exit()

    features = dataset["columns"][1:]    #####Json

    X, y = dataset['X'], dataset['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    blackbox = model.MLP(model_input_size, model_output_size, model_dropout).to(device)
    blackbox.load_state_dict(torch.load(os.path.join("./models", name_model)))
    blackbox.eval()

    X2E = X_test
    idx_record2explain = 9

    class_name = dataset['class_name']
    columns = dataset['columns']
    continuous = dataset['continuous']
    possible_outcomes = dataset['possible_outcomes']
    label_encoder = dataset['label_encoder']

    feature_names = list(columns)
    feature_names.remove(class_name)

    categorical_names = dict()
    idx_discrete_features = list()
    for idx, col in enumerate(feature_names):
        if col == class_name or col in continuous:
            continue
        idx_discrete_features.append(idx)
        categorical_names[idx] = label_encoder[col].classes_

    # Create Anchor Explainer
    explainer = anchor_tabular.AnchorTabularExplainer(possible_outcomes, feature_names, X2E, categorical_names)
    explainer.fit(X_train, y_train, X_test, y_test)
    print('Prediction: ', possible_outcomes[blackbox.predict(X2E[idx_record2explain].reshape(1, -1))[0]])

    exp, info = explainer.explain_instance(X2E[idx_record2explain].reshape(1, -1), blackbox.predict, threshold=0.95)

    print('Anchor: %s' % (' AND '.join(exp.names())))
    print('Precision: %.2f' % exp.precision())
    print('Coverage: %.2f' % exp.coverage())

    # Get test examples where the anchora pplies# Get t
    fit_anchor = np.where(np.all(X2E[:, exp.features()] == X2E[idx_record2explain][exp.features()], axis=1))[0]
    print('Anchor test coverage: %.2f' % (fit_anchor.shape[0] / float(X2E.shape[0])))
    print('Anchor test precision: %.2f' % (np.mean(blackbox.predict(X2E[fit_anchor]) ==
                                                   blackbox.predict(X2E[idx_record2explain].reshape(1, -1)))))
    print(blackbox.predict(info['state']['raw_data']))


if __name__ == "__main__":
    main()
