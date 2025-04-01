# backup.py
import os
import shutil
import logging

def criar_backup(diretorio_alvo):
    pasta_backup = os.path.join(diretorio_alvo, "PDF_Backups")
    os.makedirs(pasta_backup, exist_ok=True)
    for raiz, _, arquivos in os.walk(diretorio_alvo):
        if os.path.abspath(raiz).startswith(os.path.abspath(pasta_backup)):
            continue
        for arquivo in arquivos:
            if arquivo.lower().endswith(".pdf"):
                caminho_origem = os.path.join(raiz, arquivo)
                rel_path = os.path.relpath(raiz, diretorio_alvo)
                destino_dir = os.path.join(pasta_backup, rel_path)
                os.makedirs(destino_dir, exist_ok=True)
                try:
                    shutil.copy2(caminho_origem, os.path.join(destino_dir, arquivo))
                    logging.info(f"Backup criado: {caminho_origem} -> {destino_dir}")
                except Exception as e:
                    logging.error(f"Erro ao criar backup de {caminho_origem}: {e}")

def reverter_backup(diretorio_alvo):
    pasta_backup = os.path.join(diretorio_alvo, "PDF_Backups")
    if not os.path.exists(pasta_backup):
        raise Exception("Pasta de backup não encontrada.")
    for raiz, _, arquivos in os.walk(pasta_backup):
        for arquivo in arquivos:
            if arquivo.lower().endswith(".pdf"):
                caminho_backup = os.path.join(raiz, arquivo)
                rel_path = os.path.relpath(raiz, pasta_backup)
                caminho_original = os.path.join(diretorio_alvo, rel_path, arquivo)
                try:
                    shutil.copy2(caminho_backup, caminho_original)
                    logging.info(f"Revertido: {caminho_backup} -> {caminho_original}")
                except Exception as e:
                    logging.error(f"Erro ao reverter {caminho_backup}: {e}")
