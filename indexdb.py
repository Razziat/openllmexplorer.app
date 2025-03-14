from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

MODELS_DATABASE_URL = os.getenv("MODELS_DATABASE_URL")

engine = create_engine(MODELS_DATABASE_URL, future=True)

with engine.connect() as conn:
    # Index sur la colonne pipeline_tag dans la table models (en utilisant un préfixe de 255 caractères)
    result = conn.execute(text("SHOW INDEX FROM models WHERE Key_name = 'idx_pipeline_tag'")).mappings().all()
    if not result:
        print("Création de l'index idx_pipeline_tag sur models...")
        conn.execute(text("ALTER TABLE models ADD INDEX idx_pipeline_tag (pipeline_tag(255))"))
    else:
        print("L'index idx_pipeline_tag existe déjà sur models.")

    # Index sur la colonne model_id dans la table model_files (si nécessaire, avec un préfixe de 255)
    result = conn.execute(text("SHOW INDEX FROM model_files WHERE Key_name = 'idx_model_id'")).mappings().all()
    if not result:
        print("Création de l'index idx_model_id sur model_files...")
        conn.execute(text("ALTER TABLE model_files ADD INDEX idx_model_id (model_id(255))"))
    else:
        print("L'index idx_model_id existe déjà sur model_files.")

    conn.commit()

print("Les index ont été mis à jour avec succès.")
