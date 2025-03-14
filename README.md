# OpenLLM Explorer

OpenLLM Explorer is a web application available on [https://www.openllmexplorer.app](https://www.openllmexplorer.app) developed in Flask that allows searching, filtering, and displaying open-source language models (LLM) based on various criteria (pipeline, required VRAM, number of downloads, etc.).  
The models and their information are retrieved from Hugging Face.

The application queries two MySQL databases:  
- **huggingfacemodel**: Contains information about the models (including a pre-calculated `min_file_size` column).
- **gpudb**: Contains information about GPUs.

## Features

- **Model search and filtering**  
  Filter by `pipeline_tag`, available VRAM, number of downloads, and minimum required size.
- **Detailed display**  
  Each model is presented as a clickable card displaying its ID, type (`pipeline_tag`), minimum required size, and number of downloads. A modal provides more details, including the list of associated files and a link to the HuggingFace repo.
- **GPU suggestions**  
  The GPU field provides real-time suggestions based on data from the `gpudb` database.

## Project Structure

```
.
├── app.py                      # Main Flask application
├── indexdb.py                  # Python script to add indexes to MySQL
└── templates
    └── index.html              # Main HTML template (uses Tailwind CSS)
```

## Prerequisites

- **Python 3.10+**
- **MySQL** with two databases: `huggingfacemodel` and `gpudb`
- **Virtualenv** (recommended)
- A `.env` file to store environment variables

## Installation and Configuration

### 1. Clone the repository

```bash
git clone https://github.com/your-username/openllm-explorer.git
cd openllm-explorer
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the `.env` file

Create a `.env` file in the project's root directory and add your connection variables:

```ini
MODELS_DATABASE_URL=mysql+pymysql://user:password@ip_database:port/huggingfacemodel
GPU_DATABASE_URL=mysql+pymysql://user:password@ip_database:port/gpudb
```

### 5. Update indexes (optional)

To improve performance, run the indexing script:

```bash
python indexdb.py
```

### Running in Development Mode

To test the application locally:

```bash
python app.py
```

The application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## License

This project is licensed under the MIT License.

## Contact

For any questions or contributions, please open an issue on GitHub or contact the maintainer. Or contact me on discord Razziat#4727
