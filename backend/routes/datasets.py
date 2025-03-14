from flask_restful import Resource
from flask import jsonify
from utils.database import get_db
from sqlalchemy import text

class Datasets(Resource):
    
    def get(self):
        """Return all datasets grouped by type"""
        datasets = []
        db = next(get_db())  # Retrieve the actual session
        try:
            results = db.execute(text("SELECT * FROM dataset")).mappings().all()  # Convert rows to dictionaries
            for row in results:
                dataset = {
                    "id": row["name"],
                    "name": row["name"],
                    "type": row["type"]
                }
                datasets.append(dataset)
            
            # Group datasets by type
            grouped_datasets = {}
            for dataset in datasets:
                cancer_type = dataset["type"]
                if cancer_type not in grouped_datasets:
                    grouped_datasets[cancer_type] = []
                
                # Include full dataset object in the list
                grouped_datasets[cancer_type].append({
                    "id": dataset["id"],
                    "name": dataset["name"],
                    "type": dataset["type"]
                })
            
            return grouped_datasets
            
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            db.close()  # Ensure the session is closed properly