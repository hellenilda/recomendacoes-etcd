from flask import Flask, request, jsonify
from etcd_config import EtcdClient
import uuid
import os
from datetime import datetime

app = Flask(__name__)
etcd = EtcdClient()

# ========== PREFIXOS ==========
PERFIS_PREFIX = "/perfis/"
HABILIDADES_PREFIX = "/habilidades/"
CONEXOES_PREFIX = "/conexoes/"

# ========== HABILIDADES VÁLIDAS ==========
HABILIDADES_VALIDAS = [
    "python", "java", "javascript", "typescript",
    "sql", "nosql", "docker", "kubernetes", "aws",
    "react", "nodejs", "git", "ci-cd", "devops",
    "frontend", "backend", "fullstack", "mobile",
    "machine-learning", "data-science"
]

# ========== CRUD DE PERFIS ==========

@app.route('/perfis', methods=['POST'])
def criar_perfil():
    dados = request.json
    
    # Validação
    if not dados.get('nome'):
        return jsonify({"erro": "Nome é obrigatório"}), 400
    
    # ID único
    perfil_id = str(uuid.uuid4())
    
    # Prepara dados do perfil
    perfil = {
        "_id": perfil_id,
        "nome": dados.get('nome'),
        "cargo": dados.get('cargo', 'Desenvolvedor'),
        "empresa": dados.get('empresa', 'Não informada'),
        "localizacao": dados.get('localizacao', 'Não informada'),
        "resumo": dados.get('resumo', ''),
        "criado_em": datetime.now().isoformat()
    }
    
    # Processamento das habilidades
    habilidades = []
    if 'habilidades' in dados:
        for habilidade in dados['habilidades']:
            if habilidade.lower() in HABILIDADES_VALIDAS:
                habilidades.append(habilidade.lower())
    
    # Salva perfil no ETCD
    chave_perfil = f"{PERFIS_PREFIX}{perfil_id}"
    etcd.put(chave_perfil, perfil)
    
    # Salva habilidades de forma separada (pra pesquisa)
    if habilidades:
        chave_habilidades = f"{HABILIDADES_PREFIX}{perfil_id}"
        etcd.put(chave_habilidades, {"habilidades": habilidades})
        
        # índice invertido pra busca por habilidade
        for habilidade in habilidades:
            chave_indice = f"/indices/habilidade/{habilidade}/{perfil_id}"
            etcd.put(chave_indice, perfil_id)
    
    return jsonify({
        "mensagem": "Perfil criado com sucesso",
        "id": perfil_id,
        "perfil": perfil,
        "habilidades": habilidades
    }), 201

@app.route('/perfis', methods=['GET'])
def listar_perfis():
    try:
        perfis_dict = etcd.get_all_with_prefix(PERFIS_PREFIX)
        perfis = list(perfis_dict.values())
        return jsonify({
            "total": len(perfis),
            "perfis": perfis
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Busca perfil por ID
@app.route('/perfis/<string:perfil_id>', methods=['GET'])
def buscar_perfil(perfil_id):
    chave = f"{PERFIS_PREFIX}{perfil_id}"
    perfil = etcd.get(chave)
    
    if perfil:
        # Busca habilidades do perfil
        chave_habilidades = f"{HABILIDADES_PREFIX}{perfil_id}"
        habilidades_data = etcd.get(chave_habilidades)
        
        if habilidades_data and 'habilidades' in habilidades_data:
            perfil['habilidades'] = habilidades_data['habilidades']
        
        return jsonify(perfil), 200
    else:
        return jsonify({"erro": "Perfil não encontrado"}), 404


@app.route('/perfis/<string:perfil_id>', methods=['PUT'])
def atualizar_perfil(perfil_id):

    dados = request.json
    chave = f"{PERFIS_PREFIX}{perfil_id}"
    
    # Verifica se o perfil existe
    perfil_existente = etcd.get(chave)
    if not perfil_existente:
        return jsonify({"erro": "Perfil não encontrado"}), 404
    
    # Atualiza
    perfil_existente.update({
        "nome": dados.get('nome', perfil_existente.get('nome')),
        "cargo": dados.get('cargo', perfil_existente.get('cargo')),
        "empresa": dados.get('empresa', perfil_existente.get('empresa')),
        "localizacao": dados.get('localizacao', perfil_existente.get('localizacao')),
        "resumo": dados.get('resumo', perfil_existente.get('resumo')),
        "atualizado_em": datetime.now().isoformat()
    })
    
    # Atualiza no ETCD
    etcd.put(chave, perfil_existente)
    
    return jsonify({
        "mensagem": "Perfil atualizado",
        "perfil": perfil_existente
    }), 200


@app.route('/perfis/<string:perfil_id>', methods=['DELETE'])
def deletar_perfil(perfil_id):

    chave = f"{PERFIS_PREFIX}{perfil_id}"
    
    # Verifica se existe
    perfil = etcd.get(chave)
    if not perfil:
        return jsonify({"erro": "Perfil não encontrado"}), 404
    
    # Remove perfil
    etcd.delete(chave)
    
    # Remove habilidades associadas
    chave_habilidades = f"{HABILIDADES_PREFIX}{perfil_id}"
    etcd.delete(chave_habilidades)
    
    return jsonify({
        "mensagem": "Perfil deletado",
        "id": perfil_id
    }), 200


# ========== SISTEMA DE RECOMENDAÇÕES ==========

@app.route('/perfis/<string:perfil_id>/recomendacoes', methods=['GET'])
def recomendar_conexoes(perfil_id):
    # Recomenda conexões a partir das habilidades em comum
    
    # Busca habilidades do perfil
    chave_habilidades = f"{HABILIDADES_PREFIX}{perfil_id}"
    habilidades_data = etcd.get(chave_habilidades)
    
    if not habilidades_data or 'habilidades' not in habilidades_data:
        return jsonify({"erro": "Perfil sem habilidades cadastradas"}), 400
    
    minhas_habilidades = set(habilidades_data['habilidades'])
    
    # Busca TODOS os perfis
    todos_perfis = etcd.get_all_with_prefix(PERFIS_PREFIX)
    
    recomendacoes = []
    
    for chave, perfil in todos_perfis.items():
        # Pega o ID do perfil da chave
        outro_id = chave.replace(PERFIS_PREFIX, "")
        
        # Pula o próprio perfil
        if outro_id == perfil_id:
            continue
        
        # Busca habilidades do outros perfis
        hab_outro_chave = f"{HABILIDADES_PREFIX}{outro_id}"
        hab_outro_data = etcd.get(hab_outro_chave)
        
        if hab_outro_data and 'habilidades' in hab_outro_data:
            habilidades_outro = set(hab_outro_data['habilidades'])
            
            # Calcula habilidades em comum (interseção)
            habilidades_comuns = minhas_habilidades.intersection(habilidades_outro)
            
            if habilidades_comuns:
                recomendacoes.append({
                    "id": outro_id,
                    "nome": perfil.get('nome'),
                    "cargo": perfil.get('cargo'),
                    "empresa": perfil.get('empresa'),
                    "habilidades_comuns": list(habilidades_comuns),
                    "total_habilidades_comuns": len(habilidades_comuns),
                    "compatibilidade": f"{(len(habilidades_comuns) / len(minhas_habilidades)) * 100:.1f}%"
                })
    
    # Ordena por maior compatibilidade
    recomendacoes.sort(key=lambda x: x['total_habilidades_comuns'], reverse=True)
    
    return jsonify({
        "perfil_id": perfil_id,
        "total_recomendacoes": len(recomendacoes),
        "minhas_habilidades": list(minhas_habilidades),
        "recomendacoes": recomendacoes[:5]  # Top 5
    })


@app.route('/buscar/habilidade/<string:habilidade>', methods=['GET'])
def buscar_por_habilidade(habilidade):
    # busca todos os perfis com uma habilidade específica
    
    habilidade = habilidade.lower()
    if habilidade not in HABILIDADES_VALIDAS:
        return jsonify({
            "erro": "Habilidade inválida",
            "habilidades_validas": HABILIDADES_VALIDAS
        }), 400
    
    resultados = []
    
    # Busca em TODOS os perfis
    todos_perfis = etcd.get_all_with_prefix(PERFIS_PREFIX)
    
    for chave, perfil in todos_perfis.items():
        perfil_id = chave.replace(PERFIS_PREFIX, "")
        
        # Busca habilidades deste perfil
        hab_chave = f"{HABILIDADES_PREFIX}{perfil_id}"
        hab_data = etcd.get(hab_chave)
        
        if hab_data and 'habilidades' in hab_data:
            if habilidade in hab_data['habilidades']:
                resultados.append({
                    "id": perfil_id,
                    "nome": perfil.get('nome'),
                    "cargo": perfil.get('cargo'),
                    "empresa": perfil.get('empresa'),
                    "localizacao": perfil.get('localizacao')
                })
    
    return jsonify({
        "habilidade": habilidade,
        "total": len(resultados),
        "resultados": resultados
    })


@app.route('/conexoes', methods=['POST'])
def criar_conexao():
    # conexão entre dois perfis
    dados = request.json
    perfil_id_1 = dados.get('perfil_id_1')
    perfil_id_2 = dados.get('perfil_id_2')
    
    if not perfil_id_1 or not perfil_id_2:
        return jsonify({"erro": "IDs de ambos os perfis são necessários"}), 400
    
    # Verifica se ambos perfis existem
    if not etcd.get(f"{PERFIS_PREFIX}{perfil_id_1}"):
        return jsonify({"erro": f"Perfil {perfil_id_1} não encontrado"}), 404
    
    if not etcd.get(f"{PERFIS_PREFIX}{perfil_id_2}"):
        return jsonify({"erro": f"Perfil {perfil_id_2} não encontrado"}), 404
    
    # Cria ID único para a conexão
    conexao_id = str(uuid.uuid4())
    
    conexao = {
        "_id": conexao_id,
        "perfil_id_1": perfil_id_1,
        "perfil_id_2": perfil_id_2,
        "status": "pendente",  # pendente, aceita, recusada
        "criada_em": datetime.now().isoformat()
    }
    
    # Salva conexão
    chave_conexao = f"{CONEXOES_PREFIX}{conexao_id}"
    etcd.put(chave_conexao, conexao)
    
    return jsonify({
        "mensagem": "Conexão criada",
        "conexao": conexao
    }), 201


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # estatísticas do sistema
    
    # Conta perfis
    perfis = etcd.get_all_with_prefix(PERFIS_PREFIX)
    
    # Conta conexões
    conexoes = etcd.get_all_with_prefix(CONEXOES_PREFIX)
    
    # Conta habilidades mais comuns
    contagem_habilidades = {}
    for chave in etcd.get_all_with_prefix(HABILIDADES_PREFIX):
        hab_data = etcd.get(chave)
        if hab_data and 'habilidades' in hab_data:
            for habilidade in hab_data['habilidades']:
                contagem_habilidades[habilidade] = contagem_habilidades.get(habilidade, 0) + 1
    
    # Ordena habilidades mais populares
    habilidades_populares = sorted(
        contagem_habilidades.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return jsonify({
        "estatisticas": {
            "total_perfis": len(perfis),
            "total_conexoes": len(conexoes),
            "habilidades_mais_populares": dict(habilidades_populares),
            "ultima_atualizacao": datetime.now().isoformat()
        }
    })

# ========== HOME ==========
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "aplicacao": "Sistema de Conexões Profissionais",
        "descricao": "API para gerenciamento de perfis profissionais usando ETCD",
        "endpoints": {
            "GET /": "Esta página",
            "POST /perfis": "Criar perfil profissional",
            "GET /perfis": "Listar todos perfis",
            "GET /perfis/{id}": "Buscar perfil específico",
            "PUT /perfis/{id}": "Atualizar perfil",
            "DELETE /perfis/{id}": "Deletar perfil",
            "GET /perfis/{id}/recomendacoes": "Recomendar conexões",
            "GET /buscar/habilidade/{nome}": "Buscar por habilidade",
            "POST /conexoes": "Criar conexão",
            "GET /dashboard": "Estatísticas do sistema"
        },
        "tecnologias": ["Python", "Flask", "ETCD"],
        "status": "online"
    })

if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    print(f"""
    🔗 Endpoints disponíveis:
    http://localhost:{port}/
    
    📈 Armazenamento: {len(etcd.get_all_with_prefix(PERFIS_PREFIX))} perfis cadastrados
    
    ✅ Servidor rodando na porta {port}
    """)
    app.run(debug=True, port=port, host='0.0.0.0')