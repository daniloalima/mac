import random
import csv
import json
from typing import List

import discord

class Utils():
    def __init__(self):
        self.success = 0
        self.critical_count = 0

    def convert_to_int_list(self, string: str) -> list[int]:
        return [int(item) for item in string.split(',')]

    def roll(self, dice_pool: int, dificulty: int = None, target: int = None, reroll: int = None):
        target = 8 if target is None else target
        dice_pool = 1 if dice_pool < 1 else dice_pool
        dificulty = 0 if dificulty is None else dificulty
        reroll = 10 if reroll is None else reroll
        dice_range = dice_pool - dificulty
        dice_range = max(dice_range, 1)
        result = ''
        rolls = []
        for _ in range(dice_range):
            roll_result = random.randint(1, 10)
            rolls.append(roll_result)
            if reroll is not 0 and roll_result >= reroll:
                self.critical_count += 1
                rolls.extend(self.roll_again(reroll))
        rolls.sort(reverse=True)
        for roll in rolls:
            if roll >= target:
                self.success += 1

        if self.success >= 1:
            result = 'Sucesso'
        elif self.success == 0 and 1 in rolls:
            result = 'Falha crítica'
        else:
            result = 'Falha'

        success = self.success
        critical_count = self.critical_count

        self.success = 0
        self.critical_count = 0

        return rolls, success, result, critical_count

    def roll_again(self, reroll) -> list[int]:
        rolls = []
        while True:
            result = random.randint(1, 10)
            rolls.append(result)
            self.critical_count += 1 if result >= reroll else 0
            if result < reroll:
                break
        return rolls

    def check_admin(self, member: discord.Member, admin_roles: List[int]) -> bool:
        admin = False
        for role in member.roles:
            if role.id in admin_roles:
                admin = True
                break
        return admin

    def level_to_xp(self, level: int) -> int:
        """Mapeia níveis de 1 a 20 para os valores de XP correspondentes"""
        xp_table = {
            1: 5, 2: 7, 3: 10, 4: 12, 5: 15,
            6: 18, 7: 22, 8: 26, 9: 30, 10: 35,
            11: 40, 12: 45, 13: 50, 14: 55, 15: 60,
            16: 70, 17: 80, 18: 90, 19: 100, 20: 120
        }
        return xp_table.get(level, 0)

    def level_to_gold(self, level: int) -> int:
        gold_table = {
            1: 50, 2: 75, 3: 100, 4: 150, 5: 200,
            6: 250, 7: 300, 8: 400, 9: 500, 10: 650,
            11: 800, 12: 1000, 13: 1200, 14: 1500, 15: 2000,
            16: 2500, 17: 3000, 18: 4000, 19: 5000, 20: 6500
        }
        return gold_table.get(level, 0)

    def level_to_reward(self, level: int) -> str:
        xp = self.level_to_xp(level)
        gold = self.level_to_gold(level)
        return f"{xp} XP e {gold} moedas de ouro"

    def level_to_reward_half(self, level: int) -> str:
        xp = self.level_to_xp(level) // 2
        gold = self.level_to_gold(level) // 2
        return f"{xp} XP e {gold} moedas de ouro"

    def load_chars(self) -> List[dict]:
        """Carrega os dados dos personagens do arquivo chars.json"""
        try:
            with open('chars.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_chars(self, chars: List[dict]) -> bool:
        """Salva os dados dos personagens no arquivo chars.json"""
        try:
            with open('chars.json', 'w', encoding='utf-8') as f:
                json.dump(chars, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar chars.json: {e}")
            return False

    def find_char_by_player(self, player_id: int) -> dict:
        """Busca um personagem pelo ID do jogador"""
        chars = self.load_chars()
        for char in chars:
            if char.get('jogador') == player_id:
                return char
        return None

    def create_char(self, player_id: int, char_name: str) -> bool:
        """Cria um novo personagem"""
        chars = self.load_chars()
        
        # Verifica se o jogador já tem um personagem
        if self.find_char_by_player(player_id):
            return False
        
        new_char = {
            "jogador": player_id,
            "personagem": char_name,
            "dinheiro": 0,
            "xp": 0,
            "lvl": 1
        }
        
        chars.append(new_char)
        return self.save_chars(chars)

    def update_char(self, player_id: int, **kwargs) -> bool:
        """Atualiza dados de um personagem"""
        chars = self.load_chars()
        for i, char in enumerate(chars):
            if char.get('jogador') == player_id:
                for key, value in kwargs.items():
                    if key in ['personagem', 'dinheiro', 'xp', 'lvl']:
                        chars[i][key] = value
                return self.save_chars(chars)
        return False

    def delete_char(self, player_id: int) -> bool:
        """Remove um personagem"""
        chars = self.load_chars()
        chars = [char for char in chars if char.get('jogador') != player_id]
        return self.save_chars(chars)

    def add_char_rewards(self, player_id: int, xp: int, gold: int) -> bool:
        """Adiciona recompensas (XP e ouro) a um personagem"""
        char = self.find_char_by_player(player_id)
        if not char:
            return False
        
        new_xp = char.get('xp', 0) + xp
        new_gold = char.get('dinheiro', 0) + gold
        
        # Calcula novo nível baseado no XP total (implementação simples)
        new_level = min(20, max(1, (new_xp // 100) + 1))
        
        return self.update_char(player_id, xp=new_xp, dinheiro=new_gold, lvl=new_level)

    def csv_para_json_mdl(self, csv_path="mdl.csv", json_path="mdl.json", id_inicial=9):
        """
        Converte o arquivo mdl.csv fornecido para mdl.json no formato de assinantes.json,
        começando pelo id especificado. Campos não presentes no CSV ficam em branco.
        """
        assinantes = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # Pula o cabeçalho
                for idx, row in enumerate(reader, start=id_inicial):
                    # Pula linhas vazias ou que começam com seções
                    if len(row) == 0 or (len(row) == 1 and row[0].strip() in ["VIP ESPECIAL", ""]):
                        continue

                    # Mapeamento dos campos do CSV para o JSON
                    nome = row[0].strip() if len(row) > 0 else ""
                    celular = row[1].strip() if len(row) > 1 else ""
                    ultimo_mes_pago = row[2].strip() if len(row) > 2 else ""
                    valor = row[3].strip() if len(row) > 3 else ""

                    # Os campos abaixo não existem no CSV, então ficam em branco
                    email = ""
                    mesas = []
                    forma_pagamento = ""

                    assinante = {
                        "id": idx,
                        "nome": nome,
                        "email": email,
                        "celular": celular,
                        "mesas": mesas,
                        "ultimo_mes_pago": ultimo_mes_pago,
                        "forma_pagamento": forma_pagamento,
                        "valor": valor
                    }
                    assinantes.append(assinante)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(assinantes, f, ensure_ascii=False, indent=2)
            print(f"Arquivo {json_path} gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao converter CSV para JSON: {e}")

    def remover_duplicados_assinantes(self, json_path="assinantes.json"):
        """
        Remove assinantes duplicados do JSON, verificando por nome e celular.
        Remove também assinantes com nome vazio.
        Reordena os IDs sequencialmente a partir de 1.
        Salva o arquivo sobrescrito e imprime os assinantes removidos.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except Exception as e:
            print(f"Erro ao ler o arquivo {json_path}: {e}")
            return

        vistos = set()
        unicos = []
        removidos = []

        for assinante in assinantes:
            nome = assinante.get("nome", "").strip()
            celular = assinante.get("celular", "").strip()
            chave = (nome.lower(), celular)
            if not nome:
                removidos.append(assinante)
            elif chave in vistos:
                removidos.append(assinante)
            else:
                vistos.add(chave)
                unicos.append(assinante)

        # Reordena os IDs sequencialmente a partir de 1
        for idx, assinante in enumerate(unicos, start=1):
            assinante["id"] = idx

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(unicos, f, ensure_ascii=False, indent=2)

        if removidos:
            print("Assinantes removidos por duplicidade ou nome vazio:")
            for a in removidos:
                print(f"ID: {a.get('id')} | Nome: {a.get('nome')} | Celular: {a.get('celular')}")
        else:
            print("Nenhum assinante duplicado ou com nome vazio encontrado.")

if __name__ == "__main__":
    utils = Utils()
    # utils.csv_para_json_mdl("mdl_2.csv", "mdl_2.json", 0)
    utils.remover_duplicados_assinantes("mdl_2.json")