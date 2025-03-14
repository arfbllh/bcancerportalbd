from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import plotly.graph_objects as go
import json
from functools import lru_cache
import plotly
from flask_restful import Resource, Api
import numpy as np


class Heatmap(Resource):
    def get(self):
        try:
            # Load data
            df = load_and_process_data()
            
            # Create a hash of the data to use as a cache key
            data_hash = hash(df.values.tobytes())
            
            # Get cached figure
            fig = create_figure(data_hash)
            
            # Convert to JSON with reduced precision
            plotly_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plotly_json
        except Exception as e:
            return {"error": str(e)}, 500

@lru_cache(maxsize=1)
def load_and_process_data():
    file_path = "./datasets/brca_tcga_pub2015/data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv"
    df = pd.read_csv(file_path)
    df = df.iloc[:200, :200]
    df.set_index("Hugo_Symbol", inplace=True)
    df.drop(columns=["Entrez_Gene_Id"], inplace=True)
    df = df.apply(pd.to_numeric, errors='coerce')
    df.fillna(0, inplace=True)
    return df

# Cache the figure creation
@lru_cache(maxsize=1)
def create_figure(data_hash):
    df = load_and_process_data()
    
    # Round values to 2 decimal places to reduce data size
    z_values = np.round(df.values, 2)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=df.columns.tolist(),
        y=df.index.tolist(),
        colorscale='RdBu_r',
        colorbar=dict(title='Expression Level'),
        hoverongaps=False,
        hovertemplate='Gene: %{y}<br>Sample: %{x}<br>Expression: %{z:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Gene Expression Heatmap',
        xaxis=dict(
            title='Samples',
            tickangle=45,
            showticklabels=True,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title='Genes',
            showticklabels=True,
            tickfont=dict(size=10),
        ),
        width=1200,
        height=800,
        margin=dict(l=100, r=50, t=50, b=100)
    )
    
    return fig