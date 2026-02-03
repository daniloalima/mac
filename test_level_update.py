#!/usr/bin/env python3
"""Script de teste para a função de atualização de níveis"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importa apenas as funções necessárias
import random
import json
from typing import List

class TestUtils:
    """Versão simplificada de Utils apenas para testes"""
    
    def level_to_xp(self, level: int) -> int:
        """Mapeia níveis de 1 a 20 para os valores de XP correspondentes"""
        xp_table = {
            1: 5, 2: 7, 3: 10, 4: 12, 5: 15,
            6: 18, 7: 22, 8: 26, 9: 30, 10: 35,
            11: 40, 12: 45, 13: 50, 14: 55, 15: 60,
            16: 70, 17: 80, 18: 90, 19: 100, 20: 120
        }
        return xp_table.get(level, 0)
    
    def calculate_level_from_xp(self, current_level: int, xp: int) -> tuple[int, int]:
        """Calcula o nível e XP restante baseado no XP total.
        Retorna (novo_nivel, xp_restante)"""
        level = current_level
        remaining_xp = xp
        
        # Upando recursivamente enquanto tiver XP suficiente e não atingir o nível máximo
        while level < 20:
            xp_needed = self.level_to_xp(level)
            if remaining_xp >= xp_needed:
                remaining_xp -= xp_needed
                level += 1
            else:
                break
        
        return level, remaining_xp

def test_calculate_level():
    """Testa o cálculo de nível baseado em XP"""
    utils = TestUtils()
    
    print("=== Teste de Cálculo de Nível ===\n")
    
    # Teste 1: Personagem nível 1 com 10 XP
    print("Teste 1: Nível 1 com 10 XP")
    level, xp = utils.calculate_level_from_xp(1, 10)
    print(f"Resultado: Nível {level}, XP restante: {xp}")
    print(f"Explicação: 10 XP - 5 XP (lvl 1→2) - 7 XP não dá, então fica lvl 2 com 5 XP\n")
    # Deveria dar: Nível 2, XP 5 (gastou 5 para subir de 1 para 2)
    
    # Teste 2: Personagem nível 1 com 100 XP
    print("Teste 2: Nível 1 com 100 XP")
    level, xp = utils.calculate_level_from_xp(1, 100)
    print(f"Resultado: Nível {level}, XP restante: {xp}\n")
    
    # Teste 3: Personagem nível 5 com 50 XP
    print("Teste 3: Nível 5 com 50 XP")
    level, xp = utils.calculate_level_from_xp(5, 50)
    print(f"Resultado: Nível {level}, XP restante: {xp}\n")
    
    # Teste 4: Personagem nível 19 com 200 XP
    print("Teste 4: Nível 19 com 200 XP")
    level, xp = utils.calculate_level_from_xp(19, 200)
    print(f"Resultado: Nível {level}, XP restante: {xp}")
    print(f"Nota: Nível máximo é 20\n")
    
    # Mostra a tabela de XP
    print("=== Tabela de XP por Nível ===")
    for lvl in range(1, 21):
        xp_needed = utils.level_to_xp(lvl)
        print(f"Nível {lvl:2d}: precisa {xp_needed:3d} XP para upar")

if __name__ == "__main__":
    test_calculate_level()
