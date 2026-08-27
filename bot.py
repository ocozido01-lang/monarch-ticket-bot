import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

TOKEN = os.getenv("TOKEN")

CATEGORY_ID = int(os.getenv("CATEGORY_ID", "0"))

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

class TicketBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()
        self.add_view(TicketMenu())
        self.add_view(CloseTicket())

bot = TicketBot()


class TicketMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Fazer Teste!",
                description="Solicite um teste ou avaliação.",
                emoji="📝",
                value="teste"
            ),

            discord.SelectOption(
                label="Tire suas dúvidas",
                description="Precisa de ajuda? Abra um atendimento.",
                emoji="❓",
                value="duvida"
            ),

            discord.SelectOption(
                label="Faça Parceria",
                description="Solicite uma parceria.",
                emoji="🤝",
                value="parceria"
            ),

            discord.SelectOption(
                label="Faça uma reclamação",
                description="Envie uma reclamação.",
                emoji="⚠️",
                value="reclamacao"
            ),

            discord.SelectOption(
                label="Denuncie alguém",
                description="Faça uma denúncia.",
                emoji="🚨",
                value="denuncia"
            )
        ]

        super().__init__(
            placeholder="Selecione a opção:",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_menu"
        )

    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        category = guild.get_channel(CATEGORY_ID)

        if category is None:
            await interaction.response.send_message(
                "❌ A categoria dos tickets não foi configurada.",
                ephemeral=True
            )
            return

        for channel in category.channels:

            if channel.topic == f"ticket-{member.id}":

                await interaction.response.send_message(
                    f"❌ Você já possui um ticket aberto: {channel.mention}",
                    ephemeral=True
                )
                return

        tipo = self.values[0]

        nomes = {
            "teste": "teste",
            "duvida": "duvida",
            "parceria": "parceria",
            "reclamacao": "reclamacao",
            "denuncia": "denuncia"
        }

        nome_ticket = nomes.get(tipo, "ticket")

        overwrites = {

            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            )
        }

        support_role = discord.utils.get(
    guild.roles,
    name="Suporte"
        )

        if support_role:

            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True
            )

        for role in guild.roles:

            if role.permissions.administrator:

                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True
                )

        channel = await guild.create_text_channel(
            name=f"🎫・{nome_ticket}-{member.name}",
            category=category,
            overwrites=overwrites,
            topic=f"ticket-{member.id}"
        )

        textos = {

            "teste":
                "📝 **Fazer Teste!**\n\n"
                "Explique qual teste você deseja realizar.",

            "duvida":
                "❓ **Tire suas dúvidas**\n\n"
                "Explique sua dúvida de forma clara.",

            "parceria":
                "🤝 **Faça Parceria**\n\n"
                "Envie as informações da sua proposta.",

            "reclamacao":
                "⚠️ **Faça uma reclamação**\n\n"
                "Explique o ocorrido com detalhes.",

            "denuncia":
                "🚨 **Denuncie alguém**\n\n"
                "Informe quem está sendo denunciado e envie as provas."
        }

        embed = discord.Embed(
            title="🎫 Suporte — Monarch FC",
            description=(
                f"Olá, {member.mention}!\n\n"
                f"{textos.get(tipo)}\n\n"
                "Nossa equipe irá analisar sua solicitação "
                "e responder o mais rápido possível."
            ),
            color=discord.Color.purple()
        )

        embed.add_field(
            name="📌 Categoria",
            value=f"**{tipo.capitalize()}**",
            inline=False
        )

        embed.add_field(
            name="📋 Orientações",
            value=(
                "• Explique seu problema claramente.\n"
                "• Envie prints ou vídeos quando necessário.\n"
                "• Aguarde o atendimento da equipe.\n"
                "• Evite mencionar a Staff sem necessidade."
            ),
            inline=False
        )

        embed.set_footer(
            text="Monarch FC • Sistema de Suporte"
        )

        await channel.send(
            content=member.mention,
            embed=embed,
            view=CloseTicket()
        )

        await interaction.response.send_message(
            f"✅ Seu ticket foi criado: {channel.mention}",
            ephemeral=True
        )


class CloseTicket(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fechar Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "🔒 Este ticket será fechado em 5 segundos."
        )

        await asyncio.sleep(5)

        await interaction.channel.delete(
            reason=f"Ticket fechado por {interaction.user}"
        )


@bot.tree.command(
    name="ticket",
    description="Envia o painel de suporte."
)
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Suporte — Monarch FC",
        description=(
            "Precisa de ajuda? Abra um ticket e descreva "
            "seu problema com o máximo de detalhes possível.\n\n"

            "Nossa equipe de **Suporte** analisará sua "
            "solicitação e responderá o mais rápido possível.\n\n"

            "📌 **Antes de abrir um ticket:**\n\n"

            "• Verifique se sua dúvida já foi respondida.\n"
            "• Explique seu problema de forma clara e objetiva.\n"
            "• Envie provas (prints ou vídeos), caso necessário.\n"
            "• Aguarde o atendimento com paciência.\n"
            "• Evite mencionar a Staff sem necessidade.\n\n"

            "━━━━━━━━━━━━━━━━━━━━\n\n"

            "❤️ **Nosso objetivo é oferecer um atendimento "
            "rápido, organizado e respeitoso para todos "
            "os membros do Monarch FC.**"
        ),
        color=discord.Color.purple()
    )

    embed.set_footer(
        text="Monarch FC • Sistema de Suporte"
    )

    await interaction.response.send_message(
        embed=embed,
        view=TicketMenu()
    )


@ticket.error
async def ticket_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        await interaction.response.send_message(
            "❌ Você precisa ser administrador para usar esse comando.",
            ephemeral=True
        )


@bot.event
async def on_ready():

    print(f"Bot online como {bot.user}")


if not TOKEN:
    raise RuntimeError(
        "A variável TOKEN não foi configurada no Railway."
    )

bot.run(TOKEN)
