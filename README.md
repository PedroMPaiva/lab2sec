# Lab2Sec: DevSecOps & SIEM Automation Lab 🛡️🐳

![DevSecOps](https://img.shields.io/badge/Focus-DevSecOps-red)
![Docker](https://img.shields.io/badge/Container-Docker-blue)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-green)
![WAF](https://img.shields.io/badge/WAF-ModSecurity-orange)

## 📖 Sobre o Projeto

O **Lab2Sec** é um ambiente de laboratório prático projetado para simular o ciclo de vida completo de DevSecOps: Desenvolvimento, Infraestrutura, Segurança Ofensiva e Defensiva.

O objetivo foi criar uma aplicação web vulnerável ("Legacy Code Simulation"), containerizá-la, orquestrar a infraestrutura e implementar uma estratégia de **Defesa em Profundidade** (Defense in Depth), combinando um **WAF** na borda para bloqueio e um **SIEM** interno para detecção.

### 🏗️ Arquitetura (Defense in Depth)

O projeto consiste em uma arquitetura de microsserviços orquestrada via Docker Compose:

1.  **WAF (Active Defense):** Um Proxy Reverso **Nginx** com **ModSecurity** (OWASP CRS) atuando como guarda-costas na porta 80. Ele intercepta e bloqueia ataques antes que cheguem à aplicação.
2.  **Target App (Dev):** Uma aplicação Flask (Python) isolada na rede interna (sem acesso externo direto), simulando um E-commerce com vulnerabilidades intencionais.
3.  **Database (Ops):** Um banco de dados PostgreSQL isolado.
4.  **Security Agent (Sec):** O Agente Wazuh, instalado e configurado automaticamente dentro do contêiner da aplicação via Dockerfile.
5.  **SIEM (Sec):** Um cluster Wazuh (Manager, Indexer, Dashboard) para análise de logs, correlação de eventos e alertas.

---

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.10 (Flask, Psycopg2)
* **Containerização:** Docker & Docker Compose
* **WAF:** Nginx + ModSecurity + OWASP Core Rule Set (CRS)
* **SIEM:** Wazuh 4.7.4
* **Automação:** Shell Scripting e Dockerfile Multi-stage
* **Ataque:** Scripts Python personalizados para SQL Injection

---

## ⚡ Funcionalidades e Destaques

### 1. Aplicação "Vulnerable-by-Design"
Endpoint de login (`/login`) que simula código legado vulnerável a SQL Injection. Gera logs estruturados (`syslog`) compatíveis com o SIEM.

### 2. Defesa Ativa (WAF)
Implementação de um Web Application Firewall na borda.
* **Proxy Reverso:** Esconde a topologia da rede interna e o IP da aplicação.
* **Bloqueio de Ataques:** Regras da OWASP configuradas para bloquear injeções de SQL (Erro 403 Forbidden) protegendo a aplicação vulnerável.

### 3. Infraestrutura como Código (IaC)
Todo o ambiente (5 contêineres + redes) é levantado com um único comando (`docker compose up`).

### 4. Agente de Segurança Automatizado 🤖
Instalação "Zero-Touch" do agente Wazuh durante o build do contêiner.
* O `Dockerfile` baixa, instala e configura o `ossec.conf` automaticamente.
* O agente se registra no servidor e inicia o monitoramento sem intervenção humana.

### 5. Regras de Detecção Customizadas
Regras XML personalizadas no Wazuh para identificar ataques que porventura passem pelo WAF ou ocorram internamente.

```xml
<group name="local,syslog,">
  <rule id="100001" level="12">
    <program_name>myshop</program_name>
    <description>Ataque Crítico Detectado no E-Commerce</description>
    <match>SQL Injection Detectado</match>
  </rule>
</group>