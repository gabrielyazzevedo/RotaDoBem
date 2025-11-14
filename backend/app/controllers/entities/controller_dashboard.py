# -*- coding: utf-8 -*-

from app.config.database import connect_db
from app.models.entities.model_usuarioUnificado import RoleEnum
from app.models.entities.model_rota import StatusRotaEnum 
import pymongo

def get_dashboard_stats():
    """
    Busca estatísticas-chave da aplicação diretamente do DB para eficiência.
    """
    try:
        db = connect_db()
        
        total_doacoes = db.doacoes.count_documents({})
        
        total_motoristas = db.usuarios.count_documents(
            {"role": RoleEnum.MOTORISTA.value}
        )
        
        rotas_pendentes = db.rotas.count_documents(
            {"status": StatusRotaEnum.PENDENTE.value}
        )
        
        stats = {
            "doacoes": total_doacoes,
            "motoristas": total_motoristas,
            "rotas_pendentes": rotas_pendentes
        }
        
        return stats, None

    except Exception as e:
        return None, f"Erro ao buscar estatísticas: {str(e)}"