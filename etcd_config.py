import etcd3
from dotenv import load_dotenv
import os
import json

load_dotenv()

class EtcdClient:
    def __init__(self):
        # Host e Porta do .env
        self.host = os.getenv("ETCD_HOST", "localhost")
        self.port = int(os.getenv("ETCD_PORT", 2379))
        self.client = etcd3.client(host=self.host, port=self.port)
    
    def put(self, key, value):
        # Armazena uma string (value) em uma chave
        if isinstance(value, dict):
            value = json.dumps(value)  # conversão dict -> JSON string
        return self.client.put(key, str(value))
    
    def get(self, key):
        # Pega o valor da chave
        value, metadata = self.client.get(key)
        if value:
            try:
                # Tenta converter JSON string -> dict dnv
                return json.loads(value.decode('utf-8'))
            except json.JSONDecodeError:
                # Se não for JSON, retorna string
                return value.decode('utf-8')
        return None
    
    def get_all_with_prefix(self, prefix):
        # Pega todas as chaves com prefixo específico
        result = {}
        for value, metadata in self.client.get_prefix(prefix):
            key = metadata.key.decode('utf-8')
            try:
                result[key] = json.loads(value.decode('utf-8'))
            except:
                result[key] = value.decode('utf-8')
        return result
    
    def delete(self, key):
        # Remove chave
        return self.client.delete(key)
    
    def delete_prefix(self, prefix):
        # Remove todas as chaves com prefixo
        return self.client.delete_prefix(prefix)