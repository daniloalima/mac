import discord

class Embed():
    def __init__(self) -> None:
        pass

    def mission_embed(self, mestre: discord.Member, rank: str, title: str, resumo: str, data_hora: str) -> discord.Embed:
        reward = ""

        if "Cobre" in rank:
            reward = "2 XP e 100 lascas de cobre"
        elif "Bronze" in rank:
            reward = "3 XP e 5 lascas de prata"
        elif "Prata" in rank:
            reward = "4 XP e 2 moedas de ouro"
        elif "Ouro" in rank:
            reward = "5 XP e 10 moedas de ouro"
        elif "Platina" in rank:
            reward = "6 XP e 50 moedas de ouro"
        else:
            reward = "Você é uma lenda, já está no topo."


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
