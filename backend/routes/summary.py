from flask import request
from flask_restful import Resource
from http import HTTPStatus
import json
from utils.database import get_db
from sqlalchemy import text
import os
import re

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter




from sqlalchemy import text
import json

def get_filtered_tables(db, str1, str2):
    # Query to get table names
    result = db.execute(text("SHOW TABLES")).fetchall()
    tables = [row[0] for row in result]

    # Filter table names
    filtered_tables = [table for table in tables if table.startswith(str1) and str2 not in table]

    # Get row count for each table
    table_data = {}
    total_rows = 0

    for table in filtered_tables:
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
        row_count = count_result[0] if count_result else 0
        table_data[table] = row_count
        total_rows += row_count

    # Calculate frequency
    for table in table_data:
        table_data[table] = {
            "row_count": table_data[table],
            "freq": round((table_data[table] / total_rows) * 100, 2) if total_rows > 0 else 0
        }

    # Add total row count
    table_data["total_rows"] = total_rows

    # Convert to JSON
    json.dumps(table_data, indent=4)



class Summary(Resource):
    def get(self, dataset_name):
        try:
            
            table_name = dataset_name + "_data_clinical_patient"
            table_name = "brca_tcga_pub2015_data_clinical_patient"
            dataset_name = "brca_tcga_pub2015"
            # This is a template - you will implement the actual database queries
            
            # Create an empty response object
            response_data = {}
            
            db = next(get_db())  # Retrieve the actual session
            
            # ===== PIE CHARTS =====
            
            # 1. Samples and Patients
            
            samples_count = db.execute(text(f"SELECT COUNT(DISTINCT id) FROM {dataset_name + '_data_clinical_sample'}")).scalar()
            patients_count = db.execute(text(f"SELECT COUNT(DISTINCT patient_id) FROM {dataset_name + '_data_clinical_patient'}")).scalar()
            
            response_data['samplesPerPatient'] = [
                {"category": "Samples", "value": samples_count},
                {"category": "Patients", "value": patients_count}
            ]
            
            
            
            # 2. Overall Survival Status
            # TODO: Replace with your database query
            # response_data['overallSurvivalStatus'] = [
            #     {"category": "Living", "value": 150},
            #     {"category": "Deceased", "value": 70}
            # ]
            
            living_count = db.execute(text(f"SELECT COUNT(DISTINCT patient_id) FROM {table_name} WHERE os_status = '0:LIVING'")).scalar()
            deceased_count = db.execute(text(f"SELECT COUNT(DISTINCT patient_id) FROM {table_name} WHERE os_status = '1:DECEASED'")).scalar()
            
            
            response_data['overallSurvivalStatus'] = [
                {"category": "Living", "value": living_count},
                {"category": "Deceased", "value": deceased_count}
            ]
            
            # 3. Sample Type
            # TODO: Replace with your database query
            
            primary_count = db.execute(text(f"SELECT count(*) FROM brca_tcga_pub2015_data_clinical_sample  WHERE sample_type = 'primary'")).scalar()
            metastasis_count = db.execute(text(f"SELECT count(*) FROM brca_tcga_pub2015_data_clinical_sample  WHERE sample_type <> 'primary'")).scalar()
            
            response_data['sampleType'] = [
                {"category": "Primary", "value": primary_count},
                {"category": "Metastasis", "value": metastasis_count}
            ]
            
            
            # 4. Sex
            
            male = db.execute(text(f"SELECT count(*) FROM {table_name} where sex = 'male'")).scalar()
            female = db.execute(text(f"SELECT count(*) FROM {table_name} where sex = 'female'")).scalar()
            response_data['sex'] = [
                {"category": "Female", "value": female},
                {"category": "Male", "value": male}
            ]
            
            # 5. Race Category
            # TODO: Replace with your database query
            
            result = db.execute(text(f"SELECT race, COUNT(*) AS patient_count FROM brca_tcga_pub2015_data_clinical_patient GROUP BY race")).mappings().all()
            response_data['raceCategory'] = []
            for row in result:
                response_data['raceCategory'].append({"category": row["race"], "value": row["patient_count"]})
                            
            # 6. Ethinicity Category
            # TODO: Replace with your database query
            result = db.execute(text(
                "SELECT ethnicity, COUNT(*) AS patient_count FROM brca_tcga_pub2015_data_clinical_patient GROUP BY ethnicity"
            )).mappings().all()

            response_data["ethnicityCategory"] = []

            for row in result:
                response_data["ethnicityCategory"].append({
                    "category": row["ethnicity"],
                    "value": row["patient_count"]
                })

            
            # 7. Adjuvant Postoperative Pharmaceutical Therapy
            # TODO: Replace with your database query
            response_data['adjuvantTherapy'] = [
                {"category": "NA", "value": 100},
                {"category": "Yes", "value": 90},
                {"category": "No", "value": 30}
            ]
            
            # 8. American Joint Committee on Cancer Metastasis
            result = db.execute(text(
                "SELECT PHARMACEUTICAL_TX_ADJUVANT, COUNT(*) AS patient_count FROM brca_tcga_pub2015_data_clinical_patient GROUP BY PHARMACEUTICAL_TX_ADJUVANT"
            )).mappings().all()

            response_data["ajccMetastasis"] = []

            for row in result:
                response_data["ajccMetastasis"].append({
                    "category": row["PHARMACEUTICAL_TX_ADJUVANT"],
                    "value": row["patient_count"]
                })

            
            # 9. American Joint Committee on Cancer Publication
            # TODO: Replace with your database query
            result = db.execute(text(
                "SELECT AJCC_METASTASIS_PATHOLOGIC_PM, COUNT(*) AS patient_count FROM brca_tcga_pub2015_data_clinical_patient GROUP BY AJCC_METASTASIS_PATHOLOGIC_PM"
            )).mappings().all()

            response_data["ajccPublication"] = []

            for row in result:
                response_data["ajccPublication"].append({
                    "category": row["AJCC_METASTASIS_PATHOLOGIC_PM"],
                    "value": row["patient_count"]
                })

            
            # 10. American Joint Committee on Cancer Tumor
            result = db.execute(text(
                "SELECT AJCC_STAGING_EDITION, COUNT(*) AS patient_count FROM brca_tcga_pub2015_data_clinical_patient GROUP BY AJCC_STAGING_EDITION"
            )).mappings().all()

            response_data["ajccTumor"] = []

            for row in result:
                response_data["ajccTumor"].append({
                    "category": row["AJCC_STAGING_EDITION"],
                    "value": row["patient_count"]
                })

            
            # ===== TABLES =====
            
            # 1. Genomic Profile Sample Counts
            
            result = db.execute(text("SHOW TABLES")).fetchall()
    
            tables = [row[0] for row in result]  # Use row[0] instead of row.values()

            # Filter table names
            filtered_tables = [ table for table in tables if not any(excluded in table for excluded in ["meta", "cases", "sample", "patient"])]
            filtered_tables = [ table for table in filtered_tables if table.startswith(dataset_name)]
            
            rep = {dataset_name: "", "data": "", "_": " "}
            table_new = [re.sub("|".join(rep.keys()), lambda m: rep[m.group()], table) for table in filtered_tables]

            # Initialize genomicProfile structure
            response_data["genomicProfile"] = {
                "columns": ["Molecular Profile", "# (Count)", "Frequency (%)"],
                "rows": []
            }

            total_rows = 0
            table_data = []
            
            # Get row count for each table
            for table, t in zip(filtered_tables, table_new):
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                row_count = count_result[0] if count_result else 0  # Use row[0] to access count
                total_rows += row_count
                table_data.append({"Molecular Profile": t.strip(), "# (Count)": row_count})

            # Calculate frequency
            for entry in table_data:
                entry["Frequency (%)"] = f"{round((entry['# (Count)'] / total_rows) * 100, 1) if total_rows > 0 else 0}"
                response_data["genomicProfile"]["rows"].append(entry)



            # 2. Cancer Type Detailed
            result = db.execute(text(
                "SELECT cancer_type_detailed, COUNT(*) AS cancer_type FROM brca_tcga_pub2015_data_clinical_sample GROUP BY cancer_type_detailed"
            )).mappings().all()

            response_data['cancerTypeDetailed'] = {
                "columns": ["Category", "# (Number of Samples)", "Frequency (%)"],
                "rows": []
            }

            total_samples = sum(row["cancer_type"] for row in result)

            for row in result:
                frequency = (row["cancer_type"] / total_samples) * 100
                response_data['cancerTypeDetailed']["rows"].append({
                    "Category": row["cancer_type_detailed"],
                    "# (Number of Samples)": row["cancer_type"],
                    "Frequency (%)": f"{frequency:.1f}"
                })
            
            # 3. Mutated Genes
            # TODO: Replace with your database query
            
            result = db.execute(text(
                "SELECT hugo_symbol, COUNT(*) AS occurrence_count FROM brca_tcga_pub2015_data_mutations GROUP BY hugo_symbol ORDER BY occurrence_count DESC LIMIT 50"
            )).mappings().all()

            total_mutations = sum(row["occurrence_count"] for row in result)

            response_data['mutatedGenes'] = {
                "columns": ["Gene", "Mutation (Mut)", "# (Count)", "Frequency (%)"],
                "rows": []
            }

            # Assuming you have a way to determine the mutation type (e.g., "Missense", "Frameshift") for each gene
            # This example assumes a placeholder function `get_mutation_type(gene)` that returns the mutation type
            def get_mutation_type(gene):
                # Placeholder logic for determining mutation type
                return "Missense"  # or "Frameshift", etc.

            for row in result:
                frequency = (row["occurrence_count"] / total_mutations) * 100
                mutation_type = get_mutation_type(row["hugo_symbol"])
                response_data['mutatedGenes']["rows"].append({
                    "Gene": row["hugo_symbol"],
                    "Mutation (Mut)": mutation_type,
                    "# (Count)": row["occurrence_count"],
                    "Frequency (%)": f"{frequency:.1f}"
                })
            
            # 4. CNA Genes
            result = db.execute(text(
                "SELECT gene, cytoband, CNA, num, freq FROM cna_gene ORDER BY num DESC LIMIT 100"
            )).mappings().all()

            response_data['cnaGenes'] = {
                "columns": ["Gene Cytoband", "CNA", "# (Count)", "Frequency (%)"],
                "rows": []
            }

            for row in result:
                response_data['cnaGenes']["rows"].append({
                    "Gene Cytoband": f"{row['gene']} {row['cytoband']}",
                    "CNA": row["CNA"],
                    "# (Count)": row["num"],
                    "Frequency (%)": f"{row['freq']:.1f}"
                })
            
                    
            # 5. Brachytherapy First Reference Point Administered Total Dose
            # TODO: Replace with your database query
            response_data['brachytherapy'] = {
                "columns": ["Category", "# (Count)", "Frequency (%)"],
                "rows": [
                    {"Category": "NA", "# (Count)": 180, "Frequency (%)": "81.8"},
                    {"Category": "40-50 Gy", "# (Count)": 25, "Frequency (%)": "11.4"},
                    {"Category": "30-40 Gy", "# (Count)": 15, "Frequency (%)": "6.8"}
                ]
            }
            
            # 6. Cent17 Copy Number
            # TODO: Replace with your database query
            response_data['cent17CopyNumber'] = {
                "columns": ["Category", "# (Count)", "Frequency (%)"],
                "rows": [
                    {"Category": "NA", "# (Count)": 160, "Frequency (%)": "72.7"},
                    {"Category": "2", "# (Count)": 30, "Frequency (%)": "13.6"},
                    {"Category": "3", "# (Count)": 20, "Frequency (%)": "9.1"},
                    {"Category": "4+", "# (Count)": 10, "Frequency (%)": "4.5"}
                ]
            }
            
            # ===== BAR CHARTS =====
            
            # 1. Mutation Count
            result = db.execute(text(
                "SELECT hugo_symbol, COUNT(*) AS gene_count FROM brca_tcga_pub2015_data_mutations GROUP BY hugo_symbol"
            )).mappings().all()

            # Initialize the range counters
            range_counts = {
                "0-10": 0,
                "11-20": 0,
                "21-30": 0,
                "31-40": 0,
                "41+": 0
            }

            # Categorize each gene count into the appropriate range
            for row in result:
                count = row["gene_count"]
                if count <= 10:
                    range_counts["0-10"] += 1
                elif count <= 20:
                    range_counts["11-20"] += 1
                elif count <= 30:
                    range_counts["21-30"] += 1
                elif count <= 40:
                    range_counts["31-40"] += 1
                else:
                    range_counts["41+"] += 1

            # Format the response data
            response_data['mutationCount'] = [
                {"range": "0-10", "count": range_counts["0-10"]},
                {"range": "11-20", "count": range_counts["11-20"]},
                {"range": "21-30", "count": range_counts["21-30"]},
                {"range": "31-40", "count": range_counts["31-40"]},
                {"range": "41+", "count": range_counts["41+"]}
            ]
            
            # 2. Fraction Genomic Altered
            result = db.execute(text(
                "SELECT n_genes_in_region, n_genes_in_peak FROM brca_tcga_pub2015_data_gistic_genes_amp"
            )).mappings().all()

            # Initialize the range counters for 10 groups with a step of 0.1
            range_counts = {f"{i/10}-{(i+1)/10}": 0 for i in range(10)}

            # Calculate the fraction and categorize into ranges
            for row in result:
                if row["n_genes_in_region"] > 0:  # Avoid division by zero
                    fraction = row["n_genes_in_peak"] / row["n_genes_in_region"]
                    # Determine the appropriate range
                    for i in range(10):
                        lower_bound = i / 10
                        upper_bound = (i + 1) / 10
                        if lower_bound <= fraction < upper_bound:
                            range_counts[f"{lower_bound}-{upper_bound}"] += 1
                            break

            # Format the response data
            response_data['fractionGenomicAltered'] = [
                {"range": range_key, "count": count} for range_key, count in range_counts.items()
            ]
            
            
            # 3. Birth from Initial Pathologic Diagnosis Date
            result = db.execute(text(
                "SELECT days_to_birth FROM brca_tcga_pub2015_data_clinical_patient where days_to_birth <> '[Not Available]'"
            )).mappings().all()

            # Extract the days_to_birth values
            days = [int(row["days_to_birth"]) for row in result]

            # Find the min and max days
            min_days = min(days)
            max_days = max(days)

            # Calculate the range step
            range_step = (max_days - min_days) / 6

            # Initialize the range counters
            range_counts = {f"{int(min_days + i * range_step)}-{int(min_days + (i + 1) * range_step)}": 0 for i in range(5)}
            range_counts[f"{int(min_days + 5 * range_step)}+"] = 0

            # Categorize each days_to_birth into the appropriate range
            for day in days:
                for i in range(5):
                    lower_bound = min_days + i * range_step
                    upper_bound = min_days + (i + 1) * range_step
                    if lower_bound <= day < upper_bound:
                        range_counts[f"{int(lower_bound)}-{int(upper_bound)}"] += 1
                        break
                else:
                    # If day is greater than the last upper bound, it falls into the last range
                    range_counts[f"{int(min_days + 5 * range_step)}+"] += 1

            # Format the response data
            response_data['birthFromDiagnosis'] = [
                {"range": range_key, "count": count} for range_key, count in range_counts.items()
            ]
            
            # 4. Days to Last Follow-up
            result = db.execute(text(
                "SELECT days_to_last_followup FROM brca_tcga_pub2015_data_clinical_patient where days_to_last_followup <> '[Not Available]'"
            )).mappings().all()

            # Extract the days_to_last_followup values
            followup_days = [int(row["days_to_last_followup"]) for row in result]

            # Find the min and max follow-up days
            min_days = min(followup_days)
            max_days = max(followup_days)

            # Calculate the range step
            range_step = (max_days - min_days) / 6

            # Initialize the range counters
            range_counts = {f"{int(min_days + i * range_step)}-{int(min_days + (i + 1) * range_step)}": 0 for i in range(5)}
            range_counts[f"{int(min_days + 5 * range_step)}+"] = 0

            # Categorize each days_to_last_followup into the appropriate range
            for day in followup_days:
                for i in range(5):
                    lower_bound = min_days + i * range_step
                    upper_bound = min_days + (i + 1) * range_step
                    if lower_bound <= day < upper_bound:
                        range_counts[f"{int(lower_bound)}-{int(upper_bound)}"] += 1
                        break
                else:
                    # If day is greater than the last upper bound, it falls into the last range
                    range_counts[f"{int(min_days + 5 * range_step)}+"] += 1

            # Format the response data
            response_data['daysToFollowup'] = [
                {"range": range_key, "count": count} for range_key, count in range_counts.items()
            ]
            
    
            
            # 5. Days to Sample Collection

            # Fetch the data from the database
            result = db.execute(text(
                "SELECT days_to_sample_collection_ FROM brca_tcga_pub2015_data_clinical_sample where days_to_sample_collection_ <> '[Not Available]'"
            )).mappings().all()

            # Convert the days_to_sample_collection_ values to integers
            collection_days = [int(row["days_to_sample_collection_"]) for row in result]

            # Calculate quantiles to create more balanced ranges
            quantiles = np.quantile(collection_days, [0, 0.2, 0.4, 0.6, 0.8, 1.0])

            # Initialize the range counters
            range_counts = {f"{int(quantiles[i])}-{int(quantiles[i+1])}": 0 for i in range(len(quantiles) - 1)}

            # Categorize each days_to_sample_collection_ into the appropriate range
            for day in collection_days:
                for i in range(len(quantiles) - 1):
                    lower_bound = quantiles[i]
                    upper_bound = quantiles[i + 1]
                    if lower_bound <= day < upper_bound:
                        range_counts[f"{int(lower_bound)}-{int(upper_bound)}"] += 1
                        break

            # Format the response data
            response_data['deathFromDiagnosis'] = [
                {"range": range_key, "count": count} for range_key, count in range_counts.items()
]
            
            
            # 6. Death from Initial Pathologic Diagnosis Date
            # Fetch the data from the database
            result = db.execute(text(
                "SELECT days_to_death FROM brca_tcga_pub2015_data_clinical_patient WHERE days_to_death <> '[NOT Applicable]'"
            )).mappings().all()

            # Convert the days_to_death values to integers
            death_days = [int(row["days_to_death"]) for row in result]

            # Calculate quantiles to create more balanced ranges
            quantiles = np.quantile(death_days, [0, 0.2, 0.4, 0.6, 0.8, 1.0])

            # Initialize the range counters
            range_counts = {f"{int(quantiles[i])}-{int(quantiles[i+1])}": 0 for i in range(len(quantiles) - 1)}

            # Categorize each days_to_death into the appropriate range
            for day in death_days:
                for i in range(len(quantiles) - 1):
                    lower_bound = quantiles[i]
                    upper_bound = quantiles[i + 1]
                    if lower_bound <= day < upper_bound:
                        range_counts[f"{int(lower_bound)}-{int(upper_bound)}"] += 1
                        break

            # Format the response data
            response_data['deathFromDiagnosis'] = [
                {"range": range_key, "count": count} for range_key, count in range_counts.items()
            ]
            
            # ===== DOT PLOTS =====
            
            # 1. Mutation Count vs Fraction Genome Altered
            result = db.execute(text(
                "SELECT t_ref_count, t_alt_count FROM brca_tcga_pub2015_data_mutations where t_ref_count > 0 and t_alt_count > 0 and t_alt_count/t_ref_count < 1"
            )).mappings().all()

            response_data['mutationVsFraction'] = []

            for row in result:
                t_ref_count = row["t_ref_count"]
                t_alt_count = row["t_alt_count"]
                
                # Calculate the fractionGenomeAltered, ensuring no division by zero
                if t_alt_count != 0:
                    fraction_genome_altered = t_alt_count / t_ref_count
                else:
                    fraction_genome_altered = None  # or handle as needed, e.g., set to 0 or skip

                # Append the data to the response if fraction_genome_altered is valid
                if fraction_genome_altered is not None:
                    response_data['mutationVsFraction'].append({
                        "mutationCount": t_ref_count,
                        "fractionGenomeAltered": fraction_genome_altered
                    })

            
            response_data['mutationVsFraction'] = response_data['mutationVsFraction'][:100]
                        
            # 2. KM Plot: Overall (months)
            
            result = db.execute(text(f"SELECT os_months, os_status FROM {table_name} WHERE os_months NOT LIKE '%Not Available%'")).mappings().all()

            df = pd.DataFrame(result)
            df['event'] = df['os_status'].apply(lambda x: 1 if x == '1:DECEASED' else 0)
            kmf = KaplanMeierFitter()
            kmf.fit(durations=df['os_months'], event_observed=df['event'])
            
            
            response_data['kmOverall'] = []
            
            for time, survival_prob in zip(kmf.survival_function_.index, kmf.survival_function_['KM_estimate']):
                censored = not df[df['os_months'] == time]['event'].any()

                response_data['kmOverall'].append({
                    "time": time,
                    "survival": survival_prob,
                    'censored': censored
                })
            
            
            # 3. KM Plot: Disease Free (months)
            # Fetch and process Disease-Free Survival (DFS) data
            result = db.execute(text(
                "SELECT dfs_months, dfs_status FROM brca_tcga_pub2015_data_clinical_patient WHERE dfs_months NOT LIKE '%Not Available%'"
            )).mappings().all()

            df_dfs = pd.DataFrame(result)
            df_dfs['event'] = df_dfs['dfs_status'].apply(lambda x: 1 if x == '1:Recurred/Progressed' else 0)  # Assuming '1' means an event occurred

            kmf_dfs = KaplanMeierFitter()
            kmf_dfs.fit(durations=df_dfs['dfs_months'], event_observed=df_dfs['event'])

            response_data['kmDiseaseFree'] = []

            for time, survival_prob in zip(kmf_dfs.survival_function_.index, kmf_dfs.survival_function_['KM_estimate']):
                censored = not df_dfs[df_dfs['dfs_months'] == time]['event'].any()

                response_data['kmDiseaseFree'].append({
                    "time": time,
                    "survival": survival_prob,
                    'censored': censored
                })




            
            return response_data, HTTPStatus.OK
            
        except Exception as e:
            return {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR