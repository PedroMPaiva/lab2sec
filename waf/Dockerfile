# Usamos a imagem oficial do ModSecurity com Nginx
FROM owasp/modsecurity-crs:nginx

# Remove a configuração padrão que causa conflito
RUN rm /etc/nginx/conf.d/default.conf

# Copia a nossa configuração personalizada
COPY nginx.conf /etc/nginx/conf.d/meu-waf.conf

# Expõe a porta 80 (HTTP padrão)
EXPOSE 80
