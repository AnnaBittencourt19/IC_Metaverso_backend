# Fundamentos web e arquitetura cliente-servidor
Um servidor é um programa que fica 24h escutando portas TCP/UDP

### **O paradigma cliente-servidor**
A internet utiliza o modelo arquitetural cliente-servidor. Onde o cliente é aquele que faz um requerimento/solicitação, já o servidor recebe essa solicitação, interpreta, executa o que deve ser executado e devolve as informações depois de processadas (ele aguarda a chegada das requisições)
Tem uma analogia muito boa sobre essa dinamica cliente-servidor utilizando um restaurante como exemplo: O cliente é o freguês do restaurante analisando o cardápio e decidindo o que vai pedir, a requisição é o pedido anotado e levado pra cozinha, a cozinha é o servidor que faz o prato que o cliente pediu e o prato finalizado é a resposta do servidor que é entregue ao cliente após o processamento do pedido
Existe todo um processo "debaixo dos panos" que vai do usuário digitar o DNS, esse DNS ser transformado em IP, o protocolo TCP/IP estabelecer uma rota até o servidor....

### **Protocolo HTTP**
O HTTP é o idioma da camada 7 do modelo OSI (camada de aplicação)
O HTTP é um protocolo sem estado, ou seja, cada requisição é tratada como um evento isolado, não retém memória e cada requisição é tratada de modo isolado
### **Protocolo WebSocket**
Diferenças entre HTTP e o WebSocket: O HTTP funciona como uma Walkie-Talkie onde um lado aperta o botão, fala (envia requisição), solta o botão e o outro lado processa aperta o botão e responde (não é possível que os dois lados se comuniquem ao mesmo tempo). Já o WebSocket opera como um telefone fixo, uma vez que a chamada é atendida a linha permanece aberta, ambos os lados podem falar ao mesmo tempo e se escutar e não há necessidade de discar o número a cada nova frase.

|                   | Arquitetura HTTP (REST)                                          | Arquitetura WebSocket                                                              |
| ----------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Padrão de conexão | Uma nova conexão para cada requisição e encerra após a resposta. | Uma única conexão estabelecida no início mantida viva até o encerramento explícito |
| Direcionalidade   | Unidirecional. Apenas o cliente inicia a conversa                | Bidimencional                                                                      |



