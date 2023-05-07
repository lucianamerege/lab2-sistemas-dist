#com multiplexacao do processamento (atende mais de um cliente com select)
import socket
import select
import sys
import threading

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10020 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#threads ativas
clientes = []
dicionario = {}

def iniciaServidor():
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 
	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))
	# coloca-se em modo de espera por conexoes
	sock.listen(5) 
	# configura o socket para o modo nao-bloqueante
	sock.setblocking(False)
	# inclui o socket principal na lista de entradas de interesse
	entradas.append(sock)
	return sock


def atendeRequisicoes(clisock, endr):
	#recebe dados do cliente, volta a ser infinito pois está atendendo apenas a cada thread
	while True:
		data = clisock.recv(1024).decode()
		if not data: # dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			clisock.close() # encerra a conexao com o cliente
			return
		elif data.startswith('add'):
			mensagem, resultado = checaAdicao(data)
			if mensagem != "Erro":
				resposta = mensagem + ': ' + resultado
				print(str(endr) + ': ' + resposta)
				clisock.send(resposta.encode('utf-8'))
			else:
				print('Tentou adicionar de maneira errada')
				clisock.send(b'Sintaxe correta: add <palavra> <significado>')
		elif data.startswith('list'):
			retornaLista(data.split(), clisock)
		else:
			clisock.send(b'Comando inexistente. Para adicionar uma palavra, tente: add <palavra> <significado>')
	

def retornaLista(chave, clisock):
	if len(chave) != 2:
		clisock.send(b'Sintaxe correta: list <palavra>')
	else:	
		if chave[1] in dicionario:
			sorted = dicionario[chave[1]]
			sorted.sort()
			dicionario.update({chave[1]:sorted})
			clisock.send(str(dicionario[chave[1]]).encode('utf-8'))
		else:
			clisock.send(b'[]')
		

def checaAdicao(cmd):
	add = cmd.split()
	if len(add) != 3:
		return "Erro", "Erro"
	elif add[1] in dicionario:
		definicoes = dicionario[add[1]]
		definicoes.append(add[2])
		dicionario.update({add[1]:definicoes})
		return "Definição adicionada", add[2]
	else:
		definicoes = []
		definicoes.append(add[2])
		dicionario.update({add[1]:definicoes})
		return "Palavra adicionada ao dicionario" , add[1]
	

def trataEntradaPadrao(cmd, sock):
	if cmd == 'fim': #solicitacao de finalizacao do servidor
		for c in clientes:
			c.join() #bloqueia quem chamou o join esperando que a thread termine
		sock.close()
		sys.exit()
	elif cmd == 'list':
		print(dicionario)
	elif cmd.startswith('add'):
		mensagem, resultado = checaAdicao(cmd)
		if mensagem != "Erro":
			print(mensagem + ': ' + resultado)
		else:
			print('Sintaxe correta para adicionar palavras ao dicionario:\nadd <palavra> <significado>')
	elif cmd.startswith("del"):
		delete = cmd.split()
		if len(delete) != 2:
			print('Sintaxe correta para deletar palavras do dicionario:\ndel <palavra>')
			return
		elif delete[1] not in dicionario:
			print('Palavra não existe no dicionário')
		else:
			del dicionario[delete[1]]
			print(delete[1] + ' removido do dicionário')
	else:
		print('Comando inexistente')
		printComandosAdmin()


def printComandosAdmin():
	print('\n--------------------------\nSeus comandos: \n> add <palavra> <significado>\n> list\n> del <palavra>\n> fim\n--------------------------\n')


def main():
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	printComandosAdmin()
	while True:
		#espera por qualquer entrada de interesse
		leitura, escrita, excecao = select.select(entradas, [], [])
		#tratar todas as entradas prontas
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = sock.accept()
				print ('Conectado com: ', endr)
				#cria uma nova thread, diz a função q vai executar e os argumentos pra funcao
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock, endr))
				cliente.start()
				clientes.append(cliente)
			elif pronto == sys.stdin: #entrada padrao
				cmd = input()
				trataEntradaPadrao(cmd, sock)

main()