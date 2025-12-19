from fastapi import APIRouter
from storage.mongo import db

router = APIRouter()

@router.get("/payer/{payer_vpa}")
def payer_network(payer_vpa: str):
    edges = db["upi_graph_edges"].find(
        {"payer_vpa": payer_vpa},
        {"_id": 0}
    )

    return {
        "payer_vpa": payer_vpa,
        "connections": list(edges)
    }
