import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import os
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# Configuração do log (executada antes de qualquer chamada de logging)
logging.basicConfig(level=logging.INFO,
                    filename="pdf_modifier.log",
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    filemode="w")

# Importa as funcionalidades dos outros módulos
from mover_pdfs import operacao_apostila
from modificar_texto_pdf import modificar_texto_no_pdf
from backup import reverter_backup
#from funcoes_pdf import processar_pdf, processar_diretorio  # Se existir; caso contrário, use as funções definidas

# Classe da Interface Tkinter
class Aplicativo(tk.Tk):
    def __init__(self):
        super().__init__()
        # Configuração de DPI e escala para evitar janelas borradas no Windows 10
        self.tk.call('tk', 'scaling', 1.8)
        self.style = ttk.Style()
        self.style.theme_use("xpnative")
        self.style.configure(".", font=("Segoe UI", 10))

        self.title("Manipulador de PDFs")
        self.state('zoomed')
        try:
            self.iconbitmap(os.path.abspath("pdf_icon.ico"))
        except Exception as e:
            logging.warning(f"Não foi possível carregar o ícone personalizado: {e}")
        self.criar_menu()
        self.criar_componentes()
        self.rodando = False

    def criar_menu(self):
        menu_principal = tk.Menu(self)
        menu_ajuda = tk.Menu(menu_principal, tearoff=0)
        menu_ajuda.add_command(label="Como usar", command=lambda: messagebox.showinfo("Ajuda", "Instruções de uso..."))
        menu_ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Manipulador de PDFs - Versão X"))
        menu_principal.add_cascade(label="Ajuda", menu=menu_ajuda)
        self.config(menu=menu_principal)

    def criar_componentes(self):
        # --- Operação Apostila ---
        frame_apostila = ttk.LabelFrame(self, text="Operação Apostila")
        frame_apostila.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(frame_apostila, text="Copia os PDFs dos pacotes do Xinyu para 'Apostila' e para a subpasta 'Resumos, Slides, Mapas Mentais'.").pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_apostila = ttk.Button(frame_apostila, text="Iniciar Operação Apostila", command=self.iniciar_operacao_apostila)
        self.btn_apostila.pack(side=tk.RIGHT, padx=5, pady=5)

        # --- Seleção de Diretório ---
        frame_dir = ttk.LabelFrame(self, text="Diretório dos PDFs")
        frame_dir.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(frame_dir, text="Diretório:").pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_diretorio = ttk.Entry(frame_dir, width=50)
        self.entrada_diretorio.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        ttk.Button(frame_dir, text="Selecionar", command=self.selecionar_diretorio).pack(side=tk.LEFT, padx=5, pady=5)

        # --- Remover Texto ---
        frame_remover = ttk.LabelFrame(self, text="Remover Texto")
        frame_remover.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(frame_remover, text="Texto a remover:").pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_remover_texto = ttk.Entry(frame_remover, width=50)
        self.entrada_remover_texto.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # --- Modificar Texto ---
        frame_modificar = ttk.LabelFrame(self, text="Modificar Texto")
        frame_modificar.pack(padx=10, pady=10, fill=tk.X)
        self.var_modificar = tk.BooleanVar()
        ttk.Checkbutton(frame_modificar, text="Modificar Texto", variable=self.var_modificar, command=self.habilitar_campos_modificacao).pack(anchor=tk.W, padx=5, pady=5)
        self.rotulo_texto_antigo = ttk.Label(frame_modificar, text="Texto antigo:", state=tk.DISABLED)
        self.rotulo_texto_antigo.pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_texto_antigo = ttk.Entry(frame_modificar, width=30, state=tk.DISABLED)
        self.entrada_texto_antigo.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.rotulo_texto_novo = ttk.Label(frame_modificar, text="Texto novo:", state=tk.DISABLED)
        self.rotulo_texto_novo.pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_texto_novo = ttk.Entry(frame_modificar, width=30, state=tk.DISABLED)
        self.entrada_texto_novo.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.rotulo_cor = ttk.Label(frame_modificar, text="Cor (hex):", state=tk.DISABLED)
        self.rotulo_cor.pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_cor = ttk.Entry(frame_modificar, width=10, state=tk.DISABLED)
        self.entrada_cor.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_cor = ttk.Button(frame_modificar, text="Escolher Cor", command=self.escolher_cor, state=tk.DISABLED)
        self.btn_cor.pack(side=tk.LEFT, padx=5, pady=5)
        self.rotulo_estilo = ttk.Label(frame_modificar, text="Estilo da Fonte:", state=tk.DISABLED)
        self.rotulo_estilo.pack(side=tk.LEFT, padx=5, pady=5)
        self.estilos_fonte = ["normal", "negrito", "itálico", "negritoitálico"]
        self.combobox_estilo = ttk.Combobox(frame_modificar, values=self.estilos_fonte, state=tk.DISABLED)
        self.combobox_estilo.set("normal")
        self.combobox_estilo.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Remover Páginas ---
        frame_paginas = ttk.LabelFrame(self, text="Remover Páginas do Início")
        frame_paginas.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(frame_paginas, text="Número de páginas:").pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_paginas = ttk.Entry(frame_paginas, width=10)
        self.entrada_paginas.insert(0, "0")
        self.entrada_paginas.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Adicionar PDF ---
        frame_pdf = ttk.LabelFrame(self, text="Adicionar PDF ao Início")
        frame_pdf.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(frame_pdf, text="Arquivo PDF:").pack(side=tk.LEFT, padx=5, pady=5)
        self.entrada_pdf_adicionar = ttk.Entry(frame_pdf, width=40)
        self.entrada_pdf_adicionar.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        ttk.Button(frame_pdf, text="Selecionar PDF", command=self.selecionar_pdf_adicionar).pack(side=tk.LEFT, padx=5, pady=5)

        # --- Botões de Ação ---
        frame_acoes = ttk.Frame(self)
        frame_acoes.pack(pady=10)
        self.btn_processar = ttk.Button(frame_acoes, text="Iniciar Processamento", command=self.iniciar_processamento)
        self.btn_processar.pack(side=tk.LEFT, padx=10)
        self.btn_reverter = ttk.Button(frame_acoes, text="Reverter Backup", command=self.iniciar_reversao)
        self.btn_reverter.pack(side=tk.LEFT, padx=10)

        # --- Barra de Progresso e Log ---
        frame_progresso = ttk.LabelFrame(self, text="Progresso")
        frame_progresso.pack(padx=10, pady=10, fill=tk.X)
        self.barra_progresso = ttk.Progressbar(frame_progresso, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.barra_progresso.pack(padx=5, pady=5, fill=tk.X, expand=True)
        self.rotulo_progresso = ttk.Label(frame_progresso, text="Aguardando...")
        self.rotulo_progresso.pack(padx=5, pady=5, fill=tk.X)
        frame_log = ttk.LabelFrame(self, text="Log de Execução")
        frame_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.texto_log = tk.Text(frame_log, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(frame_log, command=self.texto_log.yview)
        self.texto_log.configure(yscrollcommand=scrollbar.set)
        self.texto_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def selecionar_diretorio(self):
        diretorio = filedialog.askdirectory()
        if diretorio:
            self.entrada_diretorio.delete(0, tk.END)
            self.entrada_diretorio.insert(0, diretorio)

    def selecionar_pdf_adicionar(self):
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if arquivo:
            self.entrada_pdf_adicionar.delete(0, tk.END)
            self.entrada_pdf_adicionar.insert(0, arquivo)

    def escolher_cor(self):
        cor = filedialog.askcolor(title="Escolher cor do texto")[1]
        if cor:
            self.entrada_cor.delete(0, tk.END)
            self.entrada_cor.insert(0, cor.lstrip("#"))

    def habilitar_campos_modificacao(self):
        if self.var_modificar.get():
            self.rotulo_texto_antigo.config(state=tk.NORMAL)
            self.entrada_texto_antigo.config(state=tk.NORMAL)
            self.rotulo_texto_novo.config(state=tk.NORMAL)
            self.entrada_texto_novo.config(state=tk.NORMAL)
            self.rotulo_cor.config(state=tk.NORMAL)
            self.entrada_cor.config(state=tk.NORMAL)
            self.btn_cor.config(state=tk.NORMAL)
            self.rotulo_estilo.config(state=tk.NORMAL)
            self.combobox_estilo.config(state=tk.NORMAL)
        else:
            self.rotulo_texto_antigo.config(state=tk.DISABLED)
            self.entrada_texto_antigo.config(state=tk.DISABLED)
            self.rotulo_texto_novo.config(state=tk.DISABLED)
            self.entrada_texto_novo.config(state=tk.DISABLED)
            self.rotulo_cor.config(state=tk.DISABLED)
            self.entrada_cor.config(state=tk.DISABLED)
            self.btn_cor.config(state=tk.DISABLED)
            self.rotulo_estilo.config(state=tk.DISABLED)
            self.combobox_estilo.config(state=tk.DISABLED)

    def iniciar_operacao_apostila(self):
        diretorio = self.entrada_diretorio.get()
        if not diretorio:
            messagebox.showerror("Erro", "Selecione um diretório!")
            return
        self.btn_apostila.config(state=tk.DISABLED)
        self.btn_processar.config(state=tk.DISABLED)
        self.btn_reverter.config(state=tk.DISABLED)
        self.adicionar_log("Iniciando Operação Apostila...")
        thread = threading.Thread(target=self.executar_apostila, args=(diretorio,), daemon=True)
        thread.start()

    def executar_apostila(self, diretorio):
        try:
            from mover_pdfs import operacao_apostila
            operacao_apostila(diretorio, self.barra_progresso, self.rotulo_progresso, log_callback=self.adicionar_log)
            self.adicionar_log("Operação Apostila concluída!")
        except Exception as e:
            self.adicionar_log(f"Erro na Operação Apostila: {e}")
        finally:
            self.btn_apostila.config(state=tk.NORMAL)
            self.btn_processar.config(state=tk.NORMAL)
            self.btn_reverter.config(state=tk.NORMAL)
            messagebox.showinfo("Concluído", "Operação Apostila finalizada!")

    def iniciar_processamento(self):
        diretorio = self.entrada_diretorio.get()
        if not diretorio:
            messagebox.showerror("Erro", "Selecione um diretório!")
            return
        remover = self.entrada_remover_texto.get().strip()
        modificar = None
        texto_antigo = self.entrada_texto_antigo.get().strip()
        texto_novo = self.entrada_texto_novo.get().strip()
        cor_hex = self.entrada_cor.get().strip()
        estilo_fonte = self.combobox_estilo.get().strip()
        if texto_antigo and texto_novo and cor_hex and estilo_fonte:
            modificar = [tk.StringVar(value=texto_antigo), tk.StringVar(value=texto_novo),
                         tk.StringVar(value=cor_hex), tk.StringVar(value=estilo_fonte)]
        elif texto_antigo or texto_novo or cor_hex or estilo_fonte:
            messagebox.showwarning("Aviso", "Para modificar o texto, preencha todos os campos.")
            modificar = None
        paginas = self.entrada_paginas.get().strip()
        if not paginas.isdigit():
            paginas = "0"
        pdf_adicionar = self.entrada_pdf_adicionar.get().strip()
        self.btn_processar.config(state=tk.DISABLED)
        self.btn_reverter.config(state=tk.DISABLED)
        self.adicionar_log("Iniciando processamento dos PDFs...")
        thread = threading.Thread(target=self.executar_processamento,
                                  args=(diretorio, tk.StringVar(value=remover), modificar,
                                        tk.StringVar(value=paginas), pdf_adicionar,
                                        self.barra_progresso, self.rotulo_progresso), daemon=True)
        thread.start()

    def executar_processamento(self, diretorio, remover_texto, modificar_texto_args, paginas_para_remover, pdf_adicionar, barra_progresso, rotulo_progresso):
        try:
            from funcoes_pdf import processar_diretorio
            processar_diretorio(diretorio, remover_texto, modificar_texto_args, paginas_para_remover, pdf_adicionar, barra_progresso, rotulo_progresso)
            self.adicionar_log("Processamento dos PDFs concluído!")
        except Exception as e:
            self.adicionar_log(f"Erro durante o processamento: {e}")
        finally:
            self.btn_processar.config(state=tk.NORMAL)
            self.btn_reverter.config(state=tk.NORMAL)
            messagebox.showinfo("Concluído", "Operação finalizada!")

    def iniciar_reversao(self):
        diretorio = self.entrada_diretorio.get().strip()
        if not diretorio:
            messagebox.showerror("Erro", "Selecione um diretório!")
            return
        self.btn_processar.config(state=tk.DISABLED)
        self.btn_reverter.config(state=tk.DISABLED)
        self.adicionar_log("Iniciando reversão dos backups...")
        thread = threading.Thread(target=self.executar_reversao, args=(diretorio,), daemon=True)
        thread.start()

    def executar_reversao(self, diretorio):
        try:
            from backup import reverter_backup
            reverter_backup(diretorio, barra_progresso=self.barra_progresso, rotulo_progresso=self.rotulo_progresso)
            self.adicionar_log("Reversão dos backups concluída!")
        except Exception as e:
            self.adicionar_log(f"Erro durante a reversão: {e}")
        finally:
            self.btn_processar.config(state=tk.NORMAL)
            self.btn_reverter.config(state=tk.NORMAL)
            messagebox.showinfo("Concluído", "Reversão finalizada!")

    def adicionar_log(self, mensagem):
        self.texto_log.config(state=tk.NORMAL)
        self.texto_log.insert(tk.END, mensagem + "\n")
        self.texto_log.see(tk.END)
        self.texto_log.config(state=tk.DISABLED)

def main():
    app = Aplicativo()
    app.mainloop()

if __name__ == "__main__":
    main()
