from flask_restful import Resource
from flask import jsonify
from utils.database import get_db
from sqlalchemy import text
import random


class ClinicalData(Resource):
    
    def get(self, dataset_name):
        """Return clinical data for a specific dataset"""
        clinical_data = []
        table_name = dataset_name + "_data_clinical_patient"
        table_name = "brca_tcga_pub2015_data_clinical_patient"
        db = next(get_db())  # Retrieve the actual session
        try:
            results = db.execute(text(f"SELECT patient_id, age, race, sex, ajcc_pathologic_tumor_stage, os_status, os_months FROM {table_name} LIMIT 200")).mappings().all()
            for row in results:
                patient_info = {
                    "patient_id": row["patient_id"],
                    "age": row["age"],
                    "race": row["race"],
                    "gender": row["sex"],
                    "stage": row["ajcc_pathologic_tumor_stage"],
                    "status": "Alive" if row["os_status"][0] == "0" else "DECEASED",
                    "survival_months": row["os_months"]
                }
                clinical_data.append(patient_info)
            random.shuffle(clinical_data)
            return clinical_data, 200
        
        except Exception as e:
            return {"error": str(e)}, 500
        
        finally:
            db.close()  # Ensure the session is closed properly
