from flask import Flask, request, jsonify
from etcd_config import EtcdClient
import uuid
import os

app = Flask(__name__)
etcd = EtcdClient()

# Prefixo para organizar chaves no ETCD
USERS_PREFIX = "/users/"

# ========== CRUD PARA USUÁRIOS ==========

# Criar usuário (POST)
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    try:
        dados = request.json
        
        # Validação simples
        if not dados.get('nome'):
            return jsonify({"erro": "Nome é obrigatório"}), 400
        
        # Gera ID único
        user_id = str(uuid.uuid4())
        
        # Adiciona ID aos dados
        dados['_id'] = user_id
        
        # Salva no ETCD: chave = "/users/{id}", valor = JSON string
        chave = f"{USERS_PREFIX}{user_id}"
        etcd.put(chave, dados)
        
        return jsonify({
            "mensagem": "Usuário criado com sucesso",
            "id": user_id,
            "chave": chave
        }), 201
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Listar todos usuários (GET)
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        # Busca todas as chaves com prefixo "/users/"
        usuarios_dict = etcd.get_all_with_prefix(USERS_PREFIX)
        
        # Converte para lista
        usuarios = []
        for chave, valor in usuarios_dict.items():
            if isinstance(valor, dict):
                usuarios.append(valor)
        
        return jsonify(usuarios), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Buscar usuário específico (GET)
@app.route('/usuarios/<string:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    try:
        chave = f"{USERS_PREFIX}{usuario_id}"
        usuario = etcd.get(chave)
        
        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({"erro": "Usuário não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Atualizar usuário (PUT)
@app.route('/usuarios/<string:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    try:
        dados = request.json
        chave = f"{USERS_PREFIX}{usuario_id}"
        
        # Verifica se usuário existe
        usuario_existente = etcd.get(chave)
        if not usuario_existente:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Mantém o ID original
        dados['_id'] = usuario_id
        
        # Atualiza no ETCD
        etcd.put(chave, dados)
        
        return jsonify({
            "mensagem": "Usuário atualizado",
            "id": usuario_id
        }), 200
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Deletar usuário (DELETE)
@app.route('/usuarios/<string:usuario_id>', methods=['DELETE'])
def deletar_usuario(usuario_id):
    try:
        chave = f"{USERS_PREFIX}{usuario_id}"
        
        # Verifica se existe antes de deletar
        usuario = etcd.get(chave)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Remove do ETCD
        etcd.delete(chave)
        
        return jsonify({
            "mensagem": "Usuário deletado",
            "id": usuario_id
        }), 200
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Buscar por nome (GET com query params)
@app.route('/usuarios/buscar', methods=['GET'])
def buscar_por_nome():
    try:
        nome = request.args.get('nome', '')
        
        if not nome:
            return jsonify({"erro": "Parâmetro 'nome' é obrigatório"}), 400
        
        # Busca todos usuários
        usuarios_dict = etcd.get_all_with_prefix(USERS_PREFIX)
        
        # Filtra localmente (ETCD não tem busca por conteúdo como MongoDB)
        resultados = []
        for chave, valor in usuarios_dict.items():
            if isinstance(valor, dict) and nome.lower() in valor.get('nome', '').lower():
                resultados.append(valor)
        
        return jsonify(resultados), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# ========== EXEMPLOS ESPECÍFICOS DE USO DO ETCD ==========

# 1. Configurações da Aplicação
@app.route('/config/<string:config_key>', methods=['GET', 'PUT'])
def gerenciar_config(config_key):
    """Gerencia configurações da aplicação"""
    chave = f"/config/app/{config_key}"
    
    if request.method == 'GET':
        valor = etcd.get(chave)
        if valor:
            return jsonify({config_key: valor}), 200
        return jsonify({"erro": "Configuração não encontrada"}), 404
    
    elif request.method == 'PUT':
        dados = request.json
        etcd.put(chave, dados.get('valor', ''))
        return jsonify({"mensagem": "Configuração atualizada"}), 200

# 2. Service Discovery (registro de serviços)
@app.route('/servicos/registrar', methods=['POST'])
def registrar_servico():
    """Registra um serviço no ETCD para service discovery"""
    dados = request.json
    nome_servico = dados.get('nome')
    endpoint = dados.get('endpoint')
    
    if not nome_servico or not endpoint:
        return jsonify({"erro": "Nome e endpoint são obrigatórios"}), 400
    
    chave = f"/services/{nome_servico}/{uuid.uuid4()}"
    etcd.put(chave, {
        "endpoint": endpoint,
        "timestamp": os.time.time(),
        "status": "active"
    })
    
    # Define TTL (Time To Live) - expira após 30 segundos
    # O serviço precisa fazer heartbeat
    return jsonify({"mensagem": "Serviço registrado", "chave": chave}), 200

# 3. Listar serviços ativos
@app.route('/servicos/<string:nome_servico>', methods=['GET'])
def listar_servicos(nome_servico):
    """Lista instâncias ativas de um serviço"""
    chave_prefix = f"/services/{nome_servico}/"
    servicos = etcd.get_all_with_prefix(chave_prefix)
    return jsonify(list(servicos.values())), 200

# 4. Distributed Lock (exemplo simples)
@app.route('/lock/<string:recurso>', methods=['POST', 'DELETE'])
def gerenciar_lock(recurso):
    """Implementa lock distribuído para um recurso"""
    chave_lock = f"/locks/{recurso}"
    
    if request.method == 'POST':
        # Tenta adquirir o lock
        lock_holder = request.json.get('holder', 'unknown')
        
        # Verifica se já existe lock
        lock_existente = etcd.get(chave_lock)
        if lock_existente:
            return jsonify({
                "erro": "Recurso já bloqueado",
                "holder": lock_existente.get('holder')
            }), 409
        
        # Cria o lock
        etcd.put(chave_lock, {
            "holder": lock_holder,
            "timestamp": os.time.time()
        })
        
        return jsonify({
            "mensagem": "Lock adquirido",
            "recurso": recurso,
            "holder": lock_holder
        }), 200
    
    elif request.method == 'DELETE':
        # Libera o lock
        etcd.delete(chave_lock)
        return jsonify({"mensagem": "Lock liberado"}), 200

if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=True, port=port)