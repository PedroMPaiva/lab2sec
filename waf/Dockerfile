# Usamos a imagem oficial do ModSecurity com Nginx
FROM owasp/modsecurity-crs:nginx

# Copiamos nossa configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80 (HTTP padrão)
EXPOSE 80