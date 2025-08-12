from huggingface_hub import upload_file
import tempfile
from pathlib import Path
import json
import os
import shutil
import subprocess

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploadedfile(uploaded_file):
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def create_repo(repo_id, exist_ok, token):
    repo_url = f"https://huggingface.co/{repo_id}"
    repo_path = repo_id.split("/")[-1]
    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", repo_url], check=True)
    return repo_path


def upload_json_card(model_card: dict, repo_id: str, token: str):
    repo_path = create_repo(repo_id, exist_ok=True, token=token)
    file_name = "model_card.json"
    with open(file_name, "w") as f:
        json.dump(model_card, f)
    shutil.copy(file_name, os.path.join(repo_path, file_name))
    subprocess.run(["git", "add", file_name], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Add {file_name}"], cwd=repo_path, check=True
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True)
    return f"https://huggingface.co/{repo_id}"


def upload_readme_card(readme_text: str, repo_id: str, token: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "README.md"
        tmp_path.write_text(readme_text)
        return upload_file(
            path_or_fileobj=str(tmp_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            token=token,
            repo_type="model",
        )
