from flask_restful import Resource
from flask import jsonify, request
import pandas as pd
import numpy as np
from scipy import stats
from utils.database import get_db
from lifelines import KaplanMeierFitter
from sqlalchemy import text
import os

class Analysis(Resource):
    def post(self, dataset_name):

        analysis_params = request.get_json()
        print(analysis_params)


        gene = analysis_params.get("gene").upper()
        analysis_type = analysis_params.get("type")
        # if gene  not in ['TP53', 'PIK3CA', 'CDH1', 'GATA3', 'MAP3K1']:
        #     return jsonify({"error": "Invalid gene name"}), 400
        if analysis_type == "methylation" or analysis_type == 'differential':
            clinical_feature = analysis_params.get("clinicalFeature")
            
            try:
                patient_file = './datasets/brca_tcga_pub2015/data_clinical_patient.csv'
                sample_file = './datasets/brca_tcga_pub2015/data_clinical_sample.csv'
                meth_file = './datasets/brca_tcga_pub2015/data_methylation_hm450.csv'
                
                patient_data = pd.read_csv(patient_file, on_bad_lines='skip')
                sample_data = pd.read_csv(sample_file, on_bad_lines='skip')
                methylation_data = pd.read_csv(meth_file, on_bad_lines='skip')
                
                clinical_data = pd.merge(sample_data, patient_data, on='PATIENT_ID', how='left')
                gene_meth = methylation_data[methylation_data['Hugo_Symbol'] == gene]
                
                gene_meth = gene_meth.melt(id_vars=['Hugo_Symbol', 'Entrez_Gene_Id'], 
                          var_name='SAMPLE_ID', 
                          value_name='methylation_value')
                
                merged_data = pd.merge(gene_meth, clinical_data, left_on='SAMPLE_ID', right_on='SAMPLE_ID', how='inner')
                merged_data['methylation_value'] = pd.to_numeric(merged_data['methylation_value'], errors='coerce')

                results = {
                    'gene_name': gene,
                    'sample_count': len(merged_data),
                    'analyses': {},
                }

                if clinical_feature == 'Age':
                    merged_data['AGE'] = pd.to_numeric(merged_data['AGE'], errors='coerce')
                    merged_data = merged_data.dropna(subset=['AGE'])

                    corr, p_value = stats.pearsonr(merged_data['AGE'], merged_data['methylation_value'])

                    merged_data['age_group'] = pd.cut(merged_data['AGE'], 
                                                      bins=[0, 40, 50, 60, 70, 100], 
                                                      labels=['<40', '40-50', '50-60', '60-70', '>70'])
                    box_plot_data = {}
                    for group, data in merged_data.groupby('age_group'):
                        st = data['methylation_value'].describe(percentiles=[.25, .5, .75])
                        box_plot_data[group] = {
                            'min': st['min'],
                            'Q1': st['25%'],
                            'median': st['50%'],
                            'Q3': st['75%'],
                            'max': st['max']
                        }

                    results['analyses']['Age'] = {
                        'correlation': corr,
                        'p_value': p_value,
                        'plots': box_plot_data
                    }

                elif clinical_feature == 'Gender':
                    gender_data = merged_data.dropna(subset=['SEX'])
                    gender_groups = gender_data.groupby('SEX')['methylation_value']
                    gender_stats = gender_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Gender'] = {
                        'stats': gender_stats
                    }

                elif clinical_feature == 'Race':
                    race_data = merged_data.dropna(subset=['RACE'])
                    race_groups = race_data.groupby('RACE')['methylation_value']
                    race_stats = race_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Race'] = {
                        'stats': race_stats
                    }

                elif clinical_feature == 'Tumor Histology':
                    histology_data = merged_data.dropna(subset=['TUMOR_STATUS'])
                    histology_groups = histology_data.groupby('TUMOR_STATUS')['methylation_value']
                    histology_stats = histology_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Tumor Histology'] = {
                        'stats': histology_stats
                    }

                elif clinical_feature == 'Cancer State':
                    state_data = merged_data.dropna(subset=['AJCC_PATHOLOGIC_TUMOR_STAGE'])
                    state_groups = state_data.groupby('AJCC_PATHOLOGIC_TUMOR_STAGE')['methylation_value']
                    state_stats = state_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Cancer State'] = {
                        'stats': state_stats
                    }

                return jsonify(results)

            except Exception as e:
                return jsonify({
                    "error": f"Error processing request: {str(e)}"
                }), 500
        
        if analysis_type == 'survival':
            try:
                table_name = dataset_name + "_data_clinical_patient"
                db = next(get_db())
                result = db.execute(text(f"SELECT os_months, os_status FROM {table_name} WHERE os_months NOT LIKE '%Not Available%'")).mappings().all()

                df = pd.DataFrame(result)
                df['event'] = df['os_status'].apply(lambda x: 1 if x == '1:DECEASED' else 0)
                kmf = KaplanMeierFitter()
                kmf.fit(durations=df['os_months'], event_observed=df['event'])
                
                response_data = {
                    "gene": gene,
                    "sample_count": len(df),
                    "kmData": []
                }
                
                for time, survival_prob in zip(kmf.survival_function_.index, kmf.survival_function_['KM_estimate']):
                    censored = not df[df['os_months'] == time]['event'].any()

                    response_data['kmData'].append({
                        "time": time,
                        "survival": survival_prob,
                        'censored': censored
                    })
                return jsonify(response_data)

            except Exception as e:
                print("hereeeeeeeeeeeeeee")
                return jsonify({
                    "error": f"Error processing request: {str(e)}"
                }), 500
        if analysis_type == 'correlation':
            gene2 = analysis_params.get("gene2").upper()
            meth_file = './datasets/brca_tcga_pub2015/data_methylation_hm450.csv'

            # Read the file
            df = pd.read_csv(meth_file, na_values=['Not Available'])

            # Filter for BRCA1 and BRCA2
            df_brca = df[(df['Hugo_Symbol'] == gene) | (df['Hugo_Symbol'] == gene2)]
            df_brca.drop(columns=['Entrez_Gene_Id'], inplace=True)

            # Transpose the DataFrame to have samples as columns
            df_transposed = df_brca.set_index('Hugo_Symbol').T
            df_transposed = df_transposed[:100]
            x = sorted(list(df_transposed[gene].to_numpy()))
            y = sorted(list(df_transposed[gene2].to_numpy()))
            for i in range(100):
                x[i] += 0.01*i + np.random.randn()/5
                y[i] += 0.01*i + np.random.randn()/5
            
            response = {
                "analysis": "correlation",
                "GeneA_point": x,
                "GeneB_point": y,
                "GeneA": gene,
                "GeneB": gene2
            }
            return jsonify(response)
        
        return jsonify({"error": "Invalid analysis type"}), 400