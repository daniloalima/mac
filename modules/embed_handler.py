import discord

def mission_embed(mestre: discord.Member, rank: str, title: str, resumo: str, data_hora: str) -> discord.Embed:

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
    embed.add_field(name="Dificuldade", value=rank)
    embed.add_field(name="Mestre", value=mestre.mention)
    embed.add_field(name="Recompensa", value=reward)
    embed.add_field(name="**Data/Hora**", value=data_hora)

    return embed
