import requests
import json
from flask import Flask
from flask_restplus import Api, Resource, fields

from src.clients.oracle_connection import DB

app = Flask(__name__)

# Função para obter os dados
def obter_dados():
    response = requests.get('https://api.fbi.gov/wanted/v1/list')
    response2 = requests.get('https://ws-public.interpol.int/notices/v1/red?resultPerPage=20&page=1')
    return json.loads(response.content)

# Função para buscar um criminoso por ID
def buscar_criminoso_por_id(data, id):
    for item in data.get("items", []):
        id_formatado = item.get('@id').split("/")[-1]
        if id_formatado == id:
            return item
    return None

# Configuração da documentação Swagger
api = Api(app, version='1.0', title='API Busca', description='API para acessar dados de criminosos')
ns = api.namespace('Challenge idwall', description='Buscar criminosos')

modelo_criminoso = api.model('Criminoso', {
    'id': fields.String(description='ID do criminoso'),
    'nome': fields.String(description='Nome do criminoso'),
    'idade': fields.String(description='Idade do criminoso'),
    'sexo': fields.String(description='Sexo do criminoso'),
    'status': fields.String(description='Status do criminoso'),
    'descricao': fields.String(description='Descrição do criminoso'),
})

# Função para buscar todos os criminosos no banco de dados
@ns.route('/buscar_criminosos')
class CriminososResource(Resource):
    @ns.marshal_list_with(modelo_criminoso)
    def get(self):
        connection = DB.conectar_banco()
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Nome, Idade, Sexo, Status, Descricao FROM T_CRIMINOSOS")
        resultados = cursor.fetchall()

        criminosos_banco = []
        for resultado in resultados:
            criminoso = {
                'id': resultado[0],
                'nome': resultado[1],
                'idade': resultado[2],
                'sexo': resultado[3],
                'status': resultado[4],
                'descricao': resultado[5]
            }
            criminosos_banco.append(criminoso)

        connection.close()

        return criminosos_banco
    
# Função para buscar um criminoso por ID
@ns.route('/buscar_criminoso_por_id/<string:id>')
class CriminosoPorIdResource(Resource):
    @ns.marshal_with(modelo_criminoso)
    def get(self, id):
        connection = DB.conectar_banco()
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Nome, Idade, Sexo, Status, Descricao FROM T_CRIMINOSOS WHERE ID = :id", id=id)
        resultado = cursor.fetchone()

        if not resultado:
            api.abort(404, "Criminoso não encontrado")

        criminoso = {
            'id': resultado[0],
            'nome': resultado[1],
            'idade': resultado[2],
            'sexo': resultado[3],
            'status': resultado[4],
            'descricao': resultado[5]
        }

        connection.close()

        return criminoso

# Função para buscar e atualizar os dados no banco Oracle
@app.route('/atualizar', methods=['GET'])
def atualizar_dados():
    data = obter_dados()
    connection = DB.conectar_banco()
    cursor = connection.cursor()
    print("Conexao ok")

    for item in data.get("items", []):
        id = item.get('@id', 'ID não disponível')
        nome = item.get('title', 'Nome não disponível')
        idade = item.get('age_range', 'Idade não disponível')
        sexo = item.get('sex', 'Sexo não disponível')
        status = item.get('status', 'Status não disponível')
        descricao = item.get('caution', 'Descrição não disponível')

        id = id.split("/")[-1]

        cursor.execute("SELECT ID FROM T_CRIMINOSOS WHERE ID = :id", id=id)
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE T_CRIMINOSOS
                SET Nome = :nome, Idade = :idade, Sexo = :sexo, Status = :status, Descricao = :descricao
                WHERE ID = :id
            """, id=id, nome=nome, idade=idade, sexo=sexo, status=status, descricao=descricao)
            print("ID atualizado:", id)
        else:
            cursor.execute("""
                INSERT INTO T_CRIMINOSOS (ID, Nome, Idade, Sexo, Status, Descricao)
                VALUES (:id, :nome, :idade, :sexo, :status, :descricao)
            """, id=id, nome=nome, idade=idade, sexo=sexo, status=status, descricao=descricao)
            print("ID inserido:", id)

    connection.commit()
    cursor.close()
    connection.close()

    return "Sucesso"

if __name__ == '__main__':
    app.run()
