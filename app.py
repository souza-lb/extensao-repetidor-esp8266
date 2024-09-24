import tkinter as tk  # Importa a biblioteca tkinter para criação de interfaces gráficas
from tkinter import messagebox, scrolledtext  # Importa componentes adicionais do tkinter
import requests  # Importa a biblioteca requests para fazer requisições HTTP
import json  # Importa a biblioteca json para manipulação de dados JSON
import sqlite3  # Importa a biblioteca sqlite3 para manipulação de banco de dados SQLite
import threading  # Importa a biblioteca threading para execução de código em paralelo

class App:
    def __init__(self, master):
        """Inicializa a aplicação e configura a interface."""
        self.master = master  # Armazena a referência à janela principal
        master.title("Repetidor ESP8266")  # Define o título da janela
        master.geometry("400x400")  # Define o tamanho da janela
        master.configure(bg="#f0f0f0")  # Define a cor de fundo da janela

        self.thread = None  # Inicializa a variável para controle de threads
        self.app_fechando = False  # Flag para indicar que a aplicação está fechando

        self.criar_interface()  # Chama método para criar a interface gráfica
        self.conectar_banco()  # Chama método para conectar ao banco de dados
        self.carregar_configuracoes()  # Carrega configurações salvas do banco de dados

    def criar_interface(self):
        """Cria os elementos da interface do usuário."""
        frame = tk.Frame(self.master, bg="#f0f0f0")  # Cria um frame para organizar os widgets
        frame.pack(pady=20)  # Adiciona o frame à janela com espaçamento vertical

        # Labels e entradas para IP e senha
        self.label_ip = self.criar_label(frame, "IP do Repetidor:", 0)  # Label para IP
        self.entry_ip = self.criar_entry(frame, 0)  # Campo de entrada para IP

        self.label_senha = self.criar_label(frame, "Senha:", 1)  # Label para senha
        self.entry_senha = self.criar_entry(frame, 1, show="*")  # Campo de entrada para senha (oculta)

        # Botões para obter dispositivos e reiniciar o repetidor
        botao_width = 15  # Definindo a largura dos botões
        self.criar_botao(self.master, "Obter Dispositivos", self.obter_dispositivos, "#4CAF50", botao_width)  # Botão para obter dispositivos
        self.criar_botao(self.master, "Reiniciar Repetidor", self.confirmar_reinicio, "red", botao_width)  # Botão para reiniciar o repetidor

        # Área de texto para exibição de dados
        self.text_area = self.criar_text_area(self.master)  # Cria área de texto para exibir informações

        # Configuração de cores para a exibição de dados
        self.configurar_cores_text_area()  # Configura cores para a área de texto

        # Protocolo de fechamento da janela
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)  # Define o comportamento ao fechar a janela

    def criar_label(self, parent, texto, linha):
        """Cria um label e o adiciona ao layout."""
        label = tk.Label(parent, text=texto, bg="#f0f0f0", font=("Arial", 10))  # Cria um label com texto e estilo
        label.grid(row=linha, column=0, padx=5, pady=5)  # Adiciona o label à grade
        return label

    def criar_entry(self, parent, linha, show=None):
        """Cria um campo de entrada e o adiciona ao layout."""
        entry = tk.Entry(parent, show=show, font=("Arial", 10), width=25)  # Cria um campo de entrada
        entry.grid(row=linha, column=1, padx=5, pady=5)  # Adiciona o campo à grade
        return entry

    def criar_botao(self, parent, texto, comando, cor, largura=10):
        """Cria um botão e o adiciona ao layout com largura especificada."""
        botao = tk.Button(parent, text=texto, command=comando, bg=cor, fg="white", font=("Arial", 10), padx=10, width=largura)  # Cria um botão
        botao.pack(pady=10)  # Adiciona o botão à janela com espaçamento vertical
        return botao

    def criar_text_area(self, parent):
        """Cria uma área de texto para exibição de informações."""
        text_area = scrolledtext.ScrolledText(parent, height=20, width=50, wrap=tk.WORD, font=("Arial", 10))  # Cria uma área de texto com barra de rolagem
        text_area.pack(pady=10)  # Adiciona a área de texto à janela
        text_area.configure(bg="#ffffff", fg="#000000")  # Configura cores de fundo e texto
        return text_area

    def configurar_cores_text_area(self):
        """Configura as cores para a exibição de dados na área de texto."""
        self.text_area.tag_configure("verde", foreground="green")  # Configura tag para texto verde
        self.text_area.tag_configure("amarelo", foreground="yellow")  # Configura tag para texto amarelo
        self.text_area.tag_configure("vermelho", foreground="red")  # Configura tag para texto vermelho

    def conectar_banco(self):
        """Conecta ao banco de dados SQLite e cria a tabela se não existir."""
        self.conn = sqlite3.connect('config.db')  # Conecta ao banco de dados (ou cria se não existir)
        self.cursor = self.conn.cursor()  # Cria um cursor para executar comandos no banco
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                ip TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')  # Cria tabela para armazenar configurações se não existir
        self.conn.commit()  # Salva as alterações no banco de dados

    def carregar_configuracoes(self):
        """Carrega as configurações do banco de dados e preenche os campos de entrada."""
        self.cursor.execute('SELECT ip, senha FROM configuracoes ORDER BY id DESC LIMIT 1')  # Busca a última configuração
        resultado = self.cursor.fetchone()  # Obtém o resultado da consulta
        if resultado:  # Se houver resultado
            self.entry_ip.insert(0, resultado[0])  # Preenche o campo de IP
            self.entry_senha.insert(0, resultado[1])  # Preenche o campo de senha

    def salvar_configuracoes(self, ip, senha):
        """Salva as configurações (IP e senha) no banco de dados."""
        self.cursor.execute('DELETE FROM configuracoes')  # Remove configurações antigas
        self.cursor.execute('INSERT INTO configuracoes (ip, senha) VALUES (?, ?)', (ip, senha))  # Insere novas configurações
        self.conn.commit()  # Salva as alterações no banco de dados

    def obter_dispositivos(self):
        """Obtém a lista de dispositivos conectados ao repetidor."""
        ip = self.entry_ip.get()  # Obtém o IP do campo de entrada
        senha = self.entry_senha.get()  # Obtém a senha do campo de entrada

        if not ip or not senha:  # Verifica se os campos estão preenchidos
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")  # Exibe mensagem de erro
            return

        try:
            # Realiza a requisição ao servidor com timeout de 10 segundos
            response = requests.post(f"http://{ip}/devices-json", data={'password': senha}, timeout=10)  # Faz requisição POST para obter dispositivos
            if response.status_code == 200:  # Se a requisição for bem-sucedida
                dados = json.loads(response.text)  # Converte a resposta JSON em um dicionário
                self.exibir_dados(dados)  # Exibe os dados na interface
                self.salvar_configuracoes(ip, senha)  # Salva as configurações
            else:
                self.mostrar_erro_requisicao("Senha inválida. Tente novamente.")  # Exibe mensagem de erro
        except Exception as e:
            self.mostrar_erro_requisicao(str(e))  # Exibe erro ocorrido durante a requisição

    def exibir_dados(self, dados):
        """Exibe os dados recebidos na área de texto."""
        self.text_area.delete(1.0, tk.END)  # Limpa a área de texto
        self.text_area.insert(tk.END, f"Rede Repetida: {dados['repeated_ssid']}\n")  # Exibe SSID repetido

        # Define a cor com base na potência do sinal
        potencia_sinal = dados["signal_strength"]  # Obtém a potência do sinal
        cor = self.definir_cor_sinal(potencia_sinal)  # Define a cor correspondente
        self.text_area.insert(tk.END, "Potência do Sinal: ", cor)  # Exibe a potência do sinal com a cor
        self.text_area.insert(tk.END, f"{potencia_sinal} dBm\n", cor)  # Exibe o valor da potência do sinal

        # Exibe total de dispositivos
        self.text_area.insert(tk.END, f"Total de Dispositivos: {dados['total_devices']}\n")  # Exibe total de dispositivos
        self.text_area.insert(tk.END, "\nDispositivos Conectados:\n")  # Título para lista de dispositivos conectados

        # Lista dispositivos conectados
        for dispositivo in dados["devices"]:  # Itera sobre cada dispositivo
            self.text_area.insert(tk.END, f"MAC: {dispositivo['mac']} - IP: {dispositivo['ip']}\n")  # Exibe MAC e IP do dispositivo
            self.text_area.insert(tk.END, "-" * 80 + "\n")  # Exibe uma linha de separação

    def definir_cor_sinal(self, potencia_sinal):
        """Define a cor da potência do sinal."""
        if potencia_sinal >= -50:  # Se a potência do sinal for boa
            return "verde"  # Retorna cor verde
        elif -70 <= potencia_sinal < -50:  # Se a potência do sinal for média
            return "amarelo"  # Retorna cor amarela
        return "vermelho"  # Caso contrário, retorna cor vermelha

    def confirmar_reinicio(self):
        """Cria uma janela de confirmação para reiniciar o repetidor."""
        confirm_window = tk.Toplevel(self.master)  # Cria uma nova janela
        confirm_window.title("Confirmação de Reinício")  # Define o título da nova janela
        confirm_window.geometry("300x200")  # Define o tamanho da nova janela

        label = tk.Label(confirm_window, text="Por favor, insira a senha para reiniciar:", font=("Arial", 10))  # Cria um label
        label.pack(pady=10)  # Adiciona o label à nova janela

        entry_confirmacao = tk.Entry(confirm_window, show="*", font=("Arial", 10), width=25)  # Campo para entrada da senha
        entry_confirmacao.pack(pady=5)  # Adiciona o campo à nova janela

        # Tamanho fixo para os botões
        botao_width = 15
        
        # Botões de confirmação e cancelamento
        self.criar_botao(confirm_window, "Confirmar", lambda: self.reiniciar(entry_confirmacao, confirm_window), "#4CAF50", botao_width)  # Botão de confirmar reinício
        self.criar_botao(confirm_window, "Cancelar", confirm_window.destroy, "red", botao_width)  # Botão de cancelar reinício

    def reiniciar(self, entry_confirmacao, confirm_window):
        """Reinicia o repetidor se a senha estiver correta."""
        if entry_confirmacao.get() == self.entry_senha.get():  # Verifica se a senha está correta
            self.thread = threading.Thread(target=self.reiniciar_repetidor)  # Cria uma nova thread para reiniciar o repetidor
            self.thread.start()  # Inicia a thread
            confirm_window.destroy()  # Fecha a janela de confirmação
        else:
            self.mostrar_erro("Senha incorreta. Reinício cancelado.")  # Exibe mensagem de erro

    def mostrar_erro(self, mensagem):
        """Exibe uma mensagem de erro em uma nova janela."""
        erro_window = tk.Toplevel(self.master)  # Cria uma nova janela para erro
        erro_window.title("Erro")  # Define o título da nova janela
        erro_window.geometry("300x200")  # Define o tamanho da nova janela
        erro_window.configure(bg="#f0f0f0")  # Define a cor de fundo da nova janela

        # Área de texto para exibição da mensagem de erro
        text_area = scrolledtext.ScrolledText(erro_window, height=5, wrap=tk.WORD, font=("Arial", 10))  # Cria área de texto para erro
        text_area.pack(pady=20)  # Adiciona à nova janela
        text_area.insert(tk.END, mensagem)  # Insere a mensagem de erro
        text_area.configure(bg="#ffffff", fg="black")  # Configura cores da área de texto
        text_area.config(state=tk.DISABLED)  # Desabilita a edição da área de texto

        # Botão de fechar
        self.criar_botao(erro_window, "Fechar", erro_window.destroy, "#4CAF50", 10)  # Botão para fechar a janela de erro

    def mostrar_erro_requisicao(self, mensagem):
        """Exibe uma janela de erro para requisições."""
        self.mostrar_erro(mensagem)  # Chama método para mostrar erro

    def reiniciar_repetidor(self):
        """Reinicia o repetidor e aguarda a atualização da lista de dispositivos."""
        ip = self.entry_ip.get()  # Obtém o IP do campo de entrada
        senha = self.entry_senha.get()  # Obtém a senha do campo de entrada

        if not ip or not senha:  # Verifica se os campos estão preenchidos
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")  # Exibe mensagem de erro
            return

        self.text_area.delete(1.0, tk.END)  # Limpa a área de texto
        self.text_area.insert(tk.END, "Reiniciando o repetidor, aguarde 15 segundos...\n")  # Informa que o repetidor está reiniciando
        self.master.update()  # Atualiza a interface

        try:
            # Realiza a requisição para reiniciar com timeout de 10 segundos
            response = requests.post(f"http://{ip}/reiniciar", data={'password': senha}, timeout=10)  # Faz requisição para reiniciar o repetidor
            if response.status_code == 200:  # Se a requisição for bem-sucedida
                # Aguarda 15 segundos antes de atualizar a lista
                self.master.after(15000, self.atualizar_lista_dispositivos)  # Agenda atualização da lista de dispositivos
            else:
                self.mostrar_erro_requisicao("Senha inválida ou falha ao reiniciar.")  # Exibe mensagem de erro
        except Exception as e:
            self.mostrar_erro_requisicao(str(e))  # Exibe erro ocorrido durante a requisição

    def atualizar_lista_dispositivos(self):
        """Atualiza a lista de dispositivos após reiniciar o repetidor."""
        self.text_area.insert(tk.END, "Atualizando lista de dispositivos...\n")  # Informa que a lista está sendo atualizada
        self.master.update()  # Atualiza a interface
        self.obter_dispositivos()  # Chama a função para obter dispositivos

    def on_closing(self):
        """Finaliza a aplicação e fecha a conexão com o banco de dados."""
        self.app_fechando = True  # Indica que a aplicação está fechando
        if self.thread and self.thread.is_alive():  # Se a thread de reinício estiver ativa
            self.thread.join(timeout=1)  # Aguarda a thread finalizar
        if hasattr(self, 'conn') and self.conn:  # Se a conexão com o banco de dados existir
            self.conn.close()  # Fecha a conexão com o banco de dados
        self.master.destroy()  # Fecha a janela principal

if __name__ == "__main__":
    # Inicializa a aplicação
    root = tk.Tk()  # Cria a janela principal
    app = App(root)  # Cria uma instância da aplicação
    root.mainloop()  # Inicia o loop principal da interface
