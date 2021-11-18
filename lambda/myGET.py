'''
Esta função foi escrita para ser acessada via HTTP GET
através de um API Gateway:
  - Solicitação de Integração: Lambda, sem proxy
  - Solicitação de método: Auth=None
  - Configuração de método GET:
    - Method Request
      - URL Query Parameters:
        - Add Query String: from (mandatório)
        - Add Query String: to   (mandatório)
    - Integration Request
      - Mapping Template:
        - Content type: application/json
        - Template: {"from": "$input.params('from')","to": "$input.params('to')"}
  - Com ativação de CORS

Ela acessa uma Tabela DynamoDB
  - Requer permissão de Query
'''


import json
import boto3
from boto3.dynamodb.conditions import Key


# Os três comandos abaixo estao fora do handler para melhor performance
# Conexão com o Banco de Dados DynamoDB
dynamodb = boto3.resource('dynamodb')

# Conexão com a Tabela de Mensagens
# Deve haver uma tabela com o nome abaixo:
tableMensagens = dynamodb.Table('Mensagens')

# Conexão com o S3
# s3 = boto3.resource('s3')

def lambda_handler(event, context):
    # Dados da mensagem vindos via HTTP GET
    # As chaves de event[] devem bater com os ids do formulário
    remetente = str(event['from'])
    destinatario = str(event['to'])

    # O try/catch é para erro no acesso ao DynamoDB
    try:
        # Uma role deve ser configurada para a esta função,
        # permitindo Query para DynamoDB
        response = tableMensagens.query(
            KeyConditionExpression=Key('destinatario').eq(destinatario))

        for x in response['Items']:
            if x['remetente'] == remetente:
                return {
                # Sucesso
                    'statusCode': 200,
                    'body': json.dumps(x['body'])
                }

#        s3.Object('chat-de-mensagens', destinatario).delete()
    except:
        # Erro: Imprime mensagem de erro no log da função lambda
        # print('Erro: lambda function terminada sem sucesso')
        return {
            'statusCode': 400,
            'body': json.dumps('Erro ao tentar recuperar mensagens')
        }
