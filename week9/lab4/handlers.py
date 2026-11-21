def v1_create_order(body):
    return {
        "order_id": "v1_1001",
        "status": "created",
        "version": "v1"
    }

def v2_create_order(body):
    return {
        "order_id": "v2_1001",
        "status": "created_v2",
        "version": "v2"
    }