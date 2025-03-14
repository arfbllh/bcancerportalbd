from sqlalchemy import create_engine, Column, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connection string with root username and blank password
connection_string = "mysql+pymysql://root:@localhost/cancer_db"

# Create engine and connect to the database
engine = create_engine(connection_string)
Base = declarative_base()

# Define the Dataset model
class Dataset(Base):
    __tablename__ = 'dataset'
    
    name = Column(String(255), primary_key=True)
    type = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"Dataset(name='{self.name}', type='{self.type}')"

# Create the table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Data to be inserted
datasets = [
    Dataset(name='brca_tcga_pub2015', type='Invasive Breast Carcinoma'),
    Dataset(name='brca_tcga', type='Invasive Breast Carcinoma'),
    Dataset(name='brca_tcga_pan_can_atlas_2018', type='Invasive Breast Carcinoma'),
    Dataset(name='brca_tcga_pub', type='Invasive Breast Carcinoma'),
    Dataset(name='brca_tcga_gdc', type='Invasive Breast Carcinoma'),
    Dataset(name='breast_cptac_gdc', type='Breast'),
    Dataset(name='bfn_duke_nus_2015', type='Breast Fibroepithelial Neoplasms'),
    Dataset(name='mbc_msk_2021', type='Metaplastic Breast Cancer')
]

# Add all records to the session
session.add_all(datasets)

# Commit the transaction
session.commit()

# Verify the data was inserted correctly
print("Contents of dataset table:")
for dataset in session.query(Dataset).all():
    print(f"Name: {dataset.name}, Type: {dataset.type}")

# Close the session
session.close()