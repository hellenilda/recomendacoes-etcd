# Sistema de Conexões Profissionais com ETCD

[Sistema de recomendação e gerenciamento de perfis profissionais](https://www.canva.com/design/DAGrjBWuMBI/lpUoyC-ISC1G8UhAnFguYw/edit?utm_content=DAGrjBWuMBI&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) desenvolvido com Flask e ETCD. A aplicação permite criar perfis com habilidades técnicas, realizar buscas especializadas e recomendar conexões entre profissionais com base em habilidades compatíveis.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando o Projeto](#executando-o-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Exemplos de Uso](#exemplos-de-uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Funciona o Sistema de Recomendação](#como-funciona-o-sistema-de-recomendação)
- [Habilidades Válidas](#habilidades-válidas)

## Sobre o Projeto

Este projeto implementa um sistema de networking profissional que utiliza ETCD como banco de dados distribuído. A aplicação oferece:

- CRUD completo de perfis profissionais
- Sistema de recomendação baseado em habilidades compartilhadas
- Busca de profissionais por habilidade específica
- Criação de conexões entre perfis
- Dashboard com estatísticas do sistema
- Validação de habilidades técnicas


## Tecnologias Utilizadas

- **Python 3.13** - Linguagem de programação
- **Flask 3.1.2** - Framework web
- **ETCD 3.5.0** - Sistema de armazenamento distribuído chave-valor
- **etcd3 0.12.0** - Cliente Python para ETCD
- **python-dotenv 1.2.1** - Gerenciamento de variáveis de ambiente

## Funcionalidades

### Gerenciamento de Perfis
- Criar, listar, atualizar e deletar perfis profissionais
- Informações incluem: nome, cargo, empresa, localização e resumo
- Associação de habilidades técnicas validadas

### Sistema de Recomendação
- Recomendação automática de conexões baseada em habilidades compatíveis
- Cálculo de compatibilidade entre perfis
- Ranking de sugestões por número de habilidades em comum
- Exibição de habilidades compartilhadas e exclusivas

### Busca e Filtros
- Busca de profissionais por habilidade específica
- Listagem de todos os perfis cadastrados
- Consulta de perfis individuais com suas habilidades

### Dashboard
- Estatísticas em tempo real do sistema
- Total de perfis cadastrados
- Total de conexões criadas
- Ranking das habilidades mais populares

### Gestão de Conexões
- Criação de conexões entre perfis
- Status de conexões (pendente, aceita, recusada)
- Validação de perfis antes de conectar

## Pré-requisitos

Antes de começar, você precisará ter instalado:

- Python 3.7 ou superior
- Docker (para executar o container ETCD)
- pip (gerenciador de pacotes Python)

### Instalando o ETCD via Docker

Execute o comando abaixo para iniciar um container ETCD 3.5.0:

```bash
docker run -d \
  -p 2379:2379 \
  -p 2380:2380 \
  --name etcd \
  quay.io/coreos/etcd:v3.5.0 \
  /usr/local/bin/etcd \
  --name s1 \
  --data-dir /etcd-data \
  --listen-client-urls http://0.0.0.0:2379 \
  --advertise-client-urls http://0.0.0.0:2379 \
  --listen-peer-urls http://0.0.0.0:2380 \
  --initial-advertise-peer-urls http://0.0.0.0:2380 \
  --initial-cluster s1=http://0.0.0.0:2380 \
  --initial-cluster-token tkn \
  --initial-cluster-state new
```

Para verificar se o ETCD está rodando:
```bash
docker ps | grep etcd
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/hellenilda/recomendacoes-etcd.git
cd recomendacoes-etcd
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

1. Certifique-se de que o container ETCD está rodando:
```bash
docker ps | grep etcd
```

2. Copie o arquivo de exemplo de variáveis de ambiente:
```bash
cp .env.example .env
```

3. Configure as variáveis no arquivo `.env`:
```
ETCD_HOST=localhost
ETCD_PORT=2379
FLASK_PORT=5000
```

Você pode modificar estas variáveis conforme necessário para seu ambiente.

## Executando o Projeto

1. Inicie o servidor Flask:
```bash
python app.py
```

2. A API estará disponível em `http://localhost:5000`

## Endpoints da API

### Informações Gerais

#### Página Inicial
```http
GET /
```
Retorna informações sobre a API e lista de todos os endpoints disponíveis.

### CRUD de Perfis

#### Criar Perfil
```http
POST /perfis
Content-Type: application/json

{
  "nome": "Maria Silva",
  "cargo": "Desenvolvedora Backend",
  "empresa": "Tech Solutions",
  "localizacao": "São Paulo, SP",
  "resumo": "Desenvolvedora com 5 anos de experiência",
  "habilidades": ["python", "docker", "sql", "aws"]
}
```

#### Listar Todos os Perfis
```http
GET /perfis
```

#### Buscar Perfil Específico
```http
GET /perfis/{perfil_id}
```
Retorna o perfil e suas habilidades associadas.

#### Atualizar Perfil
```http
PUT /perfis/{perfil_id}
Content-Type: application/json

{
  "nome": "Maria Silva Santos",
  "cargo": "Senior Backend Developer",
  "empresa": "Tech Solutions",
  "localizacao": "São Paulo, SP",
  "resumo": "Desenvolvedora Senior com 6 anos de experiência"
}
```

#### Deletar Perfil
```http
DELETE /perfis/{perfil_id}
```
Remove o perfil e suas habilidades associadas.

### Sistema de Recomendações

#### Obter Recomendações de Conexões
```http
GET /perfis/{perfil_id}/recomendacoes
```
Retorna os 5 perfis mais compatíveis baseado em habilidades compartilhadas.

**Resposta inclui:**
- Dados do perfil recomendado
- Total de habilidades em comum
- Lista de habilidades compartilhadas
- Habilidades que o outro perfil possui e você não
- Percentual de compatibilidade

### Busca e Filtros

#### Buscar por Habilidade
```http
GET /buscar/habilidade/{nome_habilidade}
```
Retorna todos os perfis que possuem a habilidade especificada.

Exemplo: `GET /buscar/habilidade/python`

### Gestão de Conexões

#### Criar Conexão
```http
POST /conexoes
Content-Type: application/json

{
  "perfil_id_1": "uuid-do-perfil-1",
  "perfil_id_2": "uuid-do-perfil-2"
}
```
Cria uma conexão pendente entre dois perfis.

### Dashboard

#### Estatísticas do Sistema
```http
GET /dashboard
```
Retorna estatísticas gerais incluindo:
- Total de perfis cadastrados
- Total de conexões criadas
- Top 5 habilidades mais populares

## Exemplos de Uso

### 1. Criar um Perfil Profissional

```bash
curl -X POST http://localhost:5000/perfis \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ana Costa",
    "cargo": "Desenvolvedora Full Stack",
    "empresa": "StartupXYZ",
    "localizacao": "Rio de Janeiro, RJ",
    "resumo": "Apaixonada por tecnologia e inovação",
    "habilidades": ["javascript", "python", "react", "nodejs", "docker"]
  }'
```

**Resposta:**
```json
{
  "mensagem": "Perfil criado com sucesso",
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "perfil": {
    "_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "nome": "Ana Costa",
    "cargo": "Desenvolvedora Full Stack",
    "empresa": "StartupXYZ",
    "localizacao": "Rio de Janeiro, RJ",
    "resumo": "Apaixonada por tecnologia e inovação",
    "criado_em": "2025-12-02T10:30:00"
  },
  "habilidades": ["javascript", "python", "react", "nodejs", "docker"]
}
```

### 2. Listar Todos os Perfis

```bash
curl http://localhost:5000/perfis
```

### 3. Obter Recomendações de Conexões

```bash
curl http://localhost:5000/perfis/a1b2c3d4-5678-90ab-cdef-1234567890ab/recomendacoes
```

**Resposta:**
```json
{
  "perfil_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "total_recomendacoes": 3,
  "minhas_habilidades": ["javascript", "python", "react", "nodejs", "docker"],
  "recomendacoes": [
    {
      "perfil_id": "xyz123...",
      "nome": "Carlos Santos",
      "cargo": "DevOps Engineer",
      "empresa": "CloudTech",
      "total_habilidades_comuns": 3,
      "habilidades_comuns": ["python", "docker", "nodejs"],
      "habilidades_que_ele_tem": ["kubernetes", "aws", "ci-cd"],
      "compatibilidade": "60%"
    }
  ]
}
```

### 4. Buscar Profissionais por Habilidade

```bash
curl http://localhost:5000/buscar/habilidade/python
```

### 5. Criar uma Conexão

```bash
curl -X POST http://localhost:5000/conexoes \
  -H "Content-Type: application/json" \
  -d '{
    "perfil_id_1": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "perfil_id_2": "xyz123-4567-89ab-cdef-0987654321zy"
  }'
```

### 6. Atualizar um Perfil

```bash
curl -X PUT http://localhost:5000/perfis/a1b2c3d4-5678-90ab-cdef-1234567890ab \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ana Costa Silva",
    "cargo": "Senior Full Stack Developer",
    "empresa": "StartupXYZ",
    "localizacao": "Rio de Janeiro, RJ",
    "resumo": "Tech Lead com foco em arquitetura de sistemas"
  }'
```

### 7. Ver Estatísticas do Sistema

```bash
curl http://localhost:5000/dashboard
```

**Resposta:**
```json
{
  "estatisticas": {
    "total_perfis": 15,
    "total_conexoes": 8,
    "habilidades_mais_populares": {
      "python": 12,
      "javascript": 10,
      "docker": 8,
      "react": 7,
      "sql": 6
    },
    "ultima_atualizacao": "2025-12-02T14:25:30"
  }
}
```

## Estrutura do Projeto

```
.
├── app.py              # Aplicação Flask com todos os endpoints
├── etcd_config.py      # Cliente ETCD com operações básicas
├── requirements.txt    # Dependências do projeto
├── .env               # Variáveis de ambiente (não versionado)
├── .env.example       # Exemplo de configuração
├── .gitignore         # Arquivos ignorados pelo Git
└── README.md          # Documentação do projeto
```

### Arquivo Principal (app.py)

Contém todos os endpoints da API organizados em seções:

**Prefixos de Organização no ETCD:**
- `/perfis/*` - Dados dos perfis profissionais
- `/habilidades/*` - Habilidades associadas aos perfis
- `/conexoes/*` - Conexões entre perfis

**Funcionalidades:**
- CRUD completo de perfis profissionais
- Sistema de recomendação baseado em habilidades
- Busca por habilidade específica
- Criação de conexões entre perfis
- Dashboard com estatísticas

### Cliente ETCD (etcd_config.py)

Classe `EtcdClient` com métodos para interagir com o ETCD:
- `put(key, value)` - Armazena um valor (converte dict para JSON automaticamente)
- `get(key)` - Recupera um valor (converte JSON de volta para dict)
- `get_all_with_prefix(prefix)` - Busca todas as chaves com prefixo específico
- `delete(key)` - Remove uma chave
- `delete_prefix(prefix)` - Remove todas as chaves com prefixo

## Como Funciona o Sistema de Recomendação

O sistema de recomendação analisa as habilidades de cada perfil para sugerir conexões relevantes:

1. **Coleta de Habilidades**: Ao criar um perfil, as habilidades são validadas contra uma lista predefinida e armazenadas separadamente no ETCD.

2. **Cálculo de Compatibilidade**: 
   - Busca todas as habilidades do perfil solicitante
   - Compara com habilidades de todos os outros perfis
   - Calcula interseção de habilidades (habilidades em comum)
   - Identifica habilidades exclusivas de cada perfil

3. **Ranking**: 
   - Ordena perfis por número de habilidades compartilhadas
   - Calcula percentual de compatibilidade
   - Retorna top 5 recomendações

4. **Resultado**: Para cada recomendação, retorna:
   - Dados do perfil recomendado
   - Número de habilidades em comum
   - Lista de habilidades compartilhadas
   - Habilidades que o outro perfil possui (oportunidade de aprendizado)
   - Percentual de compatibilidade

## Habilidades Válidas

O sistema aceita as seguintes habilidades técnicas:

**Linguagens de Programação:**
- python
- java
- javascript
- typescript

**Bancos de Dados:**
- sql
- nosql

**DevOps e Cloud:**
- docker
- kubernetes
- aws
- ci-cd
- devops

**Frontend e Backend:**
- react
- nodejs
- frontend
- backend
- fullstack

**Mobile:**
- mobile

**Dados e IA:**
- machine-learning
- data-science

**Ferramentas:**
- git

Para adicionar novas habilidades, edite a lista `HABILIDADES_VALIDAS` em `app.py`.

