# Lab2Sec: DevSecOps & SIEM Automation Lab 🛡️🚀

![DevSecOps](https://img.shields.io/badge/Focus-DevSecOps-red)
![CI/CD](https://img.shields.io/badge/Pipeline-GitHub%20Actions-blueviolet)
![SAST](https://img.shields.io/badge/SAST-Bandit-yellow)
![DAST](https://img.shields.io/badge/DAST-OWASP%20ZAP-orange)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-green)

## 📖 Sobre o Projeto

O **Lab2Sec** é um ambiente de laboratório prático projetado para simular o ciclo de vida completo de DevSecOps: do Código à Produção.

O projeto vai além da infraestrutura, implementando o conceito de **"Shift Left Security"**. Utilizamos automação de CI/CD para detectar vulnerabilidades no código e na aplicação em execução antes mesmo do deploy, além de manter uma defesa ativa em tempo real.

### 🏗️ Arquitetura (Defense in Depth)

O ambiente é composto por microsserviços orquestrados via Docker Compose:

1.  **WAF (Borda):** Nginx + ModSecurity (OWASP CRS) atuando como Proxy Reverso na porta 80, bloqueando ataques web.
2.  **App (Backend):** Aplicação Flask (Python) vulnerável, isolada na rede interna.
3.  **Database:** PostgreSQL.
4.  **SIEM:** Cluster Wazuh para monitoramento e detecção de ameaças.
5.  **Agente:** Instalado automaticamente dentro do contêiner do App.

---

## 🔄 DevSecOps Pipeline (CI/CD)

O projeto utiliza **GitHub Actions** para garantir a segurança em cada commit:

### 1. SAST (Static Application Security Testing) 🔍
**Ferramenta:** [Bandit](https://github.com/PyCQA/bandit)
* Analisa o código fonte Python em busca de falhas de segurança (ex: senhas hardcoded, SQLi, binds inseguros).
* **Governança:** Implementação de *Risk Acceptance* (aceite de risco) documentado via `# nosec` para fins didáticos do laboratório.

### 2. DAST (Dynamic Application Security Testing) 💥
**Ferramenta:** [OWASP ZAP](https://www.zaproxy.org/)
* Sobe a infraestrutura completa (WAF + App + DB) em um ambiente efêmero no GitHub.
* Realiza ataques reais contra a aplicação rodando (através do WAF na porta 80).
* Gera relatórios de conformidade e vulnerabilidades web.

---

## ⚡ Funcionalidades de Segurança

### Defesa Ativa (WAF)
* **Proxy Reverso:** Esconde a topologia da rede interna e o IP da aplicação.
* **Bloqueio:** Regras da OWASP configuradas para bloquear injeções de SQL (Erro 403 Forbidden) protegendo a aplicação vulnerável.

### Detecção Inteligente (SIEM)
* **Monitoramento de Logs:** O Agente Wazuh lê os logs da aplicação (`app.log`) em tempo real.
* **Regras Customizadas:** Configuração XML para identificar padrões de ataque específicos que passaram pelo WAF ou ocorreram internamente.

```xml
<group name="local,syslog,">
  <rule id="100001" level="12">
    <program_name>myshop</program_name>
    <description>Ataque Crítico Detectado no E-Commerce</description>
    <match>SQL Injection Detectado</match>
  </rule>
</group>