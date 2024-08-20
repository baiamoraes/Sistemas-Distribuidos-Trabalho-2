Sistema de Transferência de Arquivos - Cliente-Servidor

Descrição

Este projeto implementa um sistema de transferência de arquivos usando a arquitetura cliente-servidor com Pyro4. O servidor permite o upload, download e listagem de arquivos, além de registrar e cancelar interesses de clientes em arquivos específicos. O cliente pode interagir com o servidor por meio de uma interface gráfica.

Arquitetura:

Servidor

- Armazenamento de Arquivos: O servidor armazena arquivos carregados e gerencia interesses registrados de clientes.
- Upload de Arquivos: Adiciona arquivos ao armazenamento e notifica clientes interessados se o arquivo estiver disponível.
- Listagem de Arquivos: Retorna a lista de arquivos disponíveis para download.
- Download de Arquivos: Permite que os clientes baixem arquivos do servidor.
- Registro de Interesse: Permite que clientes registrem interesse em arquivos que não estão disponíveis no momento.
- Notificação de Eventos: Notifica clientes quando um arquivo de interesse se torna disponível.
- Cancelamento de Interesse: Remove interesses registrados de clientes.

Cliente

- Interface Gráfica: Utiliza Tkinter para interagir com o usuário.
- Upload de Arquivos: Permite que o usuário carregue arquivos para o servidor.
- Download de Arquivos: Permite que o usuário baixe arquivos do servidor.
- Registro de Interesse: Permite que o usuário registre interesse em arquivos específicos.
- Cancelamento de Interesse: Permite que o usuário cancele o interesse registrado em arquivos.
- Notificação de Eventos: Recebe notificações quando arquivos de interesse se tornam disponíveis.

Requisitos

- Python 3.
- Pyro4: Biblioteca para comunicação remota.
- Tkinter: Biblioteca para a interface gráfica.

Execução

1. Inicie o daemon:
   pyro4-ns

2. Inicie o servidor:
   python server.py

3. Inicie o cliente:
   python client.py
