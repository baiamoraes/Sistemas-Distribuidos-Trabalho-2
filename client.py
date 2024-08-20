import Pyro4  # Biblioteca para comunicação remota em Python
import tkinter as tk  # Biblioteca para criação da interface gráfica
from tkinter import messagebox, filedialog, simpledialog  # Módulos para caixas de mensagem, diálogo de arquivos e entrada simples
import threading  # Biblioteca para manipulação de threads

@Pyro4.expose  # Expõe a classe para chamadas remotas via Pyro4
class Client(object):
    def __init__(self, master):
        
        # Inicializa o cliente, configurando a interface gráfica e registrando o cliente no servidor de nomes.
        # parâmetro master: Instância da janela principal da interface gráfica (Tk)
        
        self.master = master
        self.master.title("Cliente Pyro4")
        self.server = Pyro4.Proxy("PYRONAME:server")  # Cria um proxy para o servidor Pyro4
        self.uri = None  # Inicializa o URI como None
        
        # Cria botões na interface para realizar as operações
        self.upload_button = tk.Button(master, text="Upload", command=self.upload_file)
        self.list_button = tk.Button(master, text="Listar", command=self.list_files)
        self.download_button = tk.Button(master, text="Download", command=self.download_file)
        self.interest_button = tk.Button(master, text="Interesse", command=self.register_interest)
        self.cancel_button = tk.Button(master, text="Cancelar", command=self.cancel_interest)
        
        # Posiciona os botões na interface gráfica
        self.upload_button.pack(pady=10)
        self.list_button.pack(pady=10)
        self.download_button.pack(pady=10)
        self.interest_button.pack(pady=10)
        self.cancel_button.pack(pady=10)
        
        # Registra o cliente no servidor de nomes e obtém seu URI
        daemon = Pyro4.Daemon()  # Cria o daemon Pyro4 para gerenciar as requisições remotas
        ns = Pyro4.locateNS()  # Localiza o servidor de nomes Pyro4
        self.uri = daemon.register(self)  # Registra o objeto Client no daemon
        ns.register("client", self.uri)  # Registra o cliente com um nome no servidor de nomes
        print(f"Cliente registrado no servidor com URI: {self.uri}")
        
        # Inicia uma thread para escutar notificações sem bloquear a interface gráfica
        # Essa thread foi criada pois a interface sempre congelava quando ia notificar o cliente sobre interesses
        threading.Thread(target=daemon.requestLoop, daemon=True).start()

    def upload_file(self):
        
        # Inicia uma thread para realizar o upload de um arquivo.
        
        thread = threading.Thread(target=self._upload_file)
        thread.start()

    def _upload_file(self):
        
        # Exibe um diálogo para o usuário selecionar um arquivo e realiza o upload desse arquivo para o servidor.
        
        filename = filedialog.askopenfilename(title="Selecione o arquivo para upload", filetypes=[("Arquivos de texto", "*.txt")])
        if filename:
            try:
                with open(filename, "r") as file:
                    file_content = file.read()
                
                # Faz o upload do arquivo para o servidor
                self.server.upload_file(filename.split('/')[-1], file_content)
                messagebox.showinfo("Upload", f"Arquivo {filename.split('/')[-1]} carregado com sucesso.")
            except FileNotFoundError:
                messagebox.showerror("Erro", f"Arquivo {filename} não encontrado.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def list_files(self):
        
        # Solicita ao servidor a lista de arquivos disponíveis e exibe em uma caixa de mensagem.
        
        try:
            files = self.server.list_files()
            if files:
                messagebox.showinfo("Arquivos Disponíveis", "\n".join(files))
            else:
                messagebox.showinfo("Arquivos Disponíveis", "Nenhum arquivo disponível no servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar arquivos: {e}")

    def download_file(self):
        
        # Solicita ao usuário o nome de um arquivo para download e salva o arquivo no disco.
        
        filename = simpledialog.askstring("Download", "Digite o nome do arquivo para download:")
        if filename:
            file_content = self.server.download_file(filename)
            if file_content:
                save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=filename)
                if save_path:
                    try:
                        with open(save_path, "w") as file:
                            file.write(file_content)
                        messagebox.showinfo("Download", f"Arquivo {filename} baixado com sucesso.")
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")

    def register_interest(self):
        
        # Solicita ao usuário o nome de um arquivo e a validade do interesse e inicia uma thread para registrar o interesse.
        
        filename = simpledialog.askstring("Interesse", "Digite o nome do arquivo que deseja registrar interesse:")
        validity = simpledialog.askinteger("Interesse", "Digite a validade (em segundos) do interesse:")
        if filename and validity:
            thread = threading.Thread(target=self._register_interest, args=(filename, validity))
            thread.start()

    def _register_interest(self, filename, validity):
        
        # Registra o interesse em um arquivo e notifica o usuário sobre o sucesso ou falha do registro.
        # parâmetro filename: Nome do arquivo para o qual o interesse está sendo registrado
        # parâmetro validity: Tempo (em segundos) durante o qual o interesse é válido
        
        try:
            self.server.register_interest(self.uri, filename, validity)
            messagebox.showinfo("Interesse", f"Interesse registrado para {filename}.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar interesse: {e}")

    def cancel_interest(self):
        
        # Solicita ao usuário o nome de um arquivo para cancelar o interesse e inicia uma thread para cancelar o interesse.
        
        filename = simpledialog.askstring("Cancelar Interesse", "Digite o nome do arquivo que deseja cancelar interesse:")
        if filename:
            thread = threading.Thread(target=self._cancel_interest, args=(filename,))
            thread.start()

    def _cancel_interest(self, filename):
        
        # Cancela o interesse registrado em um arquivo e notifica o usuário sobre o sucesso ou falha do cancelamento.
        # parâmetro filename: Nome do arquivo para o qual o interesse deve ser cancelado
    
        try:
            self.server.cancel_interest(self.uri, filename)
            messagebox.showinfo("Cancelar Interesse", f"Interesse cancelado para {filename}.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar interesse: {e}")

    def notify_event(self, message):
        
        # Exibe uma notificação para o cliente quando um arquivo de interesse se torna disponível.
        # parâmetro message: Mensagem a ser exibida na notificação
        
        print(f"Notificação recebida: {message}")
        # Exibe a notificação em uma thread separada para não travar a interface gráfica
        threading.Thread(target=lambda: messagebox.showinfo("Notificação", message)).start()

def main():

    # Função principal que configura e inicia o cliente Tkinter.
    
    root = tk.Tk()
    client = Client(root)
    root.mainloop()

if __name__ == "__main__":
    main()
