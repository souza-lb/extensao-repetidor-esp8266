// Inclui a biblioteca para funcionalidades do ESP8266 com Wi-Fi
#include <ESP8266WiFi.h>
// Inclui a biblioteca para criação de um servidor web
#include <ESP8266WebServer.h>
// Inclui a biblioteca para gerenciar a configuração do Wi-Fi
#include <WiFiManager.h>
// Inclui a biblioteca para manipulação de NAT
#include <lwip/napt.h>
// Inclui a biblioteca para resolver DNS
#include <lwip/dns.h>
// Inclui a biblioteca para armazenamento de preferências
#include <Preferences.h>

// Define constantes para NAPT e porta
#define NAPT 1000
#define NAPT_PORT 10

// Cria uma instância do servidor web na porta 80
ESP8266WebServer servidor(80);
// Cria uma instância para armazenar preferências
Preferences preferencias;
// Declara um array para armazenar a senha
char senhaArmazenada[32]; // Ajuste o tamanho conforme necessário
// Usa o número de série do chip como senha mestre
const String senhaMaster = String(ESP.getChipId()); 

// Função de configuração do microcontrolador
void setup() {
    Serial.begin(115200); // Inicia a comunicação serial
    Serial.println(F("Repetidor WiFi")); // Exibe mensagem inicial
    Serial.printf("Chip ID: %d\n", ESP.getChipId()); // Exibe o ID do chip
    Serial.printf("Memória disponível na inicialização: %d\n", ESP.getFreeHeap()); // Exibe a memória disponível

    // Inicia o armazenamento de preferências
    preferencias.begin("config", false);
    // Recupera a senha armazenada, se existir
    String senha = preferencias.getString("password", "");
    senha.toCharArray(senhaArmazenada, sizeof(senhaArmazenada)); // Converte para char array

    // Chama funções para configuração do Wi-Fi, NAPT e servidor web
    configurarWiFi();
    inicializarNAPT();
    configurarServidorWeb();
    servidor.begin(); // Inicia o servidor web
}

// Função principal que roda em loop
void loop() {
    servidor.handleClient(); // Processa as requisições do cliente
}

// Função para configurar o Wi-Fi
void configurarWiFi() {
    WiFiManager wifiManager; // Cria uma instância do gerenciador de Wi-Fi
    // Tenta conectar automaticamente
    if (!wifiManager.autoConnect("Configuração Repetidor")) {
        Serial.println(F("Falha na conexão")); // Mensagem de falha
        return; // Sai da função se a conexão falhar
    }

    // Exibe informações da conexão
    Serial.printf("Conectado a: %s\n", WiFi.SSID().c_str());
    auto& servidorDHCP = WiFi.softAPDhcpServer(); // Obtém o servidor DHCP
    servidorDHCP.setDns(WiFi.dnsIP(0)); // Configura o DNS

    // Define nome e senha do AP (Senha será a mesma da rede repetida e o nome será adicionada a palavra Repetidor).
    String nomeAP = WiFi.SSID() + "Repetidor";
    String senhaAP = wifiManager.getWiFiPass();

    // Configura o ponto de acesso
    WiFi.softAPConfig(IPAddress(172, 217, 28, 254),
                      IPAddress(172, 217, 28, 254),
                      IPAddress(255, 255, 255, 0));
    WiFi.softAP(nomeAP.c_str(), senhaAP.c_str()); // Inicia o AP
    Serial.printf("AP: %s\n", WiFi.softAPIP().toString().c_str()); // Exibe o IP do AP
}

// Função para inicializar NAPT
void inicializarNAPT() {
    // Inicializa NAPT e verifica o retorno
    err_t retorno = ip_napt_init(NAPT, NAPT_PORT);
    Serial.printf("ip_napt_init(%d,%d): ret=%d (OK=%d)\n", NAPT, NAPT_PORT, (int)retorno, (int)ERR_OK);
    // Ativa NAPT se a inicialização foi bem-sucedida
    if (retorno == ERR_OK) {
        retorno = ip_napt_enable_no(SOFTAP_IF, 1);
        Serial.printf("ip_napt_enable_no(SOFTAP_IF): ret=%d (OK=%d)\n", (int)retorno, (int)ERR_OK);     
    }
    // Exibe memória disponível após a inicialização do NAPT
    Serial.printf("Memória após inicialização NAPT: %d\n", ESP.getFreeHeap());
    // Mensagem de falha na inicialização do NAPT
    if (retorno != ERR_OK) {
        Serial.printf("Falha na inicialização do NAPT\n");
    }
}

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

// Endpoint para aplicação Python. Neste endpoint a aplicação obten a lista de dispositivos conectados e informações de rede e sinal.
void handleListDevicesJson() {
    if (servidor.hasArg("password")) {
        String senhaEntrada = servidor.arg("password");
        if (senhaEntrada == senhaArmazenada) {
            String json = "{";
            json += "\"total_devices\":" + String(WiFi.softAPgetStationNum()) + ",";
            json += "\"repeated_ssid\":\"" + String(WiFi.SSID()) + "\",";
            json += "\"signal_strength\":" + String(WiFi.RSSI()) + ",";
            json += "\"devices\":[";
            struct station_info *estacao = wifi_softap_get_station_info();
            bool primeiro = true;

            while (estacao) {
                if (!primeiro) {
                    json += ",";
                }
                primeiro = false;

                IPAddress ip = IPAddress(estacao->ip.addr);
                json += "{";
                json += "\"mac\":\"" + String(estacao->bssid[0], HEX) + ":" +
                        String(estacao->bssid[1], HEX) + ":" +
                        String(estacao->bssid[2], HEX) + ":" +
                        String(estacao->bssid[3], HEX) + ":" +
                        String(estacao->bssid[4], HEX) + ":" +
                        String(estacao->bssid[5], HEX) + "\",";
                json += "\"ip\":\"" + ip.toString() + "\"";
                json += "}";
                estacao = STAILQ_NEXT(estacao, next);
            }
            json += "]}";
            servidor.send(200, "application/json", json);
        } else {
            servidor.send(403, "text/plain; charset=UTF-8", "Senha incorreta");
        }
    } else {
        servidor.send(400, "text/plain; charset=UTF-8", "Senha não fornecida");
    }
}

// Função para lidar com a rota raiz
void handleRoot() {
    // Exibe um formulário de cadastro ou de acesso baseado na presença da senha
    String html = (strlen(senhaArmazenada) == 0) ? criarFormularioCadastro() : criarFormularioAcesso();
    servidor.send(200, "text/html; charset=UTF-8", html); // Envia o HTML para o cliente
}

// Função para criar o formulário de cadastro
String criarFormularioCadastro() {
    String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Configuração de Senha</title></head><body>");
    html += F("<h1>Cadastre sua Senha</h1>");
    html += F("<form action=\"/set-password\" method=\"POST\">");
    html += F("<input type=\"password\" name=\"password\" placeholder=\"Digite sua senha\" required>");
    html += F("<input type=\"submit\" value=\"Cadastrar\">");
    html += F("</form></body></html>");
    return html; // Retorna o HTML do formulário
}

// Função para criar o formulário de acesso
String criarFormularioAcesso() {
    String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Acesso Lista Dispositivos</title></head><body>");
    html += F("<h1>Digite a Senha para Acessar a lista de dispositivos</h1>");
    html += F("<form action=\"/devices\" method=\"POST\">");
    html += F("<input type=\"password\" name=\"password\" placeholder=\"Digite sua senha\" required>");
    html += F("<input type=\"submit\" value=\"Confirmar\">");
    html += F("</form>");
    html += F("<br><a href=\"/reset-password\">Redefinir Senha</a>");
    html += F("</body></html>");
    return html; // Retorna o HTML do formulário
}

// Função para criar o formulário de reset de senha
String criarFormularioReset() {
    String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Resetar Senha</title></head><body>");
    html += F("<h1>Digite a Senha Mestre para Redefinir a senha de usuário</h1>");
    html += F("<form action=\"/confirm-reset\" method=\"POST\">");
    html += F("<input type=\"password\" name=\"master_password\" placeholder=\"Senha Mestre\" required>");
    html += F("<input type=\"submit\" value=\"Confirmar\">");
    html += F("</form></body></html>");
    return html; // Retorna o HTML do formulário de reset
}

// Função para lidar com a rota de redefinição de senha
void handleResetPassword() {
    String html = criarFormularioReset(); // Cria o formulário de reset
    servidor.send(200, "text/html; charset=UTF-8", html); // Envia o HTML para o cliente
}

// Função para lidar com a confirmação de redefinição de senha
void handleConfirmReset() {
    if (servidor.hasArg("master_password")) { // Verifica se a senha mestre foi fornecida
        String senhaEntrada = servidor.arg("master_password");
        // Compara com a senha mestre
        if (senhaEntrada == senhaMaster) {
            preferencias.remove("password"); // Remove a senha armazenada
            Serial.println(F("Senha de acesso redefinida.")); // Mensagem de confirmação
            memset(senhaArmazenada, 0, sizeof(senhaArmazenada)); // Limpa a variável da senha
            String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Senha Redefinida!</title></head><body>");
            html += F("<h1>Senha redefinida com sucesso! Cadastre uma nova senha!</h1>");
            html += F("<a href=\"/\">Voltar</a></body></html>");
            servidor.send(200, "text/html; charset=UTF-8", html); // Envia o HTML de sucesso
        } else {
            servidor.send(403, "text/plain; charset=UTF-8", "Senha mestre incorreta"); // Mensagem de erro
        }
    } else {
        servidor.send(400, "text/plain; charset=UTF-8", "Senha não fornecida"); // Mensagem de erro
    }
}

// Função para lidar com a definição de nova senha
void handleSetPassword() {
    if (servidor.hasArg("password")) { // Verifica se a senha foi fornecida
        String senha = servidor.arg("password");
        senha.toCharArray(senhaArmazenada, sizeof(senhaArmazenada)); // Atualiza a variável da senha
        preferencias.putString("password", senha); // Armazena a nova senha
        Serial.println(F("Nova senha de acesso cadastrada.")); // Mensagem de confirmação
        String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Senha Definida</title></head><body>");
        html += F("<h1>Senha definida com sucesso!</h1>");
        html += F("<a href=\"/\">Voltar</a></body></html>");
        servidor.send(200, "text/html; charset=UTF-8", html); // Envia o HTML de sucesso
    } else {
        servidor.send(400, "text/plain; charset=UTF-8", "Senha não fornecida"); // Mensagem de erro
    }
}

// Função para listar os dispositivos conectados
void handleListDevices() {
    if (servidor.hasArg("password")) { // Verifica se a senha foi fornecida
        String senhaEntrada = servidor.arg("password");
        // Compara a senha fornecida com a armazenada
        if (senhaEntrada == senhaArmazenada) {
            String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Dispositivos Conectados</title></head><body>");
            html += F("<h1>Dispositivos Conectados</h1><ul>");
            int numEstacoes = WiFi.softAPgetStationNum(); // Obtém o número de dispositivos conectados
            Serial.printf("Número de dispositivos conectados: %d\n", numEstacoes);
            struct station_info *estacao = wifi_softap_get_station_info(); // Obtém informações das estações
            // Itera sobre as estações conectadas
            while (estacao) {
                IPAddress ip = IPAddress(estacao->ip.addr); // Obtém o IP da estação
                html += "<li>";
                html += "MAC: " + String(estacao->bssid[0], HEX) + ":" +
                        String(estacao->bssid[1], HEX) + ":" +
                        String(estacao->bssid[2], HEX) + ":" +
                        String(estacao->bssid[3], HEX) + ":" +
                        String(estacao->bssid[4], HEX) + ":" +
                        String(estacao->bssid[5], HEX);
                html += " - IP: " + ip.toString();
                html += "</li>";
                estacao = STAILQ_NEXT(estacao, next); // Avança para a próxima estação
            }
            html += F("</ul></body></html>");
            servidor.send(200, "text/html; charset=UTF-8", html); // Envia o HTML com a lista de dispositivos
        } else {
            servidor.send(403, "text/plain; charset=UTF-8", "Senha incorreta"); // Mensagem de erro
        }
    } else {
        servidor.send(400, "text/plain; charset=UTF-8", "Senha não fornecida"); // Mensagem de erro
    }
}

// Função para reinicio da placa repetidora.
void handleReiniciar() {
    if (servidor.hasArg("password")) {
        String senhaEntrada = servidor.arg("password");
        if (senhaEntrada == senhaArmazenada) {
            String html = F("<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Reiniciando...</title></head><body>");
            html += F("<h1>Repetidor reiniciando...</h1>");
            html += F("</body></html>");
            servidor.send(200, "text/html; charset=UTF-8", html); // Envia resposta de reinício

            // Reinicia o ESP8266
            ESP.restart();
        } else {
            servidor.send(403, "text/plain; charset=UTF-8", "Senha incorreta"); // Mensagem de erro
        }
    } else {
        servidor.send(400, "text/plain; charset=UTF-8", "Senha não fornecida"); // Mensagem de erro
    }
}
