import random
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
            self.critical_count += 1 if result == 10 else 0
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

    def rank_to_reward(self, rank: str):
        if "Cobre" in rank:
            return "2 XP e 100 lascas de cobre"
        elif "Bronze" in rank:
            return "3 XP e 5 lascas de prata"
        elif "Prata" in rank:
            return "4 XP e 2 moedas de ouro"
        elif "Ouro" in rank:
            return "5 XP e 10 moedas de ouro"
        elif "Platina" in rank:
            return "6 XP e 50 moedas de ouro"
        else:
            return "Você é uma lenda, já tem tudo que precisa."

    def rank_to_reward_half(self, rank: str):
        if "Cobre" in rank:
            return "1 XP e 50 lascas de cobre"
        elif "Bronze" in rank:
            return "2 XP e 2 lascas de prata"
        elif "Prata" in rank:
            return "3 XP e 1 moeda de ouro"
        elif "Ouro" in rank:
            return "4 XP e 5 moedas de ouro"
        elif "Platina" in rank:
            return "5 XP e 25 moedas de ouro"
        else:
            return "Você é uma lenda, cumprir essa missão era sua obrigação..."

if __name__ == "__main__":
    utils = Utils()
    print(utils.roll(10, 0, 8, 7))