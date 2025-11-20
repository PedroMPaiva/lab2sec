# Lab2Sec: DevSecOps & SIEM Automation Lab 


## Sobre o Projeto

O **Lab2Sec** é um ambiente de laboratório prático projetado para simular o ciclo de vida completo de DevSecOps: Desenvolvimento, Infraestrutura e Segurança.

O objetivo foi criar uma aplicação web vulnerável ("Legacy Code Simulation"), containerizá-la, orquestrar a infraestrutura e implementar um monitoramento de segurança ativo usando um SIEM (Wazuh) para detectar ataques em tempo real.

### Arquitetura

O projeto consiste em uma arquitetura de microsserviços rodando sobre Docker:

1.  **Target App (Dev):** Uma aplicação Flask (Python) simulando um E-commerce com vulnerabilidades intencionais (SQL Injection e IDOR).
2.  **Database (Ops):** Um banco de dados PostgreSQL isolado.
3.  **Security Agent (Sec):** O Agente Wazuh, instalado e configurado automaticamente dentro do contêiner da aplicação via Dockerfile.
4.  **SIEM (Sec):** Um cluster Wazuh (Manager, Indexer, Dashboard) para análise de logs e alertas.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.10 (Flask, Psycopg2)
* **Containerização:** Docker & Docker Compose
* **Segurança (SIEM):** Wazuh 4.7.4
* **Automação:** Shell Scripting (dentro do Dockerfile para instalação de agentes)
* **Ataque:** Scripts Python personalizados para SQL Injection

---

## Funcionalidades e Destaques

### 1. Aplicação "Vulnerable-by-Design"
A aplicação possui um endpoint de login (`/login`) que simula código legado vulnerável a SQL Injection, permitindo o bypass de autenticação. Ela gera logs estruturados (`syslog`) sempre que um padrão de ataque é detectado.

### 2. Infraestrutura como Código (IaC)
Todo o ambiente é levantado com um único comando (`docker compose up`). O arquivo `docker-compose.yml` orquestra a rede privada entre a aplicação, o banco de dados e o SIEM.

### 3. Agente de Segurança Automatizado 
Diferente de instalações manuais, o **Wazuh Agent é instalado e configurado automaticamente durante o build do Docker**.
* O `Dockerfile` baixa o agente.
* Configura o `ossec.conf` para ler o arquivo `app.log`.
* Registra o agente no servidor automaticamente ao iniciar o contêiner.

### 4. Regras de Detecção Customizadas
O Wazuh foi configurado com regras XML personalizadas para identificar padrões de ataque específicos na aplicação.

```xml
<group name="local,syslog,">
  <rule id="100001" level="12">
    <program_name>myshop</program_name>
    <description>Ataque Crítico Detectado no E-Commerce</description>
    <match>SQL Injection Detectado</match>
    <group>web,attack,pci_dss_6.5.1,</group>
  </rule>
</group>