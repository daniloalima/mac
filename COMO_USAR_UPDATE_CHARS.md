# Comando /update_chars

## Descrição
Comando de administrador que atualiza automaticamente o nível de todos os personagens no arquivo `chars.json` baseado no XP acumulado.

## Como usar
1. Execute o comando `/update_chars` no Discord (apenas admins têm permissão)
2. O bot irá processar todos os personagens e:
   - Calcular o nível correto baseado no XP acumulado
   - Atualizar o nível do personagem
   - Ajustar o XP restante (XP que sobrou após os ups de nível)
   - Salvar as mudanças no arquivo `chars.json`

## Funcionamento do Sistema de XP

### Tabela de XP necessário para upar cada nível:
- Nível 1→2: 5 XP
- Nível 2→3: 7 XP
- Nível 3→4: 10 XP
- Nível 4→5: 12 XP
- Nível 5→6: 15 XP
- Nível 6→7: 18 XP
- Nível 7→8: 22 XP
- Nível 8→9: 26 XP
- Nível 9→10: 30 XP
- Nível 10→11: 35 XP
- Nível 11→12: 40 XP
- Nível 12→13: 45 XP
- Nível 13→14: 50 XP
- Nível 14→15: 55 XP
- Nível 15→16: 60 XP
- Nível 16→17: 70 XP
- Nível 17→18: 80 XP
- Nível 18→19: 90 XP
- Nível 19→20: 100 XP
- Nível 20: Máximo (XP acumula mas não sobe mais)

### Exemplo prático:

**Antes da atualização:**
- Personagem: João Silva
- Nível: 1
- XP: 10

**Cálculo:**
1. Nível 1 com 10 XP
2. Precisa de 5 XP para ir de nível 1→2
3. 10 - 5 = 5 XP restantes
4. Agora está no nível 2 com 5 XP
5. Precisa de 7 XP para ir de nível 2→3
6. Como tem apenas 5 XP, não pode upar mais

**Depois da atualização:**
- Personagem: João Silva
- Nível: 2
- XP: 5

## Resposta do Comando

O comando retorna um relatório detalhado com:
- Total de personagens no arquivo
- Quantos foram atualizados
- Lista de mudanças para cada personagem:
  - Nome do personagem
  - Nível anterior → Nível novo
  - XP anterior → XP restante
  - Quantos níveis subiu

## Observações Importantes

1. **Processo recursivo**: O sistema continua upando o personagem enquanto tiver XP suficiente
2. **Nível máximo**: 20 é o nível máximo. XP continua acumulando mas não sobe mais de nível
3. **XP restante**: Após a atualização, o XP que sobrou fica armazenado para os próximos ups
4. **Segurança**: O arquivo é salvo apenas se houver mudanças
5. **Reversível**: Mantenha backups do `chars.json` antes de executar

## Integração com outros comandos

Este comando trabalha em conjunto com:
- `/char_add_rewards`: Adiciona XP e ouro aos personagens
- `/char_update`: Permite atualização manual de dados
- `/char_info`: Mostra as informações atualizadas do personagem

## Quando usar

- Após adicionar recompensas manualmente ao arquivo JSON
- Após corrigir XP de personagens
- Para sincronizar todos os níveis com o XP acumulado
- Após importar dados de outro sistema
