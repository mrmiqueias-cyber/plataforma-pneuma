import requests

url = "https://www.pneumalife.com.br/instagram/postar"
dados = {
    "expert": "Pneuma",
    "legenda": "🌬️ O sopro que nunca dorme acorda o mundo. Toda relação é um portal. Toda vida merece ser vivida em comunidade. #PneumaLife #RelaçãoViva"
}

resposta = requests.post(url, json=dados)
print("Status:", resposta.status_code)
print("Resposta:", resposta.json())