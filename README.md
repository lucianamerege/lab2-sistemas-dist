# lab2-sistemas-dist

O sistema deve funcionar no modelo de camadas. O cliente usará seu socket para se conectar com o socket do servidor. O socket do servidor aceitará a conexão e criará uma thread nova para tratar das requisições daquele cliente.
À partir daí, quando o cliente mandar uma nova requisição, o socket já direcionará automaticamente para a thread dele. Lá a thread chamará a função que processa o que o cliente pediu e pegará os dados do dicionário, ou retornará um erro caso o pedido não faça sentido.
O cliente poderá solicitar a adição de uma chave (ou valor caso a chave já exista), ou a listagem de valores associados à uma chave.
Após pegar e tratar os dados do dicionário, o processamento devolverá para a thread que devolve para o socket que envia para o cliente.
Essa comunicação continuará entre cliente e servidor até o cliente digitar o comando de finalização e cortar a relação com o servidor.

Os componentes ficam distribuídos da seguinte maneira:
![image](https://user-images.githubusercontent.com/52220617/236714650-4682fb70-46dc-4cc7-8bb9-cd80a0615cef.png)

Para adicionar um valor ou chave, o cliente deve enviar o comando "add <chave> <valor>"
Para listar os valores de uma chave, ele deve enviar o comando "list <chave>"
E para encerrar a aplicação, deve digitar "fim"
  
O servidor permite comandos diretamente do sistema em que roda também.
Para adicionar um valor ou chave, o administrador deve enviar o comando "add <chave> <valor>"
Para listar todas as entradas do dicionário, ele deve enviar o comando "list"
Para apagar um valor e suas chaves, ele deve enviar o comando "del <chave>"
E para encerrar a aplicação, deve digitar "fim"
