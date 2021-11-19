'''
Esta função foi escrita para ser acessada via HTTP POST
através de um API Gateway:
  - Solicitação de Integração: Lambda, sem proxy
  - Solicitação de método: Auth=None
  - Com ativação de CORS
'''


import json
from datetime import datetime
import urllib.parse
import boto3
from boto3.dynamodb.conditions import Key


# Os três comandos abaixo estao fora do handler para melhor performance
# Conexão com o Banco de Dados DynamoDB
dynamodb = boto3.resource('dynamodb')

# Conexão com a Tabela de Mensagens
# Deve haver uma tabela com o nome abaixo:
tableMensagens = dynamodb.Table('Mensagens')

# Conexão com o S3
s = boto3.client('s3')


def lambda_handler(event, context):
    # Data e hora para registrar na mensagem
    data_hora = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

    # Dados da mensagem vindos via HTTP POST
    # As chaves de event[] devem bater com os ids do formulário
    remetente = str(event['from'])
    destinatario = str(event['to'])
    mensagem = str(event['msg'])

    # O try/catch é para erro no acesso ao DynamoDB e ao S3
    try:
        # Uma role deve ser configurada para a esta função,
        # permitindo Query para DynamoDB
        response = tableMensagens.query(
            KeyConditionExpression=Key('destinatario').eq(destinatario))

        body=[
            {
                'data_hora': (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                'msg': mensagem
            }
        ]

        for x in response['Items']:
            if x['remetente'] == remetente:
                body.extend(x['body'])
                break

        # Uma role deve ser configurada para a esta função,
        # permitindo PutItem para DynamoDB
        tableMensagens.put_item(
            Item={
                'destinatario': destinatario, # Chave de Ordenação no Banco
                'remetente': remetente,       # Chave de Partição  no Banco
                'body': body
            }
        )
        fname = destinatario
        f = open('/tmp/' + fname, 'w')
        f.write(remetente)
        f.close()
        s.upload_file('/tmp/' + fname, 'chat-de-mensagens', fname)

        return {
        # Sucesso
            'statusCode': 200,
            'body': json.dumps('Mensagem de '
                               + remetente
                               + ' para '
                               + destinatario
                               + ' inserida no Banco de Dados')
        }

    except:
        # Erro: Imprime mensagem de erro no log da função lambda
        # print('Erro: lambda function terminada sem sucesso')
        return {
            'statusCode': 400,
            'body': json.dumps('Erro ao tentar processar mensagem')
        }
