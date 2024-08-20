import Pyro4  # Biblioteca para comunicação remota em Python
import threading  # Biblioteca para manipulação de threads
import time  # Biblioteca para manipulação de tempo

@Pyro4.expose  # Decorador que expõe a classe para chamadas remotas via Pyro4
class Server(object):
    def __init__(self):
        # Inicializa dicionários para armazenar arquivos e interesses
        self.files = {}  # Armazena os arquivos carregados, onde a chave é o nome do arquivo e o valor é o conteúdo
        self.interests = {}  # Armazena os interesses dos clientes, onde a chave é o nome do arquivo e o valor é uma tupla (URI do cliente, expiração)

    def upload_file(self, filename, file_content):
        
        # Faz o upload de um arquivo para o servidor.
        # Adiciona o arquivo ao armazenamento e verifica se há clientes interessados nesse arquivo.
        
        # parâmetro filename: Nome do arquivo a ser carregado
        # parâmetro file_content: Conteúdo do arquivo
        
        # Armazena o conteúdo do arquivo no dicionário de arquivos
        self.files[filename] = file_content
        print(f"Arquivo {filename} carregado com sucesso.")
        # Verifica se há clientes com interesse registrado nesse arquivo e notifica
        self.check_interests(filename)
    
    def list_files(self):
        
        # Lista todos os arquivos disponíveis no servidor.
        
        # return: Lista com os nomes dos arquivos disponíveis
        
        return list(self.files.keys())

    def download_file(self, filename):
        
        # Faz o download de um arquivo disponível no servidor.
        
        # parâmetro filename: Nome do arquivo a ser baixado
        # return: Conteúdo do arquivo se estiver disponível, caso contrário, None
        
        return self.files.get(filename)

    def register_interest(self, client_uri, filename, validity):
       
        # Registra o interesse de um cliente em um arquivo específico.
        # O interesse tem um período de validade, após o qual é removido automaticamente.
        
        # parâmetro client_uri: URI do cliente que está registrando o interesse
        # parâmetro filename: Nome do arquivo no qual o cliente está interessado
        # parâmetro validity: Tempo (em segundos) durante o qual o interesse é válido
        
        # Calcula o tempo de expiração com base na validade fornecida
        expiry = time.time() + validity
        # Armazena o interesse no dicionário de interesses
        self.interests[filename] = (client_uri, expiry)
        print(f"Interesse registrado para {filename}.")
        
        # Se o arquivo já estiver disponível, notifica o cliente imediatamente
        if filename in self.files:
            threading.Thread(target=self.notify_event, args=(filename,)).start()

    def cancel_interest(self, client_uri, filename):
        
        # Cancela o interesse registrado de um cliente em um arquivo.
        # parâmetro client_uri: URI do cliente cujo interesse deve ser cancelado
        # parâmetro filename: Nome do arquivo para o qual o interesse deve ser cancelado
        
        
        # Remove o interesse registrado para o arquivo especificado, se existir
        if filename in self.interests:
            del self.interests[filename]
            print(f"Interesse cancelado para {filename}.")
    
    def notify_event(self, filename):
        
        #Notifica o cliente sobre a disponibilidade do arquivo em que ele está interessado.
        #parâmetro filename: Nome do arquivo que está disponível
        

        # Verifica se há um interesse registrado para o arquivo
        if filename in self.interests:
            client_uri, expiry = self.interests[filename]
            # Verifica se o interesse ainda é válido
            if time.time() < expiry:
                try:
                    # Envia a notificação para o cliente interessado
                    Pyro4.Proxy(client_uri).notify_event(f"O arquivo interessado '{filename}' está disponível!")
                    print(f"Notificação enviada para o arquivo {filename}.")
                except Exception as e:
                    print(f"Erro ao notificar cliente: {e}")
            # Remove o interesse após a notificação
            del self.interests[filename]

    def check_interests(self, filename):
        
        # Verifica se há clientes interessados em um arquivo que está sendo carregado.
        # Se houver interesse registrado, notifica os clientes.
        # parâmetro filename: Nome do arquivo que foi carregado
        
        
        # Se o arquivo tem interesse registrado, notifica os clientes
        if filename in self.interests:
            threading.Thread(target=self.notify_event, args=(filename,)).start()

def main():
    
    # Função principal que configura e inicia o servidor Pyro4.
    
    # Cria o daemon Pyro4 para gerenciar as requisições remotas
    daemon = Pyro4.Daemon()
    # Localiza o servidor de nomes Pyro4
    ns = Pyro4.locateNS()
    # Registra o objeto Server no daemon
    uri = daemon.register(Server())
    # Registra o servidor de nomes com um nome
    ns.register("server", uri)
    print(f"Servidor registrado no servidor de nomes com URI: {uri}")
    # Inicia o loop de requisições do daemon
    daemon.requestLoop()

if __name__ == "__main__":
    main()
