# SmartOrder — Contratos das APIs

**Versão:** 1.0  
**Arquitetura:** SOA — Service-Oriented Architecture  
**Comunicação:** HTTP + REST + JSON

## 1. Objetivo

Este documento define os contratos de comunicação entre os serviços do SmartOrder.

Todos os serviços e consumidores devem respeitar os métodos HTTP, endpoints, formatos de dados e respostas estabelecidos aqui.

Nenhum endpoint deve ser alterado sem atualizar este documento e os componentes que dependem dele.

## 2. Padrões gerais

- Formato de comunicação: JSON.
- Codificação: UTF-8.
- Protocolo durante o desenvolvimento: HTTP.
- Cabeçalho para envio de JSON: `Content-Type: application/json`.
- Os identificadores dos produtos serão strings.
- Os identificadores dos pedidos serão numéricos.
- Datas e horários, quando utilizados, devem seguir o padrão ISO 8601.
- Os serviços devem retornar códigos HTTP adequados para indicar sucesso ou falha.

## 3. Mapa de endpoints

| Serviço | Método | Endpoint | Função |
|---|---|---|---|
| Java | GET | `/api/produtos` | Listar produtos e estoque |
| Java | POST | `/api/pedidos` | Criar pedido |
| Java | GET | `/api/pedidos` | Listar pedidos |
| Java | GET | `/api/pedidos/{id}` | Consultar pedido |
| Java | PATCH | `/api/pedidos/{id}/status` | Atualizar status |
| Python | GET | `/api/estoque` | Consultar estoque |
| Python | POST | `/api/estoque/reservas` | Reservar produtos |
| Node.js | POST | `/api/notificacoes` | Registrar notificação |
| Node.js | GET | `/api/notificacoes` | Listar notificações |
| Todos | GET | `/health` | Verificar funcionamento do serviço |

## 4. Java — Order Service

**Porta:** 8080  
**Responsabilidade:** gerenciar pedidos e coordenar a comunicação com os demais serviços.

### 4.1. Listar produtos

`GET /api/produtos`

Retorna os produtos disponíveis e suas quantidades em estoque. O Java consulta as informações do serviço Python.

**Resposta — 200 OK**

```json
{
  "produtos": [
    {
      "id": "hamburguer",
      "nome": "Hambúrguer",
      "preco": 25.00,
      "estoque": 15
    },
    {
      "id": "pizza",
      "nome": "Pizza",
      "preco": 40.00,
      "estoque": 10
    },
    {
      "id": "refrigerante",
      "nome": "Refrigerante",
      "preco": 7.00,
      "estoque": 30
    }
  ]
}
```

### 4.2. Criar pedido

`POST /api/pedidos`

Recebe os dados de um pedido, verifica os produtos e solicita a reserva do estoque ao Python.

**Requisição**

```json
{
  "cliente": "Pedro",
  "items": [
    {
      "produtoId": "hamburguer",
      "quantidade": 2
    }
  ]
}
```

**Resposta — 201 Created**

```json
{
  "id": 1001,
  "cliente": "Pedro",
  "items": [
    {
      "produtoId": "hamburguer",
      "quantidade": 2,
      "precoUnitario": 25.00
    }
  ],
  "total": 50.00,
  "status": "CONFIRMADO"
}
```

Após confirmar o pedido, o Java solicita ao Node.js o registro de uma notificação.

### 4.3. Listar pedidos

`GET /api/pedidos`

Retorna todos os pedidos registrados.

**Resposta — 200 OK**

```json
{
  "pedidos": [
    {
      "id": 1001,
      "cliente": "Pedro",
      "total": 50.00,
      "status": "CONFIRMADO"
    }
  ]
}
```

### 4.4. Consultar pedido

`GET /api/pedidos/{id}`

Exemplo: `GET /api/pedidos/1001`

Retorna os detalhes de um pedido específico.

**Resposta — 200 OK**

Retorna o objeto completo do pedido, conforme o formato definido na seção 4.2.

### 4.5. Atualizar status

`PATCH /api/pedidos/{id}/status`

Atualiza parcialmente o status de um pedido.

**Requisição**

```json
{
  "status": "EM_PREPARACAO"
}
```

**Resposta — 200 OK**

```json
{
  "id": 1001,
  "status": "EM_PREPARACAO",
  "mensagem": "Status atualizado"
}
```

Status permitidos:

- `PENDENTE`
- `CONFIRMADO`
- `EM_PREPARACAO`
- `PRONTO`
- `CANCELADO`

## 5. Python — Inventory Service

**Porta:** 5000  
**Responsabilidade:** consultar e controlar a disponibilidade dos produtos.

### 5.1. Consultar estoque

`GET /api/estoque`

**Resposta — 200 OK**

```json
{
  "estoque": [
    {
      "produtoId": "hamburguer",
      "quantidade": 15
    },
    {
      "produtoId": "pizza",
      "quantidade": 10
    },
    {
      "produtoId": "refrigerante",
      "quantidade": 30
    }
  ]
}
```

### 5.2. Reservar produtos

`POST /api/estoque/reservas`

Recebe uma solicitação de reserva e verifica se há quantidade suficiente.

**Requisição**

```json
{
  "orderId": 1001,
  "items": [
    {
      "produtoId": "hamburguer",
      "quantidade": 2
    }
  ]
}
```

**Resposta — 200 OK**

```json
{
  "sucesso": true,
  "orderId": 1001,
  "mensagem": "Estoque reservado"
}
```

**Resposta — 409 Conflict**

Utilizada quando não há estoque suficiente.

```json
{
  "sucesso": false,
  "mensagem": "Estoque insuficiente"
}
```

O `orderId` deve identificar a reserva. Se a mesma solicitação for repetida, o serviço não deve descontar o estoque novamente.

## 6. Node.js — Notification Service

**Porta:** 3000  
**Responsabilidade:** registrar e disponibilizar notificações relacionadas aos pedidos.

### 6.1. Registrar notificação

`POST /api/notificacoes`

**Requisição**

```json
{
  "orderId": 1001,
  "cliente": "Pedro",
  "status": "CONFIRMADO",
  "mensagem": "Seu pedido foi confirmado!"
}
```

**Resposta — 201 Created**

```json
{
  "sucesso": true,
  "mensagem": "Notificação registrada"
}
```

### 6.2. Listar notificações

`GET /api/notificacoes`

Retorna as notificações registradas.

**Resposta — 200 OK**

```json
{
  "notificacoes": [
    {
      "orderId": 1001,
      "cliente": "Pedro",
      "status": "CONFIRMADO",
      "mensagem": "Seu pedido foi confirmado!"
    }
  ]
}
```

## 7. Verificação de funcionamento

Todos os serviços devem disponibilizar:

`GET /health`

Exemplo de resposta:

```json
{
  "status": "UP",
  "servico": "inventory-service"
}
```

Cada serviço deve retornar seu próprio nome e estado de funcionamento.

## 8. Códigos HTTP padronizados

| Código | Significado | Situação |
|---|---|---|
| 200 | OK | Operação realizada |
| 201 | Created | Recurso criado |
| 400 | Bad Request | Dados inválidos |
| 404 | Not Found | Recurso inexistente |
| 409 | Conflict | Conflito ou estoque insuficiente |
| 500 | Internal Server Error | Erro interno |
| 503 | Service Unavailable | Serviço indisponível |

Quando houver erro, os serviços devem retornar uma resposta JSON com uma mensagem explicativa.

Exemplo:

```json
{
  "erro": "ESTOQUE_INSUFICIENTE",
  "mensagem": "Não há quantidade suficiente para o produto solicitado."
}
```

## 9. Regras de integração

1. O frontend realiza as operações de pedidos por meio do Java.
2. O Java consulta o Python para obter informações de estoque.
3. O Java solicita ao Python a reserva dos produtos durante a criação de um pedido.
4. O Java solicita ao Node.js o registro das notificações.
5. A confirmação de um pedido depende do sucesso da reserva de estoque.
6. Uma falha no serviço de notificações não deve desfazer um pedido já confirmado.
7. O identificador do pedido deve ser utilizado para relacionar as operações entre os serviços.
8. Qualquer alteração nos contratos deve ser documentada e comunicada antes de modificar os consumidores.

## 10. Observações técnicas

- Os serviços podem utilizar linguagens, bibliotecas e estruturas internas diferentes.
- A comunicação entre eles deve respeitar os contratos deste documento.
- Os serviços não devem depender diretamente das classes ou estruturas internas uns dos outros.
- Na versão inicial, os dados podem ser armazenados em memória. Portanto, serão perdidos quando o serviço for reiniciado.
- O projeto utiliza comunicação HTTP síncrona entre os serviços, sem mensageria nesta primeira versão.
