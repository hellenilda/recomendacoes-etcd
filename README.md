# API REST com Flask e ETCD

Este projeto demonstra a implementação de uma API REST usando Flask integrada com ETCD, um sistema de armazenamento distribuído de chave-valor. O projeto inclui operações CRUD completas para gerenciamento de usuários, além de exemplos práticos de uso do ETCD para configurações, service discovery e locks distribuídos.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando o Projeto](#executando-o-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Exemplos de Uso](#exemplos-de-uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Casos de Uso do ETCD](#casos-de-uso-do-etcd)

---

## Funcionalidades

- CRUD completo de usuários armazenados no ETCD
- Gerenciamento de configurações da aplicação
- Service discovery para registro e descoberta de serviços
- Implementação de locks distribuídos
- Busca e filtragem de dados

---

## Tecnologias Utilizadas

- **Python 3.13** - Linguagem de programação
- **Flask 3.1.2** - Framework web
- **ETCD 3.5.0** - Sistema de armazenamento distribuído
- **etcd3 0.12.0** - Cliente Python para ETCD
- **python-dotenv** - Gerenciamento de variáveis de ambiente

---

## Estrutura do Projeto

```
.
├── app.py              # Aplicação principal com todos os endpoints
├── etcd_config.py      # Cliente ETCD com operações básicas
├── requirements.txt    # Dependências do projeto
├── .env               # Variáveis de ambiente
├── .gitignore         # Arquivos ignorados pelo Git
└── README.md          # Documentação do projeto
```

### Arquivo Principal (app.py)

Contém todos os endpoints da API organizados em seções:
- CRUD completo de usuários
- Gerenciamento de configurações
- Service discovery
- Locks distribuídos

### Cliente ETCD (etcd_config.py)

Classe `EtcdClient` com métodos para:
- `put(key, value)` - Armazena um valor
- `get(key)` - Recupera um valor
- `get_all_with_prefix(prefix)` - Busca todas as chaves com prefixo
- `delete(key)` - Remove uma chave
- `delete_prefix(prefix)` - Remove todas as chaves com prefixo

---

## Pré-requisitos

- Python 3.7 ou superior
- Container Docker ETCD 3.5.0
- pip

---

### Instalação do ETCD

**Docker:**
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

---

## Configurações de Ambiente

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

4. Certifique-se de que o container do ETCD está rodando:
```bash
docker ps | grep etcd
```

5. Renomear o arquivo `.env.example` para `.env` e preencher os valores de acordo com sua configuração:
```
# Exemplo
ETCD_HOST=localhost
ETCD_PORT=2379
FLASK_PORT=5000
```

Você pode modificar as variáveis conforme necessário.

---

## Executando o Projeto

1. Inicie o servidor Flask:
```bash
python app.py
```

2. A API estará disponível em `http://localhost:5000`

---

## Endpoints da API

### CRUD de Usuários

#### Criar Usuário
```http
POST /usuarios
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "idade": 30
}
```

#### Listar Todos os Usuários
```http
GET /usuarios
```

#### Buscar Usuário Específico
```http
GET /usuarios/{usuario_id}
```

#### Atualizar Usuário
```http
PUT /usuarios/{usuario_id}
Content-Type: application/json

{
  "nome": "João Silva Santos",
  "email": "joao.santos@email.com",
  "idade": 31
}
```

#### Deletar Usuário
```http
DELETE /usuarios/{usuario_id}
```

#### Buscar por Nome
```http
GET /usuarios/buscar?nome=João
```

---

### Gerenciamento de Configurações

#### Obter Configuração
```http
GET /config/{config_key}
```

#### Definir Configuração
```http
PUT /config/{config_key}
Content-Type: application/json

{
  "valor": "valor_da_configuracao"
}
```

---

### Service Discovery

#### Registrar Serviço
```http
POST /servicos/registrar
Content-Type: application/json

{
  "nome": "api-pagamentos",
  "endpoint": "http://localhost:8080"
}
```

#### Listar Serviços
```http
GET /servicos/{nome_servico}
```

---

### Locks Distribuídos

#### Adquirir Lock
```http
POST /lock/{recurso}
Content-Type: application/json

{
  "holder": "servico-1"
}
```

#### Liberar Lock
```http
DELETE /lock/{recurso}
```

---

## Exemplos de Uso

### Criar um Usuário

```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "idade": 28,
    "cidade": "São Paulo"
  }'
```

### Listar Todos os Usuários

```bash
curl http://localhost:5000/usuarios
```

### Buscar Usuário por Nome

```bash
curl "http://localhost:5000/usuarios/buscar?nome=Maria"
```

### Definir uma Configuração

```bash
curl -X PUT http://localhost:5000/config/max_connections \
  -H "Content-Type: application/json" \
  -d '{"valor": "100"}'
```

### Registrar um Serviço

```bash
curl -X POST http://localhost:5000/servicos/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "api-usuarios",
    "endpoint": "http://localhost:5001"
  }'
```

### Adquirir um Lock

```bash
curl -X POST http://localhost:5000/lock/recurso-critico \
  -H "Content-Type: application/json" \
  -d '{"holder": "worker-1"}'
```

---

## Casos de Uso do ETCD

### 1. Armazenamento de Dados

O ETCD é usado como banco de dados chave-valor para armazenar informações de usuários. Cada usuário é armazenado com uma chave única no formato `/users/{id}`.

### 2. Configurações Centralizadas

Permite armazenar configurações da aplicação que podem ser acessadas e modificadas dinamicamente sem reiniciar o serviço.

### 3. Service Discovery

Implementa um sistema de registro de serviços onde aplicações podem registrar seus endpoints e outros serviços podem descobrir estas instâncias.

### 4. Locks Distribuídos

Demonstra como usar o ETCD para implementar locks distribuídos, permitindo que múltiplas instâncias de uma aplicação coordenem o acesso a recursos compartilhados.

### 5. Prefixos Hierárquicos

Utiliza prefixos para organizar dados de forma hierárquica:
- `/users/*` - Dados de usuários
- `/config/app/*` - Configurações da aplicação
- `/services/*` - Serviços registrados
- `/locks/*` - Locks distribuídos

---

## Vantagens do ETCD

- **Consistência forte**: Garante leitura consistente após escrita
- **Distribuído**: Tolera falhas em alguns nós
- **Observável**: Suporta watching de chaves para notificações em tempo real
- **Seguro**: Suporta autenticação e TLS
- **Simples**: API REST e gRPC fáceis de usar

## Limitações e Considerações

- O ETCD não é otimizado para grandes volumes de dados
- Não possui recursos avançados de busca como bancos relacionais
- Buscas por conteúdo requerem filtragem local
- Ideal para metadados, configurações e coordenação distribuída

## Materiais

- [Documentação - ETCD](https://etcd.io/docs/)
- [Documentação - Flask](https://flask.palletsprojects.com/)
- [Documentação - python-etcd3](https://python-etcd3.readthedocs.io/)
