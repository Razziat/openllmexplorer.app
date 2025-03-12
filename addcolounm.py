from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

MODELS_DATABASE_URL = os.getenv("MODELS_DATABASE_URL")

engine = create_engine(MODELS_DATABASE_URL, future=True)

with engine.connect() as conn:
    # Vérifier si la colonne min_file_size existe déjà
    check_query = text("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = 'models' 
          AND COLUMN_NAME = 'min_file_size'
    """)
    result = conn.execute(check_query).mappings().all()
    if result:
        print("La colonne 'min_file_size' existe déjà dans la table models.")
    else:
        print("Ajout de la colonne 'min_file_size' dans la table models...")
        # Ajout de la colonne min_file_size de type BIGINT
        conn.execute(text("ALTER TABLE models ADD COLUMN min_file_size BIGINT"))
        conn.commit()
        print("Colonne 'min_file_size' ajoutée avec succès.")
