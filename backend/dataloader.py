import os
import pandas as pd
import logging
import sys
import re
import glob
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import database_exists, create_database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/data_loader.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("data_loader")

# Database Configuration
DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_NAME = 'cancer_db'
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# SQLAlchemy setup
Base = declarative_base()


def get_engine(db_url=None):
    """Create and return a SQLAlchemy engine"""
    if db_url is None:
        db_url = DB_URL
    
    # Create database if it doesn't exist
    # First connect to MySQL without specifying a database
    root_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/"
    temp_engine = create_engine(root_url)
    
    # Create database if it doesn't exist
    if not database_exists(db_url):
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        logger.info(f"Created database: {DB_NAME}")
    
    # Create engine with the specified database
    engine = create_engine(db_url)
    return engine


def sanitize_column_name(col_name):
    """Convert column names to SQLAlchemy-compatible format"""
    # Replace spaces, special chars with underscores
    sanitized = re.sub(r'[^\w]', '_', str(col_name))
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = 'c_' + sanitized
    # Truncate if too long (MySQL has 64 char limit)
    if len(sanitized) > 64:
        sanitized = sanitized[:64]
    return sanitized.lower()


def create_dynamic_table_class(table_name, df, metadata):
    """Dynamically create a SQLAlchemy Table object based on DataFrame structure"""
    table_columns = [
        Column('id', Integer, primary_key=True, autoincrement=True)
    ]
    
    # Sanitize column names
    df.columns = [sanitize_column_name(col) for col in df.columns]
    
    # Add columns based on data types
    for col in df.columns:
        dtype = df[col].dtype
        
        if pd.api.types.is_integer_dtype(dtype):
            col_type = Integer
        elif pd.api.types.is_float_dtype(dtype):
            col_type = Float
        elif pd.api.types.is_bool_dtype(dtype):
            col_type = Boolean
        else:
            # Check if it's a long text
            max_len = df[col].astype(str).str.len().max()
            if max_len > 255:
                col_type = Text
            else:
                col_type = String(max(255, max_len))
        
        table_columns.append(Column(col, col_type))
    
    # Create table
    return Table(table_name, metadata, *table_columns)


def load_dataframe_to_table(engine, df, table_name):
    """Insert DataFrame contents into database table using SQLAlchemy"""
    try:
        # Sanitize column names
        df.columns = [sanitize_column_name(col) for col in df.columns]
        
        # Use the to_sql method of pandas with SQLAlchemy engine
        # If table exists, append to it
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            chunksize=1000  # Insert in chunks to prevent memory issues
        )
        
        logger.info(f"Successfully loaded data into {table_name}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error loading data into {table_name}: {e}")
        return False


def process_data_file(engine, file_path, dataset_name):
    """Process individual data file and load into database using SQLAlchemy"""
    try:
        # Extract file type from name
        file_name = os.path.basename(file_path)
        file_type = file_name.split('.')[0]  # e.g., data_clinical_patient
        
        # Check if the file is in a case_list directory
        if 'case_lists' in file_path:
            # For case_list files, use a special prefix to distinguish them
            directory_path = os.path.dirname(file_path)
            relative_path = os.path.relpath(directory_path, os.path.join(os.path.dirname(directory_path), '..'))
            
            # Create table name with case_list prefix
            table_name = f"{dataset_name}_case_list_{file_type}"
        else:
            # Standard file naming for main directory files
            table_name = f"{dataset_name}_{file_type}"
            
        table_name = sanitize_column_name(table_name)
        
        logger.info(f"Processing file: {file_path}")
        
        # Determine file format and read data
        if 'case_lists' in file_path:
            # Special handling for case_list files with the format:
            # key: value
            # case_list_ids: ID1 ID2 ID3...
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Parse lines into a dictionary
                metadata = {}
                case_ids = []
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Special handling for case_list_ids line which contains tab/space separated IDs
                    if line.startswith('case_list_ids:'):
                        # Extract everything after the colon and split on whitespace
                        case_ids_str = line.split(':', 1)[1].strip()
                        # Split by any whitespace (space, tab, etc.)
                        case_ids = re.split(r'\s+', case_ids_str)
                        # Filter out any empty strings
                        case_ids = [cid for cid in case_ids if cid]
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                
                # Better handle the case_list files format
                # Create a separate table for metadata and cases
                
                # 1. Create metadata table first (one row with all metadata)
                # Extract stable_id if available for better naming
                stable_id = metadata.get('stable_id', 'case_list')
                meta_table_name = f"{dataset_name}_meta_{stable_id}"
                meta_table_name = sanitize_column_name(meta_table_name)
                
                # Create DataFrame for metadata
                meta_df = pd.DataFrame([metadata])
                
                # Create metadata table and load data
                meta_table = create_dynamic_table_class(meta_table_name, meta_df, MetaData())
                meta_table.metadata.create_all(engine)
                load_dataframe_to_table(engine, meta_df, meta_table_name)
                logger.info(f"Created and loaded metadata table: {meta_table_name}")
                
                # 2. Create cases table (one row per case ID with reference to metadata)
                cases_table_name = f"{dataset_name}_cases_{stable_id}"
                cases_table_name = sanitize_column_name(cases_table_name)
                
                # Create DataFrame for cases
                case_rows = []
                for case_id in case_ids:
                    case_rows.append({
                        'case_id': case_id,
                        'stable_id': stable_id,
                        'dataset': dataset_name
                    })
                
                if case_rows:
                    cases_df = pd.DataFrame(case_rows)
                    
                    # Create cases table and load data
                    cases_table = create_dynamic_table_class(cases_table_name, cases_df, MetaData())
                    cases_table.metadata.create_all(engine)
                    load_dataframe_to_table(engine, cases_df, cases_table_name)
                    logger.info(f"Created and loaded cases table with {len(case_rows)} cases: {cases_table_name}")
                
                # No need to continue with standard processing
                return
                
            except Exception as e:
                logger.error(f"Error parsing case_list file {file_path}: {e}")
                logger.error(f"Falling back to standard parsing for {file_path}")
                # Fallback to standard parsing
                try:
                    df = pd.read_csv(file_path, comment='#')
                except:
                    try:
                        # Try with no separator (just plain text)
                        df = pd.read_csv(file_path, sep=None, engine='python', comment='#', header=None)
                    except:
                        # Last resort: read as single column
                        with open(file_path, 'r') as f:
                            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        df = pd.DataFrame({'content': lines})
        
        elif file_path.endswith('.txt') or file_path.endswith('.tsv'):
            # Try different parameters to handle various formats
            try:
                # First try with headers
                df = pd.read_csv(file_path, comment='#')
            except:
                # If that fails, try without headers
                df = pd.read_csv(file_path, comment='#', header=None)
                
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.seg'):
            # Special handling for segment files
            df = pd.read_csv(file_path)
        else:
            logger.warning(f"Skipping unsupported file format: {file_path}")
            return
        
        # Skip empty dataframes
        if df.empty:
            logger.warning(f"File {file_path} is empty, skipping")
            return
            
        # Create metadata object
        metadata = MetaData()
        
        # Create table definition
        table = create_dynamic_table_class(table_name, df, metadata)
        
        # Create table in the database
        metadata.create_all(engine)
        logger.info(f"Created table: {table_name}")
        
        # Load data into the table
        load_dataframe_to_table(engine, df, table_name)
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")


def load_dataset(engine, dataset_path, dataset_name):
    """Load all files from a dataset directory including the case_list subdirectory"""
    logger.info(f"Loading dataset: {dataset_name} from {dataset_path}")
    
    # Get all files in the main dataset directory
    data_files = []
    for ext in ['*.csv']:
        data_files.extend(glob.glob(os.path.join(dataset_path, ext)))
    
    # Check for case_list directory
    case_list_dir = os.path.join(dataset_path, 'case_lists')
    if os.path.isdir(case_list_dir):
        logger.info(f"Found case_lists directory in {dataset_name}")
        # Get all files from the case_list directory
        for ext in ['*.txt', '*.csv', '*.tsv']:
            case_files = glob.glob(os.path.join(case_list_dir, ext))
            # Add to our list of files to process
            data_files.extend(case_files)
    
    logger.info(f"Found {len(data_files)} files to process")
    
    # Process each file
    for file_path in data_files:
        process_data_file(engine, file_path, dataset_name)
    
    logger.info(f"Completed loading dataset: {dataset_name}")


def main():
    """Main function to load all datasets"""
    try:
        # Create SQLAlchemy engine
        engine = get_engine()
        
        # Read dataset names from file
        try:
            df = pd.read_csv('./datasets/datasets.csv')
            datasets = df['name'].to_list()
        except Exception as e:
            logger.error(f"Error reading datasets file: {e}")
            return
        
        logger.info(f"Found {len(datasets)} datasets to load")
        
        # Process each dataset
        for dataset in datasets:
            dataset_path = os.path.join('datasets', dataset)
            if os.path.isdir(dataset_path):
                load_dataset(engine, dataset_path, dataset)
            else:
                logger.warning(f"Dataset directory not found: {dataset_path}")
        
        logger.info("Data loading process completed")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()