# 📖 Comandos de Personagens

Guia completo de todos os comandos relacionados ao sistema de personagens do bot.

---

## 📋 Índice

1. [/char_create](#char_create) - Criar personagem
2. [/char_info](#char_info) - Ver informações do personagem
3. [/char_update](#char_update) - Atualizar dados do personagem
4. [/char_delete](#char_delete) - Remover personagem
5. [/char_add_rewards](#char_add_rewards) - Adicionar recompensas
6. [Sistema de Níveis e XP](#sistema-de-níveis-e-xp)
7. [Arquivo chars.json](#arquivo-charsjson)

---

## <a name="char_create"></a>🆕 /char_create

Cria um novo personagem para um jogador.

### Permissão
- ⚠️ **Somente Administradores**

### Parâmetros
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `jogador` | Member | ✅ | Membro do Discord que será dono do personagem |
| `nome_personagem` | String | ✅ | Nome do personagem |

### Comportamento
- Cada jogador pode ter **apenas 1 personagem**
- Personagem inicia com:
  - **Nível**: 1
  - **XP**: 0
  - **Dinheiro**: 0

### Exemplo de uso
```
/char_create jogador:@João nome_personagem:Aragorn
```

### Mensagens de erro
- ❌ "Você não tem permissão para usar este comando" - Não é admin
- ❌ "Esse comando só pode ser utilizado no servidor de guilda" - Comando fora do servidor
- ❌ "@João já possui um personagem: Gandalf" - Jogador já tem personagem

---

## <a name="char_info"></a>ℹ️ /char_info

Visualiza as informações de um personagem.

### Permissão
- ✅ **Todos os usuários**

### Parâmetros
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `jogador` | Member | ❌ | Membro do Discord para consultar (padrão: você mesmo) |

### Informações exibidas
- 📛 Nome do personagem
- 👤 Jogador dono
- 📊 Nível atual
- ⭐ XP acumulado
- 💰 Dinheiro (moedas de ouro)

### Exemplo de uso
```
/char_info
/char_info jogador:@Maria
```

### Mensagens de erro
- ❌ "@Maria não possui um personagem registrado" - Jogador sem personagem

---

## <a name="char_update"></a>✏️ /char_update

Atualiza os dados de um personagem existente.

### Permissão
- ⚠️ **Somente Administradores**

### Parâmetros
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `jogador` | Member | ✅ | Membro do Discord dono do personagem |
| `nome` | String | ❌ | Novo nome do personagem |
| `dinheiro` | Integer | ❌ | Nova quantidade de dinheiro (não pode ser negativo) |
| `xp` | Integer | ❌ | Nova quantidade de XP (não pode ser negativo) |
| `nivel` | Integer | ❌ | Novo nível (entre 1 e 20) |

### Comportamento
- Pelo menos **1 parâmetro** deve ser fornecido
- Valores são **sobrescritos**, não somados
- Para somar XP/ouro, use `/char_add_rewards`

### Validações
- `dinheiro`: mínimo 0 (valores negativos viram 0)
- `xp`: mínimo 0 (valores negativos viram 0)
- `nivel`: entre 1 e 20 (valores fora do range são ajustados)

### Exemplo de uso
```
/char_update jogador:@Pedro nome:Legolas
/char_update jogador:@Pedro nivel:5 xp:50
/char_update jogador:@Pedro dinheiro:1000
```

### ⚠️ Atenção
- Este comando **não calcula níveis automaticamente** com base no XP
- Para recalcular níveis baseado no XP, use `/update_chars`

### Mensagens de erro
- ❌ "Você não tem permissão para usar este comando" - Não é admin
- ❌ "@Pedro não possui um personagem registrado" - Jogador sem personagem
- ❌ "Nenhum campo foi especificado para atualização" - Nenhum parâmetro fornecido

---

## <a name="char_delete"></a>🗑️ /char_delete

Remove permanentemente um personagem.

### Permissão
- ⚠️ **Somente Administradores**

### Parâmetros
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `jogador` | Member | ✅ | Membro do Discord para remover o personagem |

### Comportamento
- ⚠️ **Ação irreversível** - O personagem será permanentemente deletado
- Recomenda-se fazer backup do `chars.json` antes de remover

### Exemplo de uso
```
/char_delete jogador:@Carlos
```

### Mensagens de erro
- ❌ "Você não tem permissão para usar este comando" - Não é admin
- ❌ "@Carlos não possui um personagem registrado" - Jogador sem personagem

---

## <a name="char_add_rewards"></a>🎁 /char_add_rewards

Adiciona XP e ouro aos personagens após missões.

### Permissão
- ⚠️ **Somente Administradores**

### Parâmetros
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `nivel` | Integer | ✅ | Nível da missão (1-20) para calcular recompensas |
| `jogador_1` | Member | ✅ | Primeiro jogador |
| `jogador_2` | Member | ✅ | Segundo jogador |
| `jogador_3` | Member | ✅ | Terceiro jogador |
| `jogador_4` | Member | ❌ | Quarto jogador (opcional) |
| `jogador_5` | Member | ❌ | Quinto jogador (opcional) |
| `metade` | Boolean | ❌ | Se true, dá metade das recompensas (missões falhadas) |

### Comportamento
- Calcula automaticamente XP e ouro baseado no nível da missão
- **Soma** as recompensas aos valores existentes (não sobrescreve)
- Se `metade=true`, dá 50% das recompensas
- Ignora jogadores que não têm personagem registrado
- Atualiza automaticamente o nível se o personagem tiver XP suficiente

### Tabela de Recompensas

| Nível | XP (sucesso) | Ouro (sucesso) | XP (falha) | Ouro (falha) |
|-------|--------------|----------------|------------|--------------|
| 1 | 5 | 50 | 2 | 25 |
| 2 | 7 | 75 | 3 | 37 |
| 3 | 10 | 100 | 5 | 50 |
| 4 | 12 | 150 | 6 | 75 |
| 5 | 15 | 200 | 7 | 100 |
| 6 | 18 | 250 | 9 | 125 |
| 7 | 22 | 300 | 11 | 150 |
| 8 | 26 | 400 | 13 | 200 |
| 9 | 30 | 500 | 15 | 250 |
| 10 | 35 | 650 | 17 | 325 |
| 11 | 40 | 800 | 20 | 400 |
| 12 | 45 | 1000 | 22 | 500 |
| 13 | 50 | 1200 | 25 | 600 |
| 14 | 55 | 1500 | 27 | 750 |
| 15 | 60 | 2000 | 30 | 1000 |
| 16 | 70 | 2500 | 35 | 1250 |
| 17 | 80 | 3000 | 40 | 1500 |
| 18 | 90 | 4000 | 45 | 2000 |
| 19 | 100 | 5000 | 50 | 2500 |
| 20 | 120 | 6500 | 60 | 3250 |

### Exemplo de uso
```
# Missão nível 5 bem-sucedida (3 jogadores)
/char_add_rewards nivel:5 jogador_1:@Ana jogador_2:@Bruno jogador_3:@Carla

# Missão nível 10 falhada (4 jogadores)
/char_add_rewards nivel:10 jogador_1:@Ana jogador_2:@Bruno jogador_3:@Carla jogador_4:@Diego metade:true
```

### Resposta do comando
Exibe um embed com:
- 📊 Nível da missão
- ⭐ XP por jogador
- 💰 Ouro por jogador
- 📋 Lista de resultados:
  - ✅ Jogador - Recompensa aplicada com sucesso
  - ❌ Jogador - Erro ao salvar
  - ⚠️ Jogador - Não possui personagem registrado

### Mensagens de erro
- ❌ "Você não tem permissão para usar este comando" - Não é admin
- ❌ "O nível deve estar entre 1 e 20" - Nível inválido

---

## <a name="sistema-de-níveis-e-xp"></a>📈 Sistema de Níveis e XP

### Como funciona

O sistema usa **XP para subir de nível** de forma recursiva e automática.

### Tabela de XP necessário para upar

| Nível Atual | XP Necessário | Nível Atual | XP Necessário |
|-------------|---------------|-------------|---------------|
| 1 → 2 | 5 XP | 11 → 12 | 40 XP |
| 2 → 3 | 7 XP | 12 → 13 | 45 XP |
| 3 → 4 | 10 XP | 13 → 14 | 50 XP |
| 4 → 5 | 12 XP | 14 → 15 | 55 XP |
| 5 → 6 | 15 XP | 15 → 16 | 60 XP |
| 6 → 7 | 18 XP | 16 → 17 | 70 XP |
| 7 → 8 | 22 XP | 17 → 18 | 80 XP |
| 8 → 9 | 26 XP | 18 → 19 | 90 XP |
| 9 → 10 | 30 XP | 19 → 20 | 100 XP |
| 10 → 11 | 35 XP | 20 → ? | Nível máximo |

### Exemplo de progressão

**Situação inicial:**
- Personagem: Legolas
- Nível: 1
- XP: 0

**Após missão nível 3 (10 XP):**
1. Recebe 10 XP
2. Tem 10 XP total
3. Precisa de 5 XP para ir de nível 1→2
4. 10 - 5 = 5 XP restantes
5. Sobe para nível 2 com 5 XP
6. Precisa de 7 XP para ir de nível 2→3
7. Não tem XP suficiente, para aqui

**Resultado final:**
- Nível: 2
- XP: 5

### Atualização automática de níveis

Ao usar `/char_add_rewards`, o sistema:
1. ✅ Adiciona o XP ganho ao XP atual
2. ✅ Calcula automaticamente quantos níveis pode subir
3. ✅ Atualiza o nível do personagem
4. ✅ Mantém apenas o XP restante (que não foi usado para upar)

### Comando /update_chars

Para recalcular todos os níveis baseado no XP acumulado:
```
/update_chars
```

Este comando é útil para:
- Corrigir níveis após edições manuais
- Sincronizar níveis com XP acumulado
- Atualizar personagens após importação de dados

---

## <a name="arquivo-charsjson"></a>💾 Arquivo chars.json

### Localização
```
/home/dan/git/mac/chars.json
```

### Estrutura
```json
[
  {
    "jogador": 123456789012345678,
    "personagem": "Aragorn",
    "dinheiro": 500,
    "xp": 25,
    "lvl": 3
  },
  {
    "jogador": 987654321098765432,
    "personagem": "Gandalf",
    "dinheiro": 1200,
    "xp": 80,
    "lvl": 7
  }
]
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `jogador` | Integer | ID do Discord do jogador (único) |
| `personagem` | String | Nome do personagem |
| `dinheiro` | Integer | Moedas de ouro do personagem |
| `xp` | Integer | XP restante (após ups de nível) |
| `lvl` | Integer | Nível atual (1-20) |

### ⚠️ Backup recomendado

Faça backup regular do arquivo:
```bash
cp chars.json chars.json.backup
```

### Edição manual

Você pode editar o arquivo manualmente, mas:
1. ⚠️ Mantenha a estrutura JSON válida
2. ⚠️ IDs do Discord devem ser números inteiros
3. ⚠️ Execute `/update_chars` após edições para recalcular níveis
4. ⚠️ Faça backup antes de editar

---

## 🔄 Fluxo de trabalho típico

### 1. Criar personagem
```
/char_create jogador:@João nome_personagem:Aragorn
```

### 2. Após missão bem-sucedida
```
/char_add_rewards nivel:5 jogador_1:@João jogador_2:@Maria jogador_3:@Pedro
```

### 3. Verificar personagem
```
/char_info jogador:@João
```

### 4. Ajuste manual (se necessário)
```
/char_update jogador:@João dinheiro:1500
```

### 5. Remover personagem (se necessário)
```
/char_delete jogador:@João
```

---

## 💡 Dicas e boas práticas

### Para jogadores
- ✅ Use `/char_info` regularmente para acompanhar sua progressão
- ✅ O comando funciona em qualquer canal do servidor
- ✅ Você pode ver o personagem de outros jogadores

### Para administradores
- ✅ Use `/char_add_rewards` após cada missão
- ✅ Marque `metade:true` para missões falhadas
- ✅ Faça backup do `chars.json` periodicamente
- ✅ Use `/update_chars` após edições manuais no JSON
- ⚠️ `/char_update` sobrescreve valores (não soma)
- ⚠️ `/char_delete` é irreversível

### Manutenção
```bash
# Backup regular
cp chars.json "chars.json.$(date +%Y%m%d)"

# Verificar integridade do JSON
python3 -m json.tool chars.json

# Recalcular todos os níveis
/update_chars (no Discord)
```

---

## ❓ FAQ

**P: Um jogador pode ter mais de um personagem?**  
R: Não, cada jogador pode ter apenas 1 personagem.

**P: O que acontece se eu usar /char_update para mudar o nível?**  
R: O nível será alterado diretamente, mas o XP não será recalculado. Use `/update_chars` depois para sincronizar.

**P: Posso dar recompensas negativas?**  
R: Não, o sistema não aceita valores negativos. Use `/char_update` para reduzir valores.

**P: O que acontece quando um personagem chega ao nível 20?**  
R: O nível 20 é o máximo. XP continua acumulando mas não há mais ups de nível.

**P: Como funciona o arredondamento em missões falhadas?**  
R: Usa divisão inteira (//). Ex: 15 XP vira 7 XP (15 // 2 = 7).

**P: Posso recuperar um personagem deletado?**  
R: Somente se tiver um backup do `chars.json`. A exclusão é permanente.

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique se está no servidor correto
2. Confirme que tem as permissões necessárias
3. Consulte os logs do bot para detalhes de erros
4. Verifique a integridade do arquivo `chars.json`
