# Novo Comando Admin: Resumo de Valores

## Funcionalidade Implementada

Foi criado um novo comando admin `/resumo_valores` que consolida informações financeiras das assinaturas do bot.

## O que o comando faz:

### 1. **Dados da Hotmart**
- Busca assinaturas com status **ACTIVE** e **DELAYED** via API
- Calcula valores totais para cada status
- Agrupa informações por planos de assinatura
- Mostra total de assinantes e valores por categoria

### 2. **Dados do JSON Local**
- Lê o arquivo `mdl_2.json` com assinantes locais
- **NOVO**: Identifica automaticamente assinantes **semestrais** (com "(s)" no nome)
- **NOVO**: Para assinantes semestrais, divide o valor por 6 para obter valor mensal
- **NOVO**: Considera ciclo de 6 meses para verificação de atraso em assinantes semestrais
- Calcula valores totais mensais ajustados e valores em atraso
- Processa valores em formato brasileiro (R$ X,XX)

### 3. **Consolidação Geral**
- Combina valores da Hotmart e JSON local
- Apresenta resumo consolidado de todos os valores mensais
- Mostra total geral e total em atraso
- Inclui detalhamento por planos da Hotmart
- **NOVO**: Mostra quantos assinantes são mensais vs semestrais

## Exemplo de Output:

```
📊 RESUMO GERAL DE VALORES - ASSINATURAS

🌐 HOTMART
• Assinaturas Ativas: 15 (R$ 1.200,00)
• Assinaturas Atrasadas: 3 (R$ 240,00)
• Total Hotmart: R$ 1.440,00

📋 JSON LOCAL
• Total de Assinantes: 27 (R$ 7.604,00)
  - Mensais: 25 | Semestrais: 2
• Assinantes em Atraso: 5 (R$ 478,80)
• Total JSON Local: R$ 7.604,00

💰 CONSOLIDADO GERAL
• Valor Total Geral: R$ 9.044,00
• Valor Total em Atraso: R$ 718,80

📈 DETALHES HOTMART POR PLANOS:
• Plano Premium: 10 assinantes (8 ativas, 2 atrasadas) - R$ 800,00
• Plano Básico: 8 assinantes (7 ativas, 1 atrasadas) - R$ 640,00
```

**Observação**: Para assinantes semestrais (com "(s)" no nome), o valor é automaticamente dividido por 6 para mostrar a receita mensal equivalente.

## Implementações Técnicas:

### Novos Métodos:
- `HotmartAPI.get_active_and_delayed_summary()` - Busca dados consolidados da API
- `AdminCommands.resumo_valores()` - Comando Discord para gerar o resumo

### Melhorias:
- Tratamento de erros robusto para API e JSON
- Processamento seguro de valores monetários
- **NOVO**: Detecção automática de assinantes semestrais pelo nome (contém "(s)")
- **NOVO**: Cálculo mensal para assinantes semestrais (valor ÷ 6)
- **NOVO**: Verificação de atraso ajustada para ciclo semestral (6 meses)
- Quebra automática de mensagens longas (chunks de 2000 caracteres)
- Validação de permissões admin

### Arquivos Modificados:
- `/modules/hotmart_handler.py` - Novo método para buscar ACTIVE e DELAYED
- `/modules/commands/admin_commands.py` - Comando `/resumo_valores` com cálculo semestral
- `/modules/services/assinante_service.py` - Verificação de atraso ajustada para semestrais

## Como Usar:

1. O comando só funciona para administradores
2. Execute `/resumo_valores` no Discord
3. O bot irá processar e retornar o relatório completo
4. Se houver erro na API Hotmart, ainda mostrará dados do JSON local

## Status: ✅ IMPLEMENTADO E TESTADO
