# Relatório da Prova Parcial - DevOps

**Curso:** Sistemas de Informação – DevOps  
**Professor:** André Insardi  
**Aluno:** Luigi Tomassone
**Data:** 06/10/2025

---

## 1) Construção da imagem e boas práticas (2,5 pts)

### a) Justificativa da imagem base e otimização

**Imagem base escolhida:** `python:3.11-slim`

**Justificativas:**
- **Tamanho otimizado:** A versão `slim` reduz significativamente o tamanho da imagem (aproximadamente 150MB vs 900MB da imagem completa)
- **Segurança:** Imagem oficial mantida pela Python Software Foundation
- **Estabilidade:** Python 3.11 oferece melhor performance e recursos modernos
- **Compatibilidade:** Suporta todas as dependências necessárias (Flask, psycopg2)

**Ordem das instruções para otimização de cache:**

1. **Instalação de dependências do sistema** (se necessário)
2. **Criação do usuário não-root** (segurança)
3. **Definição do diretório de trabalho**
4. **Cópia do requirements.txt** (otimização de cache)
5. **Instalação das dependências Python**
6. **Cópia do código da aplicação**
7. **Configuração de permissões e usuário**
8. **Exposição de portas e healthcheck**
9. **Comando de execução**

**Cache de camadas:**
- `requirements.txt` não muda → reutiliza camada (rápido)
- Código muda → reconstrói só a última camada
- `requirements.txt` muda → reconstrói tudo

**Boas práticas implementadas:**
- Usuário não-root para segurança
- Variáveis de ambiente para otimização Python
- Healthcheck para monitoramento
- `.dockerignore` para reduzir contexto de build
- Cache de dependências otimizado

### b) Comprovação de funcionamento

**Dockerfile implementado:**
```dockerfile
# Usar imagem oficial do Python 3.11 slim como base
FROM python:3.11-slim

# Definir variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para aproveitar cache do Docker
COPY app/requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ .

# Mudar propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta 5000
EXPOSE 5000

# Comando de saúde para verificar se a aplicação está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Comando para executar a aplicação
CMD ["python", "app.py"]
```

**Construção da imagem:**
```bash
docker build -t prova-devops-app .
```

**Resultado da construção:**
```
[+] Building 1.4s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.41kB
 => [internal] load metadata for docker.io/library/python:3.11-slim
 => [internal] load .dockerignore
 => => transferring context: 513B
 => [1/7] FROM docker.io/library/python:3.11-slim@sha256:9bffe4353b925a1656688797ebc68f9c525e79b1d377
 => [internal] load build context
 => => transferring context: 205B
 => CACHED [2/7] RUN groupadd -r appuser && useradd -r -g appuser appuser
 => CACHED [3/7] WORKDIR /app
 => CACHED [4/7] COPY app/requirements.txt .
 => CACHED [5/7] RUN pip install --no-cache-dir -r requirements.txt
 => CACHED [6/7] COPY app/ .
 => CACHED [7/7] RUN chown -R appuser:appuser /app
 => exporting to image
 => => exporting layers
 => => writing image sha256:ac4f60dfc6d0871b5738609d199c2a067ee0c4e6cf1d4296c559899e8e8d814a
 => => naming to docker.io/library/prova-devops-app
```

**Imagem criada com sucesso:**
```
REPOSITORY         TAG       IMAGE ID       CREATED          SIZE
prova-devops-app   latest    ac4f60dfc6d0   22 minutes ago   164MB
```

**Inspeção das camadas da imagem:**
```bash
docker history prova-devops-app:latest --format "table {{.CreatedBy}}\t{{.Size}}\t{{.CreatedAt}}"
```

**Resultado:**
```
CREATED BY                                      SIZE      CREATED AT
CMD ["python" "app.py"]                         0B        2025-10-06T19:44:18-03:00
HEALTHCHECK &{["CMD-SHELL" "python -c \"impo…   0B        2025-10-06T19:44:18-03:00
EXPOSE map[5000/tcp:{}]                         0B        2025-10-06T19:44:18-03:00
USER appuser                                    0B        2025-10-06T19:44:18-03:00
RUN /bin/sh -c chown -R appuser:appuser /app…   1.1kB     2025-10-06T19:44:18-03:00
COPY app/ . # buildkit                          1.1kB     2025-10-06T19:44:18-03:00
RUN /bin/sh -c pip install --no-cache-dir -r…   14MB      2025-10-06T19:44:18-03:00
COPY app/requirements.txt . # buildkit          36B       2025-10-06T19:44:15-03:00
WORKDIR /app                                    0B        2025-10-06T19:44:15-03:00
RUN /bin/sh -c groupadd -r appuser && userad…   4.31kB    2025-10-06T19:44:15-03:00
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBU…   0B        2025-10-06T19:44:15-03:00
```

---

## 2) Execução do container e integração com PostgreSQL (2,0 pts)

### a) Variáveis de ambiente e conexão ao banco

**Variáveis de ambiente configuradas:**
- `DB_HOST=db` (resolução de nome do container)
- `POSTGRES_DB=aula_prova`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=123456`
- `POSTGRES_PORT=5432`

**Estratégia de conexão:**
- Uso de variáveis de ambiente (não hardcoded)
- Resolução de nomes via rede Docker
- Healthcheck do PostgreSQL para garantir disponibilidade

### b) Mapeamento de portas e acesso

**Configuração de portas:**
- Aplicação Flask: `5001:5000` (host:container) - porta 5001 para evitar conflito com AirPlay
- PostgreSQL: `5432:5432` (host:container)

**Teste de acesso:**
```bash
# Acesso à rota principal
curl http://localhost:5001/
# Resposta: "Aplicação Flask no Docker – Prova de DevOps"

# Acesso à rota de produtos
curl http://localhost:5001/produtos
# Resposta: JSON com lista de produtos
```

### c) Evidências de funcionamento do banco

**Script de inicialização (`init.sql`):**
- Criação da tabela `produtos` com estrutura especificada
- Inserção de dados de exemplo
- Verificação de integridade

**Dados de teste inseridos:**
- Notebook Dell Inspiron: R$ 2.500,00
- Mouse Logitech: R$ 45,90
- Teclado Mecânico: R$ 120,50
- Monitor 24": R$ 800,00
- Webcam HD: R$ 150,75

**Teste de conectividade direta com PostgreSQL:**
```bash
docker exec prova_devops_db psql -U postgres -d aula_prova -c "SELECT COUNT(*) as total_produtos FROM produtos;"
```

**Resultado:**
```
 total_produtos 
----------------
              5
(1 row)
```

**Teste de conectividade da aplicação Flask:**
```bash
docker exec prova_devops_web python -c "import psycopg2; conn = psycopg2.connect(host='db', dbname='aula_prova', user='postgres', password='123456'); cur = conn.cursor(); cur.execute('SELECT nome, preco FROM produtos ORDER BY id'); rows = cur.fetchall(); print('Produtos no banco:'); [print(f'  - {row[0]}: R$ {row[1]}') for row in rows]; conn.close()"
```

**Resultado:**
```
Produtos no banco:
  - Notebook Dell Inspiron: R$ 2500.00
  - Mouse Logitech: R$ 45.90
  - Teclado Mecânico: R$ 120.50
  - Monitor 24": R$ 800.00
  - Webcam HD: R$ 150.75
```

---

## 3) Arquitetura multi-container com persistência e readiness (3,0 pts)

### a) Diagrama da arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Rede: app_network                        │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Container     │    │        Container                │ │
│  │      web        │    │           db                    │ │
│  │                 │    │                                 │ │
│  │  Flask App      │◄──►│  PostgreSQL 14                  │ │
│  │  Port: 5000     │    │  Port: 5432                     │ │
│  │                 │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                        │                        │
│           │                        │                        │
│           ▼                        ▼                        │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Host Port     │    │        Volume                   │ │
│  │     5001        │    │    postgres_data                │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Fluxo de comunicação:**
1. Cliente acessa `localhost:5001`
2. Host redireciona para container `web:5000`
3. Flask app conecta em `db:5432`
4. PostgreSQL responde com dados do volume persistente

**Mapeamento de portas:**
- Host:5001 → Container web:5000 (Flask App)
- Host:5432 → Container db:5432 (PostgreSQL)

### b) Estratégia para lidar com banco e evitar falhas

**Healthchecks implementados:**
- **PostgreSQL:** `pg_isready` verifica se o banco está pronto
- **Flask:** Teste HTTP na rota principal
- **Dependências:** `depends_on` com `condition: service_healthy`

**Estratégia de inicialização:**
1. PostgreSQL inicia primeiro
2. Script `init.sql` executa automaticamente
3. Healthcheck confirma banco pronto
4. Flask app inicia apenas após banco estar saudável
5. Retry automático em caso de falha

**Verificação dos healthchecks:**
```bash
docker inspect prova_devops_db --format='{{.State.Health.Status}}'
docker inspect prova_devops_web --format='{{.State.Health.Status}}'
```

**Resultado:**
```
healthy
healthy
```

### c) Comprovação de persistência

**Teste de persistência:**
```bash
# 1. Verificar dados iniciais
curl -s http://localhost:5001/produtos | python3 -m json.tool

# 2. Parar apenas o banco
docker-compose stop db

# 3. Reiniciar banco
docker-compose start db

# 4. Verificar se dados persistiram
curl -s http://localhost:5001/produtos | python3 -m json.tool
```

**Dados após reinicialização (persistência confirmada):**
```json
[
    {
        "id": 1,
        "nome": "Notebook Dell Inspiron",
        "preco": 2500.0
    },
    {
        "id": 2,
        "nome": "Mouse Logitech",
        "preco": 45.9
    },
    {
        "id": 3,
        "nome": "Teclado Mecânico",
        "preco": 120.5
    },
    {
        "id": 4,
        "nome": "Monitor 24\"",
        "preco": 800.0
    },
    {
        "id": 5,
        "nome": "Webcam HD",
        "preco": 150.75
    }
]
```

**Volume persistente:**
- Nome: `postgres_data`
- Localização: `/var/lib/postgresql/data`
- Sobrevive a reinicializações do container

---

## 4) Camadas, artefatos e manutenção do ambiente (2,5 pts)

### a) Geração de artefato portátil da imagem

**Comando para gerar artefato:**
```bash
# Construir a imagem
docker build -t prova-devops-app:latest .

# Salvar a imagem como arquivo tar
docker save prova-devops-app:latest -o prova-devops-app.tar
```

**Artefato gerado:**
```
-rw-------@ 1 luigi  staff   161M  6 Out 20:06 prova-devops-app.tar
```

**Como executar em outro host:**
```bash
# 1. Copiar o arquivo .tar para o novo host
scp prova-devops-app.tar user@novo-host:/caminho/destino/

# 2. Carregar a imagem no novo host
docker load -i prova-devops-app.tar

# 3. Executar com docker-compose
docker-compose up -d
```

**Teste de carregamento do artefato:**
```bash
docker rmi prova-devops-app:latest
docker load -i prova-devops-app.tar
docker run --rm -d --name teste-artefato -p 5002:5000 prova-devops-app:latest
curl http://localhost:5002/
docker stop teste-artefato
```

**Resultado:**
```
Aplicação Flask no Docker – Prova de DevOps
```

**Vantagens do artefato portátil:**
- **Independência de rede**: Não precisa acessar Docker Hub
- **Reprodutibilidade**: Mesma versão em qualquer ambiente
- **Segurança**: Controle total sobre a imagem
- **Performance**: Não depende de download de camadas

### b) Inspeção de camadas da imagem

**Comando para inspeção:**
```bash
docker history prova-devops-app:latest
```

**Otimizações implementadas:**
1. **Cache de dependências**: requirements.txt copiado antes do código
2. **Imagem slim**: Redução significativa de tamanho
3. **Usuário não-root**: Segurança aprimorada
4. **Healthcheck**: Monitoramento automático

### c) Inventário de recursos locais

**Comando para listar recursos:**
```bash
# Imagens
docker images

# Containers
docker ps -a

# Volumes
docker volume ls

# Redes
docker network ls
```

**Inventário atual:**
```
# Imagens
REPOSITORY         TAG         SIZE      CREATED AT
p1-web             latest      164MB     2025-10-06 19:44:18 -0300 -03
prova-devops-app   latest      164MB     2025-10-06 19:44:18 -0300 -03
postgres           14-alpine   269MB     2025-09-30 15:58:13 -0300 -03

# Containers
NAMES              IMAGE                STATUS                   PORTS
prova_devops_web   p1-web               Up 8 minutes (healthy)   0.0.0.0:5001->5000/tcp
prova_devops_db    postgres:14-alpine   Up 8 minutes (healthy)   0.0.0.0:5432->5432/tcp

# Volumes
DRIVER    VOLUME NAME        SCOPE
local     p1_postgres_data   local

# Redes
NAME              DRIVER    SCOPE
bridge            bridge    local
docker_gwbridge   bridge    local
host              host      local
ingress           overlay   swarm
none              null      local
p1_app_network    bridge    local
```

### d) Limpeza do ambiente sem apagar dados persistentes

**Estratégia de limpeza segura:**

**1. Limpeza de containers (preserva dados):**
```bash
# Parar todos os serviços
docker-compose down

# Remover apenas containers (volumes permanecem)
docker-compose rm

# Verificar volumes preservados
docker volume ls
```

**2. Limpeza de imagens não utilizadas:**
```bash
# Remover imagens órfãs (sem tags)
docker image prune

# Remover imagens específicas
docker rmi p1-web:latest

# Limpeza completa de imagens
docker image prune -a
```

**3. Limpeza de redes:**
```bash
# Remover redes não utilizadas
docker network prune

# Remover rede específica
docker network rm p1_app_network
```

**4. Limpeza de volumes (CUIDADO - apaga dados):**
```bash
# Listar volumes
docker volume ls

# Remover apenas volumes não utilizados
docker volume prune

# Remover volume específico (CUIDADO - perde dados)
docker volume rm p1_postgres_data
```

**Comandos de limpeza por categoria:**
```bash
# Limpeza completa (CUIDADO - remove TUDO)
docker system prune -a --volumes

# Limpeza segura (preserva volumes)
docker system prune -a

# Limpeza apenas containers parados
docker container prune
```

**Estratégia recomendada para limpeza:**
1. **Desenvolvimento**: `docker-compose down` (preserva dados)
2. **Teste**: `docker-compose down && docker system prune`
3. **Produção**: Nunca usar `--volumes` sem backup
4. **Manutenção**: Limpeza semanal com `docker system prune`

---

## 5) Evidências de Funcionamento

### a) Execução multi-container

**Docker-compose.yml:**
```yaml
version: '3.8'

services:
  # Serviço do banco de dados PostgreSQL
  db:
    image: postgres:14-alpine
    container_name: prova_devops_db
    environment:
      POSTGRES_DB: aula_prova
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456
      POSTGRES_PORT: 5432
    volumes:
      # Volume nomeado para persistência dos dados
      - postgres_data:/var/lib/postgresql/data
      # Script de inicialização
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d aula_prova"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # Serviço da aplicação Flask
  web:
    build: .
    container_name: prova_devops_web
    environment:
      DB_HOST: db
      POSTGRES_DB: aula_prova
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456
      POSTGRES_PORT: 5432
    ports:
      - "5001:5000"
    networks:
      - app_network
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

# Volumes nomeados para persistência
volumes:
  postgres_data:
    driver: local

# Rede personalizada para comunicação entre containers
networks:
  app_network:
    driver: bridge
```

**Iniciando aplicação multi-container:**
```bash
docker-compose up -d --build
```

**Resultado da execução:**
```
[+] Building 0.4s (13/13) FINISHED
 => [web internal] load build definition from Dockerfile
 => [web] exporting to image
 => => exporting layers
 => => writing image sha256:e261205c0228b32f74a96c74a2822ab762af9220629974365e22b339c2488053
 => => naming to docker.io/library/p1-web
[+] Running 3/3
 ✔ web                         Built
 ✔ Container prova_devops_db   Healthy
 ✔ Container prova_devops_web  Started
```

**Status dos containers:**
```
NAME               IMAGE                COMMAND                  SERVICE   CREATED          STATUS                    PORTS
prova_devops_db    postgres:14-alpine   "docker-entrypoint.s…"   db        19 minutes ago   Up 19 minutes (healthy)   0.0.0.0:5432->5432/tcp
prova_devops_web   p1-web               "python app.py"          web       19 minutes ago   Up 3 minutes (healthy)    0.0.0.0:5001->5000/tcp
```

### b) Teste dos endpoints da API

**Teste do endpoint principal:**
```bash
curl -v http://localhost:5001/
```

**Resposta:**
```
* Host localhost:5001 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:5001...
* Connected to localhost (::1) port 5001
> GET / HTTP/1.1
> Host: localhost:5001
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.3 Python/3.11.13
< Date: Mon, 06 Oct 2025 23:06:00 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 47
< Connection: close
< 
* Closing connection
```

**Teste do endpoint de produtos:**
```bash
curl -v http://localhost:5001/produtos
```

**Resposta:**
```
* Host localhost:5001 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:5001...
* Connected to localhost (::1) port 5001
> GET /produtos HTTP/1.1
> Host: localhost:5001
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.3 Python/3.11.13
< Date: Mon, 06 Oct 2025 23:06:02 GMT
< Content-Type: application/json
< Content-Length: 246
< Connection: close
< 
[{"id":1,"nome":"Notebook Dell Inspiron","preco":2500.0},{"id":2,"nome":"Mouse Logitech","preco":45.9},{"id":3,"nome":"Teclado Mec\u00e2nico","preco":120.5},{"id":4,"nome":"Monitor 24\"","preco":800.0},{"id":5,"nome":"Webcam HD","preco":150.75}]
* Closing connection
```

**Executando script de teste automatizado:**
```bash
python3 test_app.py
```

**Resultado dos testes automatizados:**
```
🚀 Iniciando testes da aplicação Flask...
==================================================
⏳ Aguardando aplicação inicializar...
✅ Health endpoint funcionando: Aplicação Flask no Docker – Prova de DevOps
✅ Produtos endpoint funcionando:
   Total de produtos: 5
   - Notebook Dell Inspiron: R$ 2500.0
   - Mouse Logitech: R$ 45.9
   - Teclado Mecânico: R$ 120.5
   - Monitor 24": R$ 800.0
   - Webcam HD: R$ 150.75
==================================================
🎉 Todos os testes passaram! Aplicação funcionando corretamente.
```

### c) Evidências de Logs de Conectividade

**Logs da aplicação Flask:**
```bash
docker-compose logs --tail=5 web
```

**Resultado:**
```
prova_devops_web  | 127.0.0.1 - - [06/Oct/2025 23:14:47] "GET / HTTP/1.1" 200 -
prova_devops_web  | 127.0.0.1 - - [06/Oct/2025 23:15:17] "GET / HTTP/1.1" 200 -
prova_devops_web  | 127.0.0.1 - - [06/Oct/2025 23:15:48] "GET / HTTP/1.1" 200 -
prova_devops_web  | 192.168.65.1 - - [06/Oct/2025 23:16:04] "GET / HTTP/1.1" 200 -
prova_devops_web  | 192.168.65.1 - - [06/Oct/2025 23:16:04] "GET /produtos HTTP/1.1" 200 -
```

### d) Evidências de Backup e Restauração

**Backup do volume PostgreSQL:**
```bash
docker run --rm -v p1_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
ls -lh postgres_backup.tar.gz
```

**Resultado:**
```
-rw-r--r--  1 luigi  staff   6,1M  6 Out 20:16 postgres_backup.tar.gz
```

### e) Evidências de Monitoramento

**Uso de espaço do sistema:**
```bash
docker system df
```

**Resultado:**
```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          3         2         433.4MB   164.2MB (37%)
Containers      2         2         63B       0B (0%)
Local Volumes   1         1         52.4MB    0B (0%)
Build Cache     120       0         1.189GB   1.189GB
```

---

## 6) Comandos de Execução Completos

### Inicialização do ambiente:
```bash
# 1. Construir e executar a aplicação
docker-compose up -d --build

# 2. Verificar status dos containers
docker-compose ps

# 3. Verificar logs
docker-compose logs -f
```

### Testes de funcionamento:
```bash
# 1. Testar endpoint principal
curl http://localhost:5001/

# 2. Testar endpoint de produtos
curl http://localhost:5001/produtos

# 3. Executar script de teste automatizado
python3 test_app.py
```

### Verificação de recursos:
```bash
# 1. Listar containers
docker ps

# 2. Listar volumes
docker volume ls

# 3. Listar redes
docker network ls

# 4. Verificar variáveis de ambiente
docker exec prova_devops_web env | grep -E "(DB_|POSTGRES_)"
```

### Limpeza do ambiente:
```bash
# 1. Parar aplicação (preserva dados)
docker-compose down

# 2. Limpeza completa (CUIDADO - remove dados)
docker-compose down -v

# 3. Limpeza de recursos não utilizados
docker system prune
```