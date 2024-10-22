from typing import List
import discord
from .utils import Utils

class Embed():
    def __init__(self) -> None:
        self.utils = Utils()

    def mission_embed(self, mestre: discord.Member, rank: str, title: str, resumo: str, data_hora: str) -> discord.Embed:
        reward = self.utils.rank_to_reward(rank)

        embed = discord.Embed(title=title, description=resumo)
        embed.color = 0xff0000
        embed.add_field(name="Dificuldade", value=rank, inline=True)
        embed.add_field(name="Mestre", value=mestre.mention, inline=True)
        embed.add_field(name="Recompensa", value=reward, inline=False)
        embed.add_field(name="**Data/Hora**", value=data_hora, inline=False)

        return embed

    def rolls_embed(self, user: discord.Member, rolls: list[int], success: int, result: str, critical_count: int) -> discord.Embed:
        embed = discord.Embed(title=f"Rolagens de {user.display_name}")
        embed.color = 0x000000
        embed.add_field(name="**Rolagens**", value=', '.join([str(roll) for roll in rolls]), inline=False)

        if success > 0:
            embed.add_field(name="**Sucessos**", value=success, inline=False)
        elif result == "Falha crítica":
            embed.add_field(name="**Falha crítica!**", value="Putz...", inline=False)
        else:
            embed.add_field(name="**Falha!**", value="", inline=False)

        if critical_count > 0:
            embed.add_field(name="**Número de críticos**", value=critical_count, inline=True)

        return embed

    def ping_embed(self, latency: float, commands_synced: int) -> discord.Embed:
        embed = discord.Embed(title="Sync and Ping")
        embed.color = 0x000000
        embed.add_field(name="**Latência**", value=f"{latency:.2f}ms", inline=False)
        embed.add_field(name="**Comandos sincronizados**", value=commands_synced, inline=False)

        return embed

    def feature_check_embed(self, is_admin: bool, is_guild_server: bool) -> discord.Embed:
        embed = discord.Embed(title="Funções disponíveis")
        embed.color = 0x008000

        if is_admin:
            embed.add_field(name="**Funções de administrador**", value="Disponíveis", inline=False)
        else:
            embed.add_field(name="**Funções de administrador**", value="Indisponíveis", inline=False)

        if is_guild_server:
            embed.add_field(name="**Funções do servidor de guilda**", value="Disponíveis", inline=False)
        else:
            embed.add_field(name="**Funções do servidor de guilda**", value="Indisponíveis", inline=False)

        embed.add_field(name="**Rolagens de Parabellum**", value="Disponível", inline=False)

        return embed

    def mission_success_embed(self, rank: str, jogadores: List[discord.Member]) -> discord.Embed:
        reward = self.utils.rank_to_reward(rank)

        jogadores = [jogador for jogador in jogadores if jogador]

        embed = discord.Embed(title="Missão concluída!")
        embed.color = 0x008000
        embed.add_field(name="**Dificuldade**", value=rank, inline=False)
        embed.add_field(name="**Jogadores**", value=' '.join([jogador.mention for jogador in jogadores]), inline=False)
        embed.add_field(name="**Recompensa**", value=reward, inline=False)

        return embed

    def mission_failed_embed(self, rank: str, jogadores: List[discord.Member]) -> discord.Embed:
        reward = self.utils.rank_to_reward_half(rank)

        jogadores = [jogador for jogador in jogadores if jogador]

        embed = discord.Embed(title="Missão falhou!")
        embed.color = 0xff0000
        embed.add_field(name="**Dificuldade**", value=rank, inline=False)
        embed.add_field(name="**Jogadores**", value=' '.join([jogador.mention for jogador in jogadores]), inline=False)
        embed.add_field(name="**Recompensa (pela metade)**", value=reward, inline=False)

        return embed
