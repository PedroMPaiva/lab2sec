FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    lsb-release \ 
    procps \ 
    && rm -rf /var/lib/apt/lists/*

RUN wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.7.4-1_amd64.deb && \
    WAZUH_MANAGER='wazuh.manager' WAZUH_AGENT_NAME='lab2sec-app' dpkg -i ./wazuh-agent_4.7.4-1_amd64.deb && \
    rm wazuh-agent_4.7.4-1_amd64.deb

RUN sed -i '/<ossec_config>/a \
  <localfile>\n\
    <location>/app/app.log</location>\n\
    <log_format>syslog</log_format>\n\
  </localfile>' /var/ossec/etc/ossec.conf

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["/bin/bash", "-c", "/var/ossec/bin/wazuh-agentd & python myshop.py"]
