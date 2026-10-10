import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from pycaret.regression import load_model, predict_model

MODEL_NAME = 'deployment_20260516'

def test_model_file_exists():
    """Valida que el archivo serializado del modelo exista en el repositorio."""
    pkl_path = f"{MODEL_NAME}.pkl"
    assert os.path.exists(pkl_path), f"El archivo del modelo {pkl_path} no existe."

def test_model_loading_and_inference():
    """Valida que el modelo PyCaret pueda cargarse y predecir sobre datos no vistos."""
    model = load_model(MODEL_NAME)
    assert model is not None, "El modelo no pudo ser cargado."

    sample_input = pd.DataFrame([{
        'age': 35,
        'sex': 'male',
        'bmi': 26.5,
        'children': 2,
        'smoker': 'no',
        'region': 'northeast'
    }])

    prediction = predict_model(model, data=sample_input)
    assert 'prediction_label' in prediction.columns, "La columna de predicción no está presente en la salida."
    pred_value = float(prediction.loc[0, 'prediction_label'])
    assert pred_value > 0, f"El valor predicho de costo de seguro ({pred_value}) debe ser positivo."
