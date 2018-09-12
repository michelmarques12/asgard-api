# Changelog

### 0.75.0
 * Atualização do flask para `0.12.4`, https://nvd.nist.gov/vuln/detail/CVE-2018-1000656

### 0.74.0
 * Adição do endpoint `/plugins` que mostra o status final de load dos plugins da API
 * Mudança na chave onde a exception de um request é logada
 * Fix no build da imagem docker para usar pipenv

### 0.73.0-rc1
 * Refactoring dos scripts que ligam o ambiente de dev local
 * Atualização da asgard SDK para 0.3.0-rc1
 * Atualização da asgard-api-plugin-metrics-mesos 0.8.0-rc1

### 0.71.0
 * Corrigido bug que afetava um GET em /v2/apps/ para uma conta vazia

### 0.70.0
 * Adição do filtro de compatibilidade entre UI 1.30 e Backend <= 1.4.x;
 * Remoção da key `secrets` de todos os JSONs

### 0.69.0
 * Atualizando asgard-api-plugin-mesos-metrics para 0.6.0

### 0.68.1
  - Gerando versão correta. A 0.68.0 foi gerada errado.

### 0.68.0
  - Criação de um cache client. Cache client não dá raise caso o redis esteja fora do ar. 
  - Criação dos endpoints para download de arquivos de uma task

### 0.67.0
  - Uso do `get_option` da asgard-api-sdk;
  - Melhoria no ambiente de dev. Agora temos toda a infra completa, com PgSQL com múltiplas contas.

### 0.66.0
  - Atualizando asgard-api-sdk==0.2.0
  - Atualizando mesos-metrics-api==0.5.0

### 0.65.0
  - Passamos um objeto logger para todos os plugins que são carregados no boot;
  - Ajustamos o loglevel de todos os loggers a partir de uma envvar: `ASGARD_LOGLEVEL`;

### 0.64.0
  - Atualização do plugin session-checker-plugin para não usar mais o objeto Sieve (e sim o objeto Bridge)

### 0.63.1
  - Correção para apps que tinham o nome contento a string `*versions/`. 

### 0.63.0
  - IN-2425 Implemntação da API de file read/download para podermos ver os logs de uma task pela API do Asgard
  - Script que ajuda a fazer um tail -f nos logs de uma app

### 0.62.0
  - IN-2451 Atualização do session-checker-plugin para 0.2.0 (para usar o request pipelines);
  - Essa versão da API só funciona com a versão da UI 0.12.0+. Pois a partir dessa versão já temos suporte a request pipeline.

### 0.61.0
  - IN-2434 Implementação da uma estrutura simples para plugins no backend
      > Adição do um primeiro plugin:  asgard-api-plugin-metrics-mesos==0.1.0

### 0.60.0
  - Mudança do versionamento para SemVer. Estávamos incrementando o `.patch` e não o `.minor`.
  - IN-2422 Fix no scale após edição da app e que todas as apps eram renovadas

### 0.0.59
  - Ativando suporte ao newrelic APM

### 0.0.58
  - IN-2407 Bugfix apps que continham em seu nome o valor de seu próprio namespace

### 0.0.57
  - Adicionando dump do schema do banco
  - Silenciando os logs do marathon-python

### 0.0.56
  - IN-2104/IN-2408 Suporte a múltiplos Marathons

### 0.0.55
  - IN-2362 Movendo o `merge_apps()` pra dentro do `.split()`
  - IN-2379 Major refacroting no pipeline de request/response. Agora os dois fluxos são atendidos pelo mesmo dispatch()

### 0.0.54
  - Atualizando session-checker-plugin para usar o ajaxWrapper de dentro do objeto Sieve.

### 0.0.53
  - Mudança no nome da imagem para `/sieve/infra/asgard-api`
  - IN-2404 Remove label traefik.backend para que não exista a possibilidade de duas apps terem o mesmo backend

### 0.0.52
  - IN-2354 Removendo deployments de outros namespaces
  - IN-2365 Filto que remove campos que o marathon nao aceita quando fazemos POST/PUT

### 0.0.51
  - IN-2344 Suporte ao endpoint /v2/tasks
  - IN-2355 Usando passgem por referencia nos filtros
  - IN-2356 Não passamos `original_*` para os métodos de response filters
  - IN-2357 Adiçao do AddURIFilter que adiciona a autenticação do docker registry
  - IN-2361 Mudando todas as chamdas de `().from_json()` para `.from_json()`

### 0.0.50
  - Implementção da possibilidade de remover campos que são multi-valor (constraints, labels, env, etc)

### 0.0.48/0.0.49
  - Suporte ao endpoint /v2/queue
  - Refactoring interno para generalizar o forma como pegamos o ID do resource sendo acessado

### 0.0.47
  - Removendo do response apps que não pertencem ao namespace atual (/v2/apps)
  - Separando erros de autenticação em HTTP 401 e erros não tratados em HTTP 500. O Stacktrace é retornado no response JSON.

### 0.0.46
  - BUGFIX: Apps que tinham a ultima parte do path repetidos retornavam 404

### 0.0.45
  - Implementação parcial do endpoint /v2/deployments. As apps do seu namespace já aparecem certo (sem o prefixo), mas ainda aparecem apps de outros namespaces.
  - Implementação do filtro que preenche a label de defaultscale.

### 0.0.44
  - Filtro que adiciona constrains mesos:LIKE:slave e workload:LIKE:general, caso não existam.

### 0.0.43
  - Atualizando plugin session-checker-plugin

### 0.0.42
  - Implementado response pipeline. Agora é possível modificar os responses devolvidos pelo marathon usando filtros
  - Immplementado suporte a GET/DELETE em /v2/groups/
  - Removido código que lidava com requests não autenticados. Agora a autenticção é sempre requerida;

### 0.0.41
  - Implementado lógica de troca de conta
  - Atualização do plugin session-checker-plugin, com a Dialog de troca de conta

### 0.0.40
  - Refactoring no AsgardApp

### 0.0.39
  - Suporte a request com lista no body;
  - Implementação do filtro que adiciona namespace
  - Desligando filtro de namespace, por enquanto.
  - Implementado um teste para ajudar a garantir que nenhum filtro ativo terá problemas com requests não-autenticados

### 0.0.38
  - BUGFIX: User do request sendo corretamente repassado para o dispatch
  - Filter para adicionar a costraint `owner:LIKE:<account.owner>`

### 0.0.37
  - Início do suporte a `account_id` nos requests
  - Necessidade de estar vinculado a pelo menos uma conta para que o request seja válido
  - Adicionando primeiro endpoint de métricas. ZK. Já feito com flask Blueprints.
  - Atualizando marathon-python para 0.9.2

### 0.0.36
  - Remoção do Fluxo velho de request
  - Remoção dos filtros: dns, constraint, defaultscale. Serão re-implementados eventualmente.
  - Criação do wrapper para o MarathonApp

### 0.0.35
  - Fitlro forcepull
  - Filtro trim

### 0.0.34
  - Major Refactoring do pipeline de filtros. Agora cada filtro recebe apenas uma app por vez, independente do request estar sendo feito em múltiplas apps
  - Mudança na interface dos filtros. Essa mudança é incompatível com os filtros velhos

### 0.0.33
  - Implementação do roteamento para o fluxo novo e fluxo velho. Isso depois será removido, quando tudo for fluxo novo.

### 0.0.32
  - Separando o mapeamento de todas as rotas da API. Isso vai permitir que possamos mexer nas rotas de forma individual

### 0.0.31
  - Removendo header Content-Encoding. Marathon 1.3.13 retorna os responses em formato gzip, mas o hollowman ainda nao trata isso.

### 0.0.30
  - Adicionando session-checker-plugin

### 0.0.29
  - Migração para python 3.6

### 0.0.28
  - Atualizando example-plugin. Corrigindo chamada à Dialog API.

### 0.0.27
  - Atualizando immage base para uwsgi/py27:0.0.12 (Log "JSON")

### 0.0.26
  - Adicionado lógica para dupla autenticação: Token JWT (com oauth2) e Token de usuário
  - Adicionadas novas configurações: HOLLOWMAN_DB_ECHO, HOLLOWMAN_ENFORCE_AUTH, HOLLOWMAN_DB_URL

### 0.0.25
  - Adicionadas rotas pra servir o código dos plugins para a UI
  - Atualização para imagem base alpine/py27/uwsgi20:0.0.11, por causa do `UWSGI_EXTRA_ARGS`
  - Necessidade de passar `UWSGI_EXTRA_ARGS="--static-map2 /static=/opt/app/"`
  - Adição de um plugin de exemplo
### 0.0.24
  - Migrando para Flask-OAuthlib
### 0.0.23
  - Adicionado todo o fluxo para autenticação oauth2, mas ainda não é obrigatório.

## Env vars
* ASGARD_CACHE_URL [required]: Enredeço do cache (Redis). No formato: `redis://<host>:<port>/<db>`
* MARATHON_CREDENTIALS [required] user:pass for the basic auth
* HOLLOWMAN_MARATHON_ADDRESS_INDEX [required] Where to connect to find Marathon api. List of Marathon IPs. <INDEX> starts at 0.
* HOLLOWMAN_MESOS_ADDRESS_INDEX [required] Where to connect to find Mesos API. List of Mesos IPs. <INDEX> starts at 0.
* ASGARD_CACHE_KEY_PREFIX: default `asgard-api/` Prefixo que será usado em todas as operações com o cache
* ASGARD_CACHE_DEFAULT_TIMEOUT default 60s; Tempo de expiração padrão das chaves de cache
* HOLLOWMAN_REDIRECT_ROOTPATH_TO: Env que diz para onde o usuario será redirecionado se acessar a raiz onde o hollowman está deployado. Defaults to `/v2/apps`
* HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID: ID da app Oauth2, registrado no console do Google
* HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET: Secret dessa app.
* HOLLOWMAN_SECRET_KEY: Secret usado pelo Flask
* HOLLOWMAN_REDIRECT_AFTER_LOGIN: URL pra onde o usuário será redirecionado após o fluxo do oauth2. O redirect é feito pra: `URL?jwt=<token_jwt>`
* HOLLOWMAN_DB_ECHO: Define se os logs do SQLAlchemy estão ligados: Valores possíveis: 1|0. Default 0
* HOLLOWMAN_DB_URL: URL completa (com user, pwd, host, schema) do banco de dados: Formato: `postgresql://<user>:<pwd>@<host>/<schema>`
* ASGARD_LOGLEVEL: String indicando o loglevel a ser usado. Pode ser INFO, ERROR, DEBUG, WARNING, etc.



## Evoluindo o banco de dados

Sempr que fizermos uma mudança no banco, vamos guardar o SQL na pasta `sql/`. Os arquivos têm nome prefixado por um número (`date +"%s"`),
pois isso indica a ordem em que deve ser rodados. Por enquanto vamos assim até migrar para um projeto que gerencie essas migrações.

Para pegar o SQL que o Alchemy gera para um model:
Abra o ipython com a env
>>> from sqlalchemy.schema import CreateTable
>>> from hollowman.models import <Model>
>>> from hollowman.models import engine
>>> print (CreateTable(Account.__table__).compile(engine))

## Opções específicas de filtros

Qualquer filtro pode ser desliagdo por app caso a app possua a label `hollowman.filter.<name>.disable=<anyvalue>`. Onde `<name>` é o
valor do atributo `name` da classe que implementa o filtro em questão.


Um filtro qualquer pode ser desabilitado **globalmente** usando a envvar: HOLLOWMAN_FILTER_<NAME>_DISABLE: "qualquer-valor".


A ausência da env ou da label significa que o filtro está ligado.

### Passando parametros adcionais para um filtro

É possível passar parametros abritrários para um filtro qualquer via envvar. O nome da env deve ser:

`HOLLOWMAN_FILTER_<FILTER>_PARAM_<OPTIONNAME>_<INDEX>` onde:

`<FILTER>` é o nome do filtro
`<OPTIONNAME>` e o nome do parametro
`<INDEX>` é um indice para quando precisamos passar uma lista



## Parametros por Filtro

### Constraint

O Filtro DNS recebe o parametro `BASECONSTRAINT`. Esse parametro diz quais constraints serão adicionadas a uma pp caso ela não tenha nenhuma. Isso significa que o nome da env é: `HOLLOWMAN_FILTER_CONSTRAINT_PARAM_BASECONSTRAINT_{0,1,2}`


## Como adicionar novos plugins para a UI


Para adicionar novos plugins o `main.js` do plugin deve ser comitado em `/static/plugins/<plugin-id>/main.js`
Alteramos o arquivo `app.py` e adicionamos uma nova chamada a `register_plugin(<plugin-id>)`

Isso é o mínimo neceessário para que esse novo plugin esteja disponível para a UI.




## Running tests
`py.test --cov=hollowman --cov-report term-missing -v -s`
