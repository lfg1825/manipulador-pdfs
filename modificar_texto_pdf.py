# modificar_texto_pdf.py
import fitz
import os
import logging

def modificar_texto_no_pdf(caminho_pdf, texto_antigo, texto_novo, cor_hex, estilo_fonte, x_offset=0, y_offset=0):
    try:
        r = int(cor_hex[0:2], 16) / 255
        g = int(cor_hex[2:4], 16) / 255
        b = int(cor_hex[4:6], 16) / 255
        cor_texto = (r, g, b)

        estilo = estilo_fonte.lower()
        if estilo == "negrito":
            nome_fonte = "helvB"
        elif estilo == "itálico":
            nome_fonte = "helvI"
        elif estilo in ("negritoitálico", "italico negrito", "negrito italico"):
            nome_fonte = "helvBI"
        else:
            nome_fonte = None

        documento = fitz.open(caminho_pdf)
        for num_pagina in range(len(documento)):
            pagina = documento[num_pagina]
            instancias = pagina.search_for(texto_antigo)
            for inst in instancias:
                pagina.add_redact_annot(inst, fill=(1, 1, 1))
                pagina.apply_redactions()
                x0, y0, x1, y1 = inst
                novo_x = x0 + x_offset
                novo_y = y0 + y_offset
                try:
                    if nome_fonte:
                        pagina.insert_text((novo_x, novo_y), texto_novo, fontsize=10, color=cor_texto, fontname=nome_fonte)
                    else:
                        pagina.insert_text((novo_x, novo_y), texto_novo, fontsize=10, color=cor_texto)
                except Exception as e:
                    logging.warning(f"Falha ao inserir com a fonte {nome_fonte} em {caminho_pdf}: {e}. Inserindo com fonte padrão.")
                    pagina.insert_text((novo_x, novo_y), texto_novo, fontsize=10, color=cor_texto)
        caminho_temp = caminho_pdf + ".temp"
        documento.save(caminho_temp, deflate=True, garbage=3, clean=True)
        documento.close()
        os.replace(caminho_temp, caminho_pdf)
        logging.info(f"Texto modificado com sucesso em: {caminho_pdf}")
        return True
    except Exception as e:
        logging.error(f"Erro ao modificar texto em {caminho_pdf}: {e}")
        return False
