import json
import boto3
from datetime import datetime


def lambda_handler(event, context):
    # Conexão com o Banco de Dados DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Conexão com a Tabela de Mensagens
    tableMensagens = dynamodb.Table('TabelaMensagens')

    # Data e hora para registrar a mensagem
    dataEhora = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

    # Dados da mensagem vindos do http POST
    # As chaves do objeto event[] devem bater com os ids do formulário
    remetente = str(event['from'])
    destinatario = str(event['to'])
    mensagem = str(event['msg'])

    # Putting a try/catch to log to user when some error occurs
    try:
        tableMensagens.put_item(
            Item={
                'dataEhora': dataEhora,
                'remetente': remetente,
                'destinatario': destinatario,
                'mensagem': mensagem
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Mensagem inserida no Banco de Dados!')
        }
    except:
        print('Erro: lambda function terminada sem sucesso')
        return {
                'statusCode': 400,
                'body': json.dumps('Erro ao tentar processar mensagem')
        }
