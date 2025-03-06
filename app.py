from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, text
import re
import os

load_dotenv()

app = Flask(__name__)

# Chaînes de connexion PostgreSQL (à adapter selon votre configuration)
MODELS_DATABASE_URL = os.getenv("MODELS_DATABASE_URL")
GPU_DATABASE_URL = os.getenv("GPU_DATABASE_URL")

# Création des moteurs SQLAlchemy
models_engine = create_engine(MODELS_DATABASE_URL, future=True)
gpu_engine = create_engine(GPU_DATABASE_URL, future=True)

### PARTIE MODELS ###

def get_model_db_connection():
    return models_engine.connect()

def compute_min_total_size(files_list):
    """
    Calcule la taille totale minimale pour un modèle.
    Pour les fichiers multipart, recherche le pattern "-<number>-of-<number>" dans le nom,
    regroupe par ensemble (clé = préfixe + "-of-" + nombre total) et somme les tailles
    uniquement si l’ensemble est complet (nombre de fichiers trouvés == nombre total indiqué).
    Les fichiers individuels sont également pris en compte.
    Retourne le minimum de ces totaux, ou None s'il n'y a aucun fichier.
    """
    multipart_groups = {}
    individual_sizes = []
    pattern = re.compile(r'-(\d+)-of-(\d+)')
    for f in files_list:
        fname = f["filename"]
        size = f["size_bytes"]
        m = pattern.search(fname)
        if m:
            total_files = int(m.group(2))
            prefix = fname.split('-' + m.group(1) + '-of-')[0]
            group_key = prefix + "-of-" + m.group(2)
            if group_key not in multipart_groups:
                multipart_groups[group_key] = {"total_size": 0, "count": 0, "expected": total_files}
            multipart_groups[group_key]["total_size"] += size
            multipart_groups[group_key]["count"] += 1
        else:
            individual_sizes.append(size)
    totals = []
    for group in multipart_groups.values():
        if group["count"] == group["expected"]:
            totals.append(group["total_size"])
    totals.extend(individual_sizes)
    return min(totals) if totals else None

@app.route('/api/models')
def api_models():
    # Récupération des paramètres
    pipeline = request.args.get('pipeline')
    vram = request.args.get('vram', type=float)  # VRAM en GB
    sort_by = request.args.get('sort_by', default="downloads")
    order = request.args.get('order', default="desc")
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    offset = (page - 1) * limit

    # Requête SQL initiale : on filtre uniquement par pipeline
    filters = "WHERE 1=1"
    params = {}
    if pipeline:
        filters += " AND pipeline_tag ILIKE :pipeline"
        params['pipeline'] = f"%{pipeline}%"

    conn = get_model_db_connection()
    query = text("SELECT * FROM models " + filters)
    models_result = conn.execute(query, params).mappings().all()

    models_list = []
    # Pour chaque modèle, on calcule min_file_size à partir des fichiers
    for model in models_result:
        m_dict = dict(model)
        files_result = conn.execute(
            text("SELECT model_id, filename, file_type, size_bytes FROM model_files WHERE model_id = :model_id"),
            {"model_id": m_dict["model_id"]}
        ).mappings().all()
        files_list = [dict(row) for row in files_result]
        m_dict["files"] = files_list
        m_dict["min_file_size"] = compute_min_total_size(files_list)
        models_list.append(m_dict)
    conn.close()

    # Filtrage selon la VRAM (appliqué après avoir calculé min_file_size)
    if vram is not None:
        vram_bytes = vram * 1e9
        models_list = [
            m for m in models_list 
            if m["min_file_size"] is not None and m["min_file_size"] <= vram_bytes
        ]

    # Tri selon le critère choisi
    if sort_by == "downloads":
        models_list.sort(key=lambda m: m.get("downloads", 0), reverse=(order == "desc"))
    elif sort_by == "min_file_size":
        models_list.sort(key=lambda m: m["min_file_size"] if m["min_file_size"] is not None else float('inf'),
                         reverse=(order == "desc"))

    # Pagination appliquée sur la liste finale
    paginated_models = models_list[offset: offset + limit]
    return jsonify({
        "page": page,
        "limit": limit,
        "models": paginated_models
    })


### PARTIE GPU ###

def get_gpu_db_connection():
    return gpu_engine.connect()

@app.route('/api/gpus')
def api_gpus():
    conn = get_gpu_db_connection()
    tables_result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).mappings().all()
    tables = [row['table_name'] for row in tables_result]
    
    gpu_list = []
    for table in tables:
        cols_result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = :table"), {"table": table}).mappings().all()
        columns = [row['column_name'] for row in cols_result]
        model_col = None
        for col in columns:
            if col.lower() == "model":
                model_col = col
                break
        mem_col = None
        for col in columns:
            if col.lower() == "memory size (mb)":
                mem_col = col
                break
        if model_col and mem_col:
            try:
                rows = conn.execute(text(f'SELECT "{model_col}" as model_name, "{mem_col}" as memory_mb FROM "{table}"')).mappings().all()
                for row in rows:
                    gpu_list.append({
                        "name": row["model_name"],
                        "memory_mb": row["memory_mb"]
                    })
            except Exception as e:
                print(f"Erreur dans la table {table}: {e}")
        else:
            if columns:
                first_col = columns[0]
                rows = conn.execute(text(f'SELECT "{first_col}" as model_name FROM "{table}"')).mappings().all()
                for row in rows:
                    gpu_list.append({
                        "name": row["model_name"],
                        "memory_mb": None
                    })
    conn.close()
    gpu_list = [g for g in gpu_list if g["name"] is not None]
    unique = {}
    for gpu in gpu_list:
        if gpu["name"] not in unique:
            unique[gpu["name"]] = gpu
    return jsonify(sorted(list(unique.values()), key=lambda x: x["name"].lower()))

### Interface principale ###

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
