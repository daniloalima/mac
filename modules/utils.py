import random
from typing import List

import discord

class Utils():
    def __init__(self):
        self.success = 0
        self.critical_count = 0

    def convert_to_int_list(self, string: str) -> list[int]:
        return [int(item) for item in string.split(',')]

    def roll(self, dice_pool: int, dificulty: int, target: int = None):
        target = 8 if target is None else target
        result = ''
        rolls = []
        for _ in range(dice_pool - dificulty):
            roll_result = random.randint(1, 10)
            rolls.append(roll_result)
            if roll_result == 10:
                self.critical_count += 1
                rolls.extend(self.roll_again())
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

    def roll_again(self) -> list[int]:
        rolls = []
        while True:
            result = random.randint(1, 10)
            rolls.append(result)
            self.critical_count += 1 if result == 10 else 0
            if result != 10:
                break
        return rolls

    def check_admin(self, member: discord.Member, admin_roles: List[int]) -> bool:
        admin = False
        for role in member.roles:
            if role.id in admin_roles:
                admin = True
                break
        return admin

if __name__ == "__main__":
    utils = Utils()
    print(utils.roll(10, 3))