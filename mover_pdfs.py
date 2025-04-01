# mover_pdfs.py
import os
import shutil

def operacao_apostila(diretorio_base, barra_progresso, rotulo_progresso, log_callback=None):
    diretorio_base = os.path.abspath(diretorio_base)
    destino_apostila = os.path.join(diretorio_base, "Apostila")
    destino_resumos = os.path.join(destino_apostila, "Resumos, Slides, Mapas Mentais")
    os.makedirs(destino_apostila, exist_ok=True)
    os.makedirs(destino_resumos, exist_ok=True)

    if log_callback:
        log_callback(f'Operando no diretório: {diretorio_base}')

    lista_copias = []
    for raiz, _, arquivos in os.walk(diretorio_base):
        # Ignora pastas já criadas para a operação
        if "apostila" in os.path.basename(raiz).lower():
            continue
        for arquivo in arquivos:
            if not arquivo.lower().endswith(".pdf"):
                continue
            caminho_origem = os.path.join(raiz, arquivo)
            nome_sem_ext = os.path.splitext(arquivo)[0].lower()
            # Critério 1: se o nome contém "completo", "grifado" ou "simplificado"
            if ("completo" in nome_sem_ext) or ("grifado" in nome_sem_ext) or ("simplificado" in nome_sem_ext):
                lista_copias.append((caminho_origem, destino_apostila))
            # Critério 2: se o arquivo ou a pasta contém "resumos, slides, mapas mentais"
            if ("resumos, slides, mapas mentais" in arquivo.lower()) or ("resumos, slides, mapas mentais" in raiz.lower()):
                lista_copias.append((caminho_origem, destino_resumos))

    total = len(lista_copias)
    if log_callback:
        log_callback(f"Total de arquivos a copiar: {total}")

    for i, (origem, destino) in enumerate(lista_copias):
        try:
            shutil.copy2(origem, os.path.join(destino, os.path.basename(origem)))
            if log_callback:
                log_callback(f"Copiado: {os.path.basename(origem)} para {destino}")
        except Exception as erro:
            if log_callback:
                log_callback(f"Erro ao copiar {os.path.basename(origem)} para {destino}: {erro}")
        barra_progresso["value"] = i + 1
        rotulo_progresso.config(text=f"Copiando: {i+1}/{total} arquivos")
    rotulo_progresso.config(text="Operação Apostila Concluída!")
    if log_callback:
        log_callback("Operação Apostila finalizada.")
