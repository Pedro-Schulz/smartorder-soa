
products = {
    "CPK-001": {
        "id": "CPK-001",
        "nome": "Motor CPK Industrial 100",
        "marca": "CPK",
        "linha": "Industrial",
        "categoria": "Motor elétrico trifásico",
        "descricao": "Motor elétrico desenvolvido para aplicações industriais gerais, com foco em desempenho e operação contínua."
    },
    "CPK-002": {
        "id": "CPK-002",
        "nome": "Motor CPK Compact 50",
        "marca": "CPK",
        "linha": "Compact",
        "categoria": "Motor elétrico monofásico",
        "descricao": "Motor compacto indicado para equipamentos de pequeno e médio porte, com instalação simplificada."
    },
    "CPK-003": {
        "id": "CPK-003",
        "nome": "Motor CPK Power 200",
        "marca": "CPK",
        "linha": "Power",
        "categoria": "Motor elétrico trifásico",
        "descricao": "Motor desenvolvido para máquinas e equipamentos industriais que exigem maior capacidade de operação."
    }
}

# Quantidade disponível em estoque
stock = {
    "CPK-001": 15,
    "CPK-002": 10,
    "CPK-003": 30
}

# Reservas já processadas
reservations = {}


def get_all_products():
    return [
        {
            **product,
            "quantidade": stock[product_id]
        }
        for product_id, product in products.items()
    ]


def get_product(product_id):
    product = products.get(product_id)

    if product is None:
        return None

    return {
        **product,
        "quantidade": stock[product_id]
    }


def reserve_products(order_id, items):

    # Impede processar a mesma reserva novamente
    if order_id in reservations:
        if reservations[order_id] == items:
            return {
                "success": True,
                "message": "Reserva já processada",
                "orderId": order_id
            }, 200

        return {
            "success": False,
            "message": "Este pedido já possui outra reserva"
        }, 409

    # Primeiro verifica todos os motores
    for item in items:
        product_id = item["produtoId"]
        quantity = item["quantidade"]

        product = products.get(product_id)

        if product is None:
            return {
                "success": False,
                "message": f"Motor {product_id} não encontrado"
            }, 404

        if stock[product_id] < quantity:
            return {
                "success": False,
                "message": f"Estoque insuficiente para {product['nome']}"
            }, 409

    # Só altera o estoque depois de validar todos
    for item in items:
        product_id = item["produtoId"]
        quantity = item["quantidade"]

        stock[product_id] -= quantity

    # Registra a reserva
    reservations[order_id] = [
        dict(item) for item in items
    ]

    return {
        "success": True,
        "orderId": order_id,
        "message": "Motores reservados com sucesso"
    }, 201