from .base_command import BaseCommand
from ..embed_handler import Embed
import discord
from discord import app_commands
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CharCommands(BaseCommand):
    def __init__(self, utils, admin_roles, embed, guild_server_id):
        super().__init__(utils, admin_roles)
        self.embed = embed
        self.guild_server_id = guild_server_id

    def register_commands(self, tree: app_commands.CommandTree):
        tree.command(description="Criar um personagem para um jogador")(self.char_create)
        tree.command(description="Ver informações de um personagem")(self.char_info)
        tree.command(description="Atualizar dados de um personagem")(self.char_update)
        tree.command(description="Remover um personagem")(self.char_delete)
        tree.command(description="Adicionar recompensas a personagens")(self.char_add_rewards)

    @app_commands.describe(
        jogador="Membro do Discord que será dono do personagem",
        nome_personagem="Nome do personagem"
    )
    async def char_create(
        self,
        interaction: discord.Interaction,
        jogador: discord.Member,
        nome_personagem: str
    ):
        # Verifica se é admin
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Verifica se o jogador já tem um personagem
        existing_char = self.utils.find_char_by_player(jogador.id)
        if existing_char:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed(f"{jogador.mention} já possui um personagem: {existing_char.get('personagem', 'Sem nome')}"),
                ephemeral=True
            )
            return

        # Cria o personagem
        if self.utils.create_char(jogador.id, nome_personagem):
            await interaction.response.send_message(
                embed=self.embed.char_created_embed(nome_personagem, jogador)
            )
            logger.info(f"Personagem '{nome_personagem}' criado para {jogador.name} ({jogador.id})")
        else:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed("Erro ao criar personagem. Tente novamente."),
                ephemeral=True
            )

    @app_commands.describe(jogador="Membro do Discord para ver o personagem")
    async def char_info(
        self,
        interaction: discord.Interaction,
        jogador: Optional[discord.Member] = None
    ):
        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Se não foi especificado um jogador, usa o próprio usuário
        target_member = jogador if jogador else interaction.user

        char_data = self.utils.find_char_by_player(target_member.id)
        if not char_data:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed(f"{target_member.mention} não possui um personagem registrado."),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=self.embed.char_info_embed(char_data, target_member)
        )

    @app_commands.describe(
        jogador="Membro do Discord dono do personagem",
        nome="Novo nome do personagem",
        dinheiro="Nova quantidade de dinheiro",
        xp="Nova quantidade de XP",
        nivel="Novo nível"
    )
    async def char_update(
        self,
        interaction: discord.Interaction,
        jogador: discord.Member,
        nome: Optional[str] = None,
        dinheiro: Optional[int] = None,
        xp: Optional[int] = None,
        nivel: Optional[int] = None
    ):
        # Verifica se é admin
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Verifica se o jogador tem um personagem
        char_data = self.utils.find_char_by_player(jogador.id)
        if not char_data:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed(f"{jogador.mention} não possui um personagem registrado."),
                ephemeral=True
            )
            return

        # Prepara os dados a serem atualizados
        update_data = {}
        if nome is not None:
            update_data['personagem'] = nome
        if dinheiro is not None:
            update_data['dinheiro'] = max(0, dinheiro)  # Não permite valores negativos
        if xp is not None:
            update_data['xp'] = max(0, xp)
        if nivel is not None:
            update_data['lvl'] = max(1, min(20, nivel))  # Nível entre 1 e 20

        if not update_data:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed("Nenhum campo foi especificado para atualização."),
                ephemeral=True
            )
            return

        # Atualiza o personagem
        if self.utils.update_char(jogador.id, **update_data):
            updated_char = self.utils.find_char_by_player(jogador.id)
            await interaction.response.send_message(
                embed=self.embed.char_updated_embed(updated_char, jogador, update_data)
            )
            logger.info(f"Personagem de {jogador.name} ({jogador.id}) atualizado: {update_data}")
        else:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed("Erro ao atualizar personagem. Tente novamente."),
                ephemeral=True
            )

    @app_commands.describe(jogador="Membro do Discord para remover o personagem")
    async def char_delete(
        self,
        interaction: discord.Interaction,
        jogador: discord.Member
    ):
        # Verifica se é admin
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Verifica se o jogador tem um personagem
        char_data = self.utils.find_char_by_player(jogador.id)
        if not char_data:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed(f"{jogador.mention} não possui um personagem registrado."),
                ephemeral=True
            )
            return

        # Remove o personagem
        if self.utils.delete_char(jogador.id):
            embed = discord.Embed(title="Personagem removido!")
            embed.color = 0xff4444
            embed.add_field(name="**Personagem**", value=char_data.get('personagem', 'Sem nome'), inline=True)
            embed.add_field(name="**Jogador**", value=jogador.mention, inline=True)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Personagem '{char_data.get('personagem')}' de {jogador.name} ({jogador.id}) foi removido")
        else:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed("Erro ao remover personagem. Tente novamente."),
                ephemeral=True
            )

    @app_commands.describe(
        nivel="Nível da missão para calcular recompensas",
        jogador_1="Primeiro jogador",
        jogador_2="Segundo jogador", 
        jogador_3="Terceiro jogador",
        jogador_4="Quarto jogador (opcional)",
        jogador_5="Quinto jogador (opcional)",
        metade="Se true, dá metade das recompensas (para missões falhadas)"
    )
    async def char_add_rewards(
        self,
        interaction: discord.Interaction,
        nivel: int,
        jogador_1: discord.Member,
        jogador_2: discord.Member,
        jogador_3: discord.Member,
        jogador_4: Optional[discord.Member] = None,
        jogador_5: Optional[discord.Member] = None,
        metade: bool = False
    ):
        # Verifica se é admin
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Validar nível
        if nivel < 1 or nivel > 20:
            await interaction.response.send_message(
                embed=self.embed.char_error_embed("O nível deve estar entre 1 e 20."),
                ephemeral=True
            )
            return

        # Lista de jogadores
        jogadores = [jogador_1, jogador_2, jogador_3, jogador_4, jogador_5]
        jogadores = [j for j in jogadores if j is not None]

        # Calcula recompensas
        xp_reward = self.utils.level_to_xp(nivel)
        gold_reward = self.utils.level_to_gold(nivel)

        if metade:
            xp_reward = xp_reward // 2
            gold_reward = gold_reward // 2

        # Aplica recompensas
        success_count = 0
        results = []

        for jogador in jogadores:
            char_data = self.utils.find_char_by_player(jogador.id)
            if char_data:
                if self.utils.add_char_rewards(jogador.id, xp_reward, gold_reward):
                    success_count += 1
                    results.append(f"✅ {jogador.mention}")
                else:
                    results.append(f"❌ {jogador.mention} (erro ao salvar)")
            else:
                results.append(f"⚠️ {jogador.mention} (sem personagem)")

        # Resposta
        reward_type = "metade das recompensas" if metade else "recompensas completas"
        embed = discord.Embed(title=f"Recompensas aplicadas - {reward_type}")
        embed.color = 0x00ff00 if success_count > 0 else 0xff0000
        embed.add_field(name="**Nível da missão**", value=nivel, inline=True)
        embed.add_field(name="**XP por jogador**", value=xp_reward, inline=True)
        embed.add_field(name="**Ouro por jogador**", value=gold_reward, inline=True)
        embed.add_field(name="**Resultados**", value="\n".join(results), inline=False)

        await interaction.response.send_message(embed=embed)
        logger.info(f"Recompensas de nível {nivel} aplicadas a {success_count}/{len(jogadores)} jogadores")
