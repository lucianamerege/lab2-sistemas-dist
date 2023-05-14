#servidor de echo: lado cliente
import socket

HOST = 'localhost' # maquina onde esta o servidor
PORT = 10020       # porta que o servidor esta escutando

def iniciaCliente():
	# cria socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet (IPv4 + TCP) 

	# conecta-se com o servidor
	sock.connect((HOST, PORT)) 

	return sock

def fazRequisicoes(sock):
	# le as mensagens do usuario ate ele digitar 'fim'
	while True: 
		msg = input("\nO que deseja fazer?\nOpções:\n > Adicionar palavra/significado: Digite 'Add <palavra> <significado>'\n > Listar significados: Digite 'List <palavra>'\n > Fechar conexão: Digite 'Fim'\n\n")
		if msg == 'Fim': break 

		# envia a mensagem do usuario para o servidor
		sock.send(msg.encode('utf-8'))

		#espera a resposta do servidor
		msg = sock.recv(1024) 

		# imprime a mensagem recebida
		print(str(msg, encoding='utf-8'))

	# encerra a conexao
	sock.close()

def main():
	#inicia o cliente
	sock = iniciaCliente()
	#interage com o servidor ate encerrar
	fazRequisicoes(sock)

main()