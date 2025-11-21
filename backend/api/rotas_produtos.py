from fastapi import APIRouter
import pandas as pd
from backend.recomendador.engine import recomendar_por_cpf

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.get("/padronizados")
def listar_produtos():
    df = pd.read_csv("dataset/standardized/produtos_padronizados.csv")
    return df.to_dict(orient="records")

@router.get("/{pid}")
def obter_produto(pid: str):
    df = pd.read_csv("dataset/standardized/produtos_padronizados.csv")
    item = df[df["id"] == pid]
    return item.to_dict(orient="records")


@router.get("/recomendar/{cpf}")
def recomendar(cpf: str, k: int = 5):
    resultado = recomendar_por_cpf(cpf, top_k=k)

    return {
        "cpf": cpf,
        "total_recomendacoes": len(resultado),
        "recomendacoes": resultado
    }
