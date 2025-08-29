import json
from typing import List, Dict, Optional

class MesaService:
    def __init__(self, arquivo_path: str = "mesas.json"):
        self.arquivo_path = arquivo_path
    
    def carregar_mesas(self) -> List[Dict]:
        """Carrega mesas do arquivo JSON"""
        try:
            with open(self.arquivo_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def salvar_mesas(self, mesas: List[Dict]):
        """Salva mesas no arquivo JSON"""
        with open(self.arquivo_path, "w", encoding="utf-8") as f:
            json.dump(mesas, f, ensure_ascii=False, indent=2)
    
    def buscar_por_id(self, mesa_id: int) -> Optional[Dict]:
        """Busca mesa por ID"""
        mesas = self.carregar_mesas()
        return next((m for m in mesas if m["id"] == mesa_id), None)
    
    def proximo_id(self) -> int:
        """Encontra o próximo ID disponível"""
        mesas = self.carregar_mesas()
        return 1 if not mesas else max(m["id"] for m in mesas) + 1
    
    def criar_mesa(self, mestre_name: str, mestre_id: int, nome: str, sistema: str, dia_semana: str, frequencia: str) -> Dict:
        """Cria uma nova mesa"""
        mesas = self.carregar_mesas()
        novo_id = self.proximo_id()
        
        nova_mesa = {
            "id": novo_id,
            "mestre": mestre_name,
            "mestre_id": mestre_id,
            "nome": nome,
            "sistema": sistema,
            "dia_semana": dia_semana,
            "frequencia": frequencia
        }
        
        mesas.append(nova_mesa)
        self.salvar_mesas(mesas)
        return nova_mesa
    
    def atualizar_mesa(self, mesa_id: int, **kwargs) -> Optional[Dict]:
        """Atualiza uma mesa existente"""
        mesas = self.carregar_mesas()
        
        for i, mesa in enumerate(mesas):
            if mesa["id"] == mesa_id:
                for key, value in kwargs.items():
                    if value is not None:
                        mesa[key] = value
                self.salvar_mesas(mesas)
                return mesa
        
        return None
