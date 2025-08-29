import json
from typing import List, Dict, Optional
import datetime
import calendar

class AssinanteService:
    def __init__(self, arquivo_path: str = "mdl_2.json"):
        self.arquivo_path = arquivo_path

    def carregar_assinantes(self) -> List[Dict]:
        """Carrega assinantes do arquivo JSON"""
        try:
            with open(self.arquivo_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_assinantes(self, assinantes: List[Dict]):
        """Salva assinantes no arquivo JSON"""
        with open(self.arquivo_path, "w", encoding="utf-8") as f:
            json.dump(assinantes, f, ensure_ascii=False, indent=2)

    def buscar_por_id(self, assinante_id: int) -> Optional[Dict]:
        """Busca assinante por ID"""
        assinantes = self.carregar_assinantes()
        return next((a for a in assinantes if a["id"] == assinante_id), None)

    def proximo_id(self) -> int:
        """Encontra o próximo ID disponível"""
        assinantes = self.carregar_assinantes()
        return 1 if not assinantes else max(a["id"] for a in assinantes) + 1

    def criar_assinante(self, nome: str, email: str, celular: str, mesas: List[int], 
                       ultimo_mes_pago: str, forma_pagamento: str, valor: str) -> Dict:
        """Cria um novo assinante"""
        assinantes = self.carregar_assinantes()
        novo_id = self.proximo_id()
        
        novo_assinante = {
            "id": novo_id,
            "nome": nome,
            "email": email if email.strip() else "",
            "celular": celular,
            "mesas": mesas,
            "ultimo_mes_pago": ultimo_mes_pago,
            "forma_pagamento": forma_pagamento,
            "valor": valor
        }
        
        assinantes.append(novo_assinante)
        self.salvar_assinantes(assinantes)
        return novo_assinante
    
    def atualizar_assinante(self, assinante_id: int, **kwargs) -> Optional[Dict]:
        """Atualiza um assinante existente"""
        assinantes = self.carregar_assinantes()
        
        for i, assinante in enumerate(assinantes):
            if assinante["id"] == assinante_id:
                for key, value in kwargs.items():
                    if value is not None:
                        assinante[key] = value
                self.salvar_assinantes(assinantes)
                return assinante
        
        return None
    
    def verificar_atraso(self, ultimo_mes_pago: str, nome: str = "") -> bool:
        """Verifica se um assinante está em atraso"""
        try:
            # Parse manual da data no formato DD/MM/YYYY
            data_str = ultimo_mes_pago.strip()
            if "/" in data_str:
                parts = data_str.split("/")
                if len(parts) == 3:
                    dia = int(parts[0])
                    mes = int(parts[1])
                    ano = int(parts[2])
                    data_pagamento = datetime.datetime(ano, mes, dia)
                else:
                    return False
            else:
                return False

            # Determinar se é assinante semestral (tem "(s)" no nome)
            is_semestral = "(s)" in nome.lower()
            meses_para_adicionar = 6 if is_semestral else 1

            # Calcula o próximo vencimento
            if data_pagamento.month + meses_para_adicionar > 12:
                # Se ultrapassar dezembro, vai para o próximo ano
                new_year = data_pagamento.year + ((data_pagamento.month + meses_para_adicionar - 1) // 12)
                new_month = ((data_pagamento.month + meses_para_adicionar - 1) % 12) + 1
                try:
                    proximo_vencimento = data_pagamento.replace(year=new_year, month=new_month)
                except ValueError:  # Caso do dia 31 em mês com 30 dias
                    last_day = calendar.monthrange(new_year, new_month)[1]
                    proximo_vencimento = datetime.datetime(new_year, new_month, min(data_pagamento.day, last_day))
            else:
                new_month = data_pagamento.month + meses_para_adicionar
                try:
                    proximo_vencimento = data_pagamento.replace(month=new_month)
                except ValueError:  # Caso do dia 31 em mês com 30 dias
                    last_day = calendar.monthrange(data_pagamento.year, new_month)[1]
                    proximo_vencimento = datetime.datetime(data_pagamento.year, new_month, min(data_pagamento.day, last_day))

            # Verifica se já passou do vencimento
            hoje = datetime.datetime.now()
            return hoje > proximo_vencimento
        except:
            return False
    
    def listar_atrasados(self) -> List[Dict]:
        """Lista todos os assinantes em atraso"""
        assinantes = self.carregar_assinantes()
        atrasados = []
        
        for assinante in assinantes:
            ultimo_mes_pago = assinante.get("ultimo_mes_pago", "")
            nome = assinante.get("nome", "")
            if self.verificar_atraso(ultimo_mes_pago, nome):
                atrasados.append(assinante)
        
        return atrasados
