- Baixa no site "silicon labs". Link: https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads
	- Tem haver com o uso do UART
	- Para instalar abrir o executável 
	- No gerenciador de dispositivos deve aparecer o silicon lab 
- Portas ESP32 (cyd):
	![[Pasted image 20260624203501.png]]
- Instalar esptools:
	- Thonny -> Ferramentas -> Gerenciar plugins... -> procurar esptools -> instalar
- Selecionar qual porta vai ser usada no thonny: 
	- Ferramentas -> opções -> Interpretador -> selecionar MicroPython(ESP32) -> selecionar a porta onde está o ESP32 -> Instalar ou atualizar o MicroPython
## O que é MicroPython?
- É uma implementação do Python para microcontroladores
- Arduino vs MicroPython:
	- No Arduino o código é escrito no computador compilado pela IDE e enviado para a memória flash do ESP32 já pronto para ser executado, já no MicroPython o código também é escrito no computador mas quem executa é um interpretador dentro do próprio ESP32
	- MicroPython é executado em tempo de execução (Não é rápido)
