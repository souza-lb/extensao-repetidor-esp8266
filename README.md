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

Sistema Operacional Utilizado:  GNU/Linux Debian 12.7.0  


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

Copie o arquivo "extensao-buscado-1.0.0-jar-with-dependencies.jar" para uma pasta de sua preferência.  

Para iniciar o programa execute no terminal:  

```bash
java -jar extensao-buscado-1.0.0-jar-with-dependencies.jar
```

Se o software iniciar dentro de alguns instantes você receberá uma janela de notificação conforme abaixo:  

![Janela alerta](/imagens/janela-alerta-app.png)  

Se você clicar no botão "Abrir PDF" você receberá uma janela conforme abaixo:  

![Janela arquivo PDF](/imagens/janela-arquivo-pdf-do.png)  

O software utilizará o seu visualizador de arquivos "PDF" padrão.

Em alguns instantes você receberá sua notificação por Telegram conforme abaixo:  

![Notificação Telegram](/imagens/notificacao-telegram.png)


Em seguinda você receberá sua notificação por E-Mail conforme abaixo:  

![Notificação E-Mail](/imagens/notificacao-email.png)  


<h2>Como rodar o projeto utilizando o Docker ?</h2>  

Com a vantagem de não necessitar de alterações significativas no sistema host.<p>
A imagem utilizada no contêiner docker encapsula todas as dependências da aplicação.  


Realize as etapas anteriores incluindo o passo para gerar o arquivo "jar"

Agora acesse a pasta do segundo repositório que você clonou (extensao-buscado-docker)

Copie o seu "fat jar" para a pasta conforme abaixo:  

![Pasta repositório extensão-buscado-docker-main](/imagens/pasta-extensao-buscado-docker-main.png)  

Abra um terminal na pasta raiz do repositorio que você clonou e adicionou o arquivo "jar".

Dê a permissão para que o conteiner tenha acesso aos recursos gráficos do X11 ( Para Windows consulte a ajudo do seu sistema ):

```bash
$ xhost +local:docker
```

Para criar a imagem docker execute neste terminal:  

```bash
$ sudo docker-compose build
```

Você terá uma saída como abaixo:  

![Saída comando docker-compose build](/imagens/docker-compose-build.png)  

Isso vai damorar um pouco na primera vez pois vai baixar a imagem para o repositório local.

Agora execute no terminal:

```bash
$ sudo docker-compose up
```
Você também pode rodar o comando acima com o parâmetro -d como resultado seu terminal fica livre:

```bash
$ sudo docker-compose up -d
```

Você receberá uma saída conforme abaixo:  

![Saída comando docker-compose up](/imagens/docker-compose-up.png)  

Neste ponto seu sóftware já está rodando. Em alguns segundo a janela de notificação abrirá.

Ao final do uso remova a permissão concedida anteriormene com:

```bash
$ xhost -local:docker
```

<h2>Como rodar o projeto usando o IDE Eclipse ?</h2>

Utilize a opção para importar um projeto existente maven conforme abaixo:  

![Janela inicial inportação Maven Eclipse](/imagens/eclipse-projeto-maven-existente.png)  

Avançe para a próxima tela conforme abaixo:  

![Janela Maven Eclipse POM](/imagens/eclipse-projeto-maven-existente-pom.png)  

Rode a classe principal "Main.java"  

Esta classe concentra as principais funções da aplicação. Nela você define os horários de agendamento e serviços de notificação que você deseja utilizar.  

![Eclipse classe Main](/imagens/classe-main-eclipse.png)  

Seu programa já está funcionando:  

![Janela Eclipse rodando](/imagens/classe-main-eclipse-rodando.png)  

<h2>Solução de Problemas</h2>  

A aplicação utiliza um sistema de log para facilitar a solução de problemas. Consulte a pasta  
"log" na raiz do projeto. Verifique o arquivo de "buscado.log" nos techos que apresentarem a ocorrência  
"ERRO". Ao lado da ocorrência será fornecida uma descrição do erro apresentado.  

<h3>Erros Frequentes</h3>

* Erro biblioteca DotEnv. (Solução: Certifique que o arquivo ".env" está na pasta "/src/main/env/" e está corretamente editado).
* Erro ao rodar "mvn package". (Solução: Certifique que possui instalado o Apache Maven com "$ sudo apt install maven").
* Java não localizado. (Solução: Cetifique que possui o OpenJDK 17 ou superior instalado com "$ sudo apt install openjdk-17-jdk").



Este repositório foi criado por: <b>Leonardo Bruno de Souza Silva</b><br>
<b>Matrícula 202301011744</b><br>
<b>Projeto de Extensão BuscaDO da Disciplina Java Orientado à Objeto</b><br>
202301011744@alunos.estacio.br<br>
<b>souzalb@proton.me</b>

