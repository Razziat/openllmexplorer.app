# OpenLLM Explorer

OpenLLM Explorer est une application web développée en Flask qui permet de rechercher, filtrer et afficher des modèles de langage (LLM) open source en fonction de différents critères (pipeline, VRAM requise, nombre de téléchargements, etc.).  
L’application interroge deux bases de données MySQL :
- **huggingfacemodel** : Contient les informations sur les modèles (y compris une colonne pré-calculée `min_file_size`).
- **gpudb** : Contient les informations sur les GPU.

L’interface utilisateur est conçue avec Tailwind CSS. L’application est déployée en production à l’aide de Gunicorn, avec Nginx (ou Caddy) comme reverse proxy et gestion automatique des certificats SSL.

## Fonctionnalités

- **Recherche et filtrage de modèles**  
  Filtre par pipeline_tag, VRAM disponible, nombre de téléchargements et taille minimale requise.
- **Affichage détaillé**  
  Chaque modèle est présenté sous forme de carte cliquable affichant son ID, son type (pipeline_tag), la taille minimale requise et le nombre de téléchargements. Un modal fournit plus de détails, y compris la liste des fichiers associés.
- **Suggestions GPU**  
  Le champ GPU propose des suggestions en temps réel à partir des données de la base `gpudb`.
- **Optimisation des performances**  
  Pré-calcul de la colonne `min_file_size` et indexation des colonnes critiques pour accélérer la recherche.
- **Déploiement sécurisé**  
  Utilisation de Gunicorn et Nginx (ou Caddy) pour la production, avec des certificats SSL gérés automatiquement.

## Structure du projet

. ├── app.py # Application Flask principale ├── indexdb.py # Script Python pour ajouter des index sur MySQL ├── update_min_file_size.py # Script pour pré-calculer et mettre à jour min_file_size dans la table models └── templates └── index.html # Template HTML principal (utilise Tailwind CSS)

## Prérequis

- **Python 3.10+**
- **MySQL** avec deux bases de données : `huggingfacemodel` et `gpudb`
- Un VPS Ubuntu ou autre système compatible
- **Virtualenv** (recommandé)
- **Gunicorn** pour la production
- **Nginx** ou **Caddy** comme reverse proxy
- Un fichier `.env` pour stocker vos variables d’environnement

## Installation et Configuration

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/openllm-explorer.git
cd openllm-explorer
2. Créer et activer un environnement virtuel
bash
Copier
python -m venv venv
source venv/bin/activate   # Sous Windows : venv\Scripts\activate
3. Installer les dépendances
bash
Copier
pip install -r requirements.txt
Exemple de contenu de requirements.txt :

nginx
Copier
Flask
SQLAlchemy
PyMySQL
python-dotenv
gunicorn
4. Configurer le fichier .env
Créez un fichier .env à la racine du projet et ajoutez-y vos variables de connexion :

dotenv
Copier
MODELS_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/huggingfacemodel
GPU_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/gpudb
5. Mettre à jour les index (optionnel)
Pour améliorer les performances, exécutez le script d'indexation :

bash
Copier
python indexdb.py
6. Mettre à jour la colonne min_file_size (optionnel)
Si la colonne min_file_size n'est pas encore renseignée, utilisez le script suivant pour la mettre à jour :

bash
Copier
python update_min_file_size.py
Exécution en mode développement
Pour tester localement l’application :

bash
Copier
python app.py
L’application sera accessible à l’adresse http://127.0.0.1:5000.

Licence
Ce projet est sous licence MIT.

Contact
Pour toute question ou contribution, veuillez ouvrir une issue sur GitHub ou contacter le mainteneur.


