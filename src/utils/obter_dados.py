# Função para obter os dados
import json
import requests


def obter_dados():
    response = requests.get('https://api.fbi.gov/wanted/v1/list')
    return json.loads(response.content)