# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.database import get_db
from flask_restful import Api, Resource
from routes.datasets import Datasets
from routes.clinical_data import ClinicalData
from routes.summary import Summary
from routes.analysis import Analysis
from routes.heatmap import Heatmap
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
api = Api(app)
CORS(app)  # Enable CORS for all routes

# Sample dataset information
datasets = [
    {"id": "brca_tcga_pub2015", "name": "brca_tcga_pub2015", "type": "Invasive Breast Carcinoma"},
    {"id": "brca_tcga", "name": "brca_tcga", "type": "Invasive Breast Carcinoma"},
    {"id": "brca_tcga_pan_can_atlas_2018", "name": "brca_tcga_pan_can_atlas_2018", "type": "Invasive Breast Carcinoma"},
    {"id": "brca_tcga_pub", "name": "brca_tcga_pub", "type": "Invasive Breast Carcinoma"},
    {"id": "brca_tcga_gdc", "name": "brca_tcga_gdc", "type": "Invasive Breast Carcinoma"},
    {"id": "breast_cptac_gdc", "name": "breast_cptac_gdc", "type": "Breast"},
    {"id": "bfn_duke_nus_2015", "name": "bfn_duke_nus_2015", "type": "Breast Fibroepithelial Neoplasms"},
    {"id": "mbc_msk_2021", "name": "mbc_msk_2021", "type": "Metaplastic Breast Cancer"},
]


# Sample summary statistics for each dataset
summary_stats = {
    "brca_tcga_pub2015": {
        "total_patients": 825,
        "median_age": 58.5,
        "stage_distribution": {
            "Stage I": 143,
            "Stage II": 478,
            "Stage III": 165,
            "Stage IV": 39
        },
        "mutation_counts": {
            "TP53": 287,
            "PIK3CA": 312,
            "CDH1": 128,
            "GATA3": 95,
            "MAP3K1": 82
        }
    },
    # Add summary data for other datasets as needed
}

    

@app.route('/api/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Return details for a specific dataset"""
    dataset = next((d for d in datasets if d["id"] == dataset_id), None)
    
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404
    
    return jsonify(dataset)


# @app.route('/api/datasets/<dataset_id>/summary', methods=['GET'])
# def get_summary(dataset_id):
#     """Return summary statistics for a specific dataset"""
#     if dataset_id not in summary_stats:
#         return jsonify({"error": "Summary not found"}), 404
    
#     return jsonify(summary_stats[dataset_id])

# @app.route('/api/datasets/<dataset_id>/analysis', methods=['POST'])
# def run_analysis(dataset_id):
#     """Run analysis on dataset based on input parameters"""
#     analysis_params = request.json
#     print(analysis_params)
    
#     # This is where you would implement your actual analysis logic
#     # For now, return a dummy response
#     result = {
#         "dataset_id": dataset_id,
#         "analysis_type": analysis_params.get("type", "default"),
#         "parameters": analysis_params,
#         "results": {
#             "p_value": 0.032,
#             "correlation": 0.78,
#             "significant_genes": ["TP53", "PIK3CA", "BRCA1"]
#         }
#     }
    
#     return jsonify(result)





api.add_resource(Datasets, '/api/datasets')
api.add_resource(ClinicalData, '/api/datasets/<dataset_name>/clinical')
api.add_resource(Summary, '/api/datasets/<dataset_name>/summary')
api.add_resource(Analysis, '/api/datasets/<dataset_name>/analysis')
api.add_resource(Heatmap, '/api/datasets/heatmap')
if __name__ == '__main__':
    app.run(debug=True, port=4000)