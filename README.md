<h1 align=center>Projeto de Extensão Repetidor ESP8266</h1>

<b>Projeto de Extensão da Disciplina Aplic. de Cloud, Iot e Indústria 4.0 em Python - Leonardo Bruno de Souza Silva - 202301011744 - Arquivos da Aplicação.</b>

<b>Repositório Pricipal do Projeto Repetidor ESP8266</b>

<b>Arquivos software placa ESP8266 arquivos aplicação em Python para Gerenciar Dispositivos IoT</b>

Este repositório fornece:

* Firmware-ESP8266-1.6.2.bin: Firmware Original da Placa ESP8266.

* app.py: Aplicativo em Python para gerenciar a rede de Dispositivos IoT criada pelo repetidor.

* repetidor-esp8266.ino: Código para placa. (Cria o repetidor, fornece ambiente e cria endpoints para consumo na aplicação Python).

* requisitos_python.txt: Lista de requisitos para uso da aplicação Python.

* requisitos_sistema: Lista de requisitos do sistema operacional. 

Para criar o ambiente você vai precisar basicamente de:

* GNU Linux Debian 12.7.0
* IDE Arduino.
* Python3
* Bibliotecas: python3-serial, requests, libserialport-dev.
* Placa ESP8266 na versão 3 ( opcionais: Cabo(s) usb para alimentação, case(s) para proteção da placa).
* Git

Placas utilizadas no Projeto:   

![Placas ESP8266 e Cases](/imagens/placa-esp8266-case.jpg)   

Cases com impressão 3D utilizados para proteção das placas:   

![Cases](/imagens/esp8266-cases.jpg)  


<h2>Como rodar o projeto ?</h2>

Para instalação dos pacotes básicos 
execute no terminal:

```bash
$ sudo apt install git python3 python3-virtualenv arduino python3-serial libserialport-dev
```

Com o git instalado ou pelo navegador clone o repositório abaixo:

extensao-repetidor-esp8266 ( repositório principal do projeto )
```bash
$ git clone https://github.com/souza-lb/extensao-repetidor-esp8266
```

Dentro da pasta do repositório que você encontra:  

![Pasta repositório extensão-repetidor-esp8266-main](/imagens/arquivos-repositorio.png)  

Abra o IDE Arduino. Na aba preferências adicione a url referente à placa ESP8266 conforme abaixo:


```bash
http://arduino.esp8266.com/stable/package_esp8266com_index.json
```

![Opção Preferências](/imagens/repositorio-placa.png)  


Agora instale a biblioteca referente à sua placa conforme abaixo:


![Biblioteca Placa](/imagens/gestao-placas.png)  

Execute agora :

```bash
sudo mvn package
```

Volte para área de bibliotecas e instale a ESP-Essentials:


![ESP Essentials](/imagens/esp-essentials.png)  

Abra o arquivo "repetidor-esp8266.ino" no seu Arduino IDE e envie para a placa.

![IDE Arduino](/imagens/ide-arduino-includes.png)  

Após reiniciar a plca consulte a saída serial (Neste caso a rede wifi já está configurada).

![Saída serial](/imagens/monitor-serial.png)   

Observe no IDE Arduino os Endpoints. Eles são um elemento importante que será utilizado na nossa aplicação Python:


```bash
// Função para configurar o servidor web
void configurarServidorWeb() {
    // Define as rotas do servidor
    servidor.on("/", HTTP_GET, handleRoot);
    servidor.on("/reset-password", HTTP_GET, handleResetPassword);
    servidor.on("/confirm-reset", HTTP_POST, handleConfirmReset);
    servidor.on("/set-password", HTTP_POST, handleSetPassword);
    servidor.on("/devices", HTTP_POST, handleListDevices);
    servidor.on("/devices-json", HTTP_POST, handleListDevicesJson); // Novo endpoint
    servidor.on("/reiniciar", HTTP_POST, handleReiniciar);
}
```

![Endpoints Aplicação](/imagens/endpoints-importantes.png)   


Conecte ao ponto de acesso abra o navegador e você será redirecionado para a tela abaixo:   

![Tela inicial ponto acesso](/imagens/tela-inicial-configuracao-repetidor.png)   

Configure a rede que você deseja repetir:   

![Tela redes disponíveis](/imagens/tela-configuracao-repetidor-redes-disponiveis.png)   


Após cadastrar reinicie sua placa e conecte ao ponto de acesso "NomeRede+Repetidor", utilize a senha de rede repetida.

Abra o navegador e cadastre sua senha para uso da aplicação conforme as imagens a seguir (Apenas com a senha será possível obter dados do ponto de acesso):

![Cadastro de senha](/imagens/tela-cadastro-senha-app-consulta.png)    

A seguir você receberá a tela de confirmação de cadastro:

![Cadastro confirmado](/imagens/tela-cadastro-senha-app-confirmacao.png)  


Agora execute o aplicativo "app.py", informe a senha cadastrada no passo anterior e informe também o ip do ponto de acesso. Se não souber qual consulte a saída serial. A placa está configurada para fornecer essa informação na inicialização. 


![Tela Inicial Gerenciador](/imagens/gerenciador-repetidor-esp8266.png)  


Agora clique no botão verde "Obter dispositivos". A aplicação exibirá a lista de dispositivos conectados ao ponto de acesso. Exibirá também a potência do sinal da rede repetida. Repare que a cor do valor do sinal varia de acordo com a sua potência atual.   


![Tela Inicial Gerenciador Ativo](/imagens/gerenciador-repetidor-esp8266-ativo.png)  


Caso a placa apresente problemas você pode reinicializá-lo remotamente, foi implementado um endpoint para que mediante o fornecimento de senha o dispositivo possa ser reinicializado. Esta função é bem útil principalmnente se a placa for instalada em um local de difícil acesso. Abaixo segue tela para confirmação de reinicialização:   


![Tela Reinicialização](/imagens/confirmacao-reinicio.png)   


Processo de reinicialização em curso:   


![Tela Reinicialização em curso](/imagens/reinicio-realizado.png)




Este repositório foi criado por: <b>Leonardo Bruno de Souza Silva</b><br>
<b>Matrícula 202301011744</b><br>
<b>Projeto de Extensão Repetidor ESP8266 da Disciplina Aplic. de Cloud, Iot e Indústria 4.0 em Python</b><br>
202301011744@alunos.estacio.br<br>
<b>souzalb@proton.me</b>

