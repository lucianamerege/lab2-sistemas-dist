#com multiplexacao do processamento (atende mais de um cliente com select)
import socket
import select
import sys
import threading

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10003 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#threads ativas
clientes = []
dicionario = {}
num_linhas = 0

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

def iniciaDicionario():
	global num_linhas
	with open('dicionario.txt', 'r') as arq:
		linhas = arq.readlines()
		for i, linha in enumerate(linhas):
			if linha != '\n':
				#strip tira os espaços no começo e fim da linha
				chave, *valores = [entrada.strip() for entrada in linha.split(',')]
				valores.insert(0, i)
				dicionario[chave] = valores
			num_linhas = num_linhas + 1

	print("Dicionario preparado:")
	print(dicionario)

def atendeRequisicoes(clisock, endr):
	#recebe dados do cliente, volta a ser infinito pois está atendendo apenas a cada thread
	while True:
		data = clisock.recv(1024).decode()

		if not data: # dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			clisock.close() # encerra a conexao com o cliente
			return
		elif data.startswith('Add'):
			mensagem, resultado = checaAdicao(data)
			if mensagem != "Erro":
				resposta = mensagem + ': ' + resultado
				print(str(endr) + ': ' + resposta)
				clisock.send(resposta.encode('utf-8'))
			else:
				clisock.send(b'Sintaxe incorreta.')
		elif data.startswith('List'):
			retornaLista(data.split(), clisock)
		else:
			clisock.send(b'Comando inexistente.')

def retornaLista(chave, clisock):
	if len(chave) != 2:
		clisock.send(b'Sintaxe incorreta.')
	else:	
		if chave[1] in dicionario:
			sorted = dicionario[chave[1]]
			num = sorted[0]
			del sorted[0]
			sorted.sort()
			clisock.send(str(sorted).encode('utf-8'))
			dicionario[chave[1]].insert(0, num)
		else:
			clisock.send(b'[]')
		

def checaAdicao(cmd):
	global num_linhas
	add = cmd.split()
	if len(add) != 3:
		return "Erro", "Erro"
	elif add[1] in dicionario:
		definicoes = dicionario[add[1]]
		definicoes.append(add[2])
		dicionario.update({add[1]:definicoes})
		with open('dicionario.txt', 'r+') as arq:
			linhas = arq.readlines()
			#o primeiro valor da lista é o número da linha onde está aquela palavra
			linhas[int(definicoes[0])] = linhas[int(definicoes[0])].strip() + ', ' + add[2] + '\n'
			arq.seek(0)
			for linha in linhas:
				arq.write(linha)

		return "Definição adicionada", add[2]
	else:
		with open('dicionario.txt', 'a') as arq:
			arq.write(add[1] + ', ' + add[2] + '\n')

		definicoes = [num_linhas]
		definicoes.append(add[2])
		dicionario.update({add[1]:definicoes})
		num_linhas = num_linhas + 1

		return "Palavra adicionada ao dicionario" , add[1]
	

def trataEntradaPadrao(cmd, sock):
	if cmd == 'Fim': #solicitacao de finalizacao do servidor
		for c in clientes:
			c.join() #bloqueia quem chamou o join esperando que a thread termine
		sock.close()
		sys.exit()
	elif cmd == 'List':
		print(dicionario)
	elif cmd.startswith('Add'):
		mensagem, resultado = checaAdicao(cmd)
		if mensagem != "Erro":
			print(mensagem + ': ' + resultado)
		else:
			print('Sintaxe incorreta.')
	elif cmd.startswith("Del"):
		delete = cmd.split()
		if len(delete) != 2:
			print('Sintaxe incorreta.')
			return
		elif delete[1] not in dicionario:
			print('Palavra inexistente.')
		else:
			values = dicionario[delete[1]]
			lines = open('dicionario.txt', 'r').readlines()
			lines[values[0]] = '\n'
			arq = open('dicionario.txt', 'w')
			arq.writelines(lines)
			arq.close()
			del dicionario[delete[1]]
			print(delete[1] + ' removido do dicionário')
	else:
		print('Comando inexistente')
		printComandosAdmin()


def printComandosAdmin():
	print('\n--------------------------\nSeus comandos: \n> Add <palavra> <significado>\n> List\n> Del <palavra>\n> Fim\n--------------------------\n')


def main():
	sock = iniciaServidor()
	iniciaDicionario()
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
