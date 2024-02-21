import unittest
from unittest.mock import Mock, call
import numpy as np
from datetime import datetime
from aki_predictor import AKIPredictor

class AKIPredictorTest(unittest.TestCase):
    def setUp(self):
        self.storage_manager = Mock()
        self.test_mrn = '12345'
        self.test_patient_data = {
            'sex': 'f',
            'date_of_birth': '1990-01-01',
            'creatinine_results': [60.7, 62.3, 53, 80, 165, 204.56]
        }
        self.storage_manager.current_patients = {
            self.test_mrn: self.test_patient_data
        }

    def test_predict_aki(self):
        model_mock = Mock()
        model_mock.predict.return_value = np.array([1], dtype=np.int64)
        predictor = AKIPredictor(self.storage_manager)
        predictor.model = model_mock

        result = predictor.predict_aki(self.test_mrn)

        self.assertEqual(result, 1)

        # Calculate expected age to assert correct input to the model
        today = datetime.date.today()
        dob = datetime.datetime.strptime(self.test_patient_data['date_of_birth'], "%Y-%m-%d")
        expected_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Expected input features include sex (encoded as 1 for 'f'), age, and creatinine results
        expected_input_features = np.array([1, expected_age] + self.test_patient_data['creatinine_results'], dtype=np.float64).reshape(1, -1)
        
        # Assert the model's predict method was called with the correct input features
        model_mock.predict.assert_called_once_with(expected_input_features)

if __name__ == '__main__':
    unittest.main()
