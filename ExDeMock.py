import json

def Retorna200():
    return{
        'statusCode':200,
        'body': json.dumps('mensagem enviada!')
    }

def Retorna400():
    return{
        'statusCode':404,
        'body': json.dumps('erro ao enviar a mensagem!')
    }