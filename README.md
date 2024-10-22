# mac
Bot da guilda de Parabellum

## Descrição
Este é um bot para a guilda de Parabellum, desenvolvido para auxiliar nas atividades da guilda, como rolagem de dados, criação de missões e verificação de latência.

## Comandos de Admin
### `/sync_and_ping`
Verifica a latência do bot e recarrega todos os comandos.
- **Uso**: `/sync_and_ping`
- **Descrição**: Retorna a latência do bot em milissegundos.


## Comandos gerais
### `/roll_parabellum`
Rola dados para testes de Parabellum.
- **Uso**: `/roll_parabellum <qtd_dados> <dificuldade> <target>`
- **Parâmetros**:
  - `qtd_dados`: Quantidade de dados a serem rolados.
  - `dificuldade`: Dificuldade do teste.
  - `target` (opcional): Alvo da rolagem para sucesso (padrão é 8).
- **Descrição**: Rola a quantidade especificada de dados e retorna os resultados, incluindo sucessos e falhas críticas.

### `/feature_check`
Checa as funcionalidades disponíveis.
- **Uso**: `/feature_check`
- **Descrição**: Verifica se o usuário é administrador e se o comando está sendo executado no servidor da guilda.


## Comandos da guilda
### `/mission_create`
Cria uma missão no quadro.
- **Uso**: `/mission_create <mestre> <rank> <titulo_missao> <resumo> <data_hora>`
- **Parâmetros**:
  - `mestre`: Narrador da mesa.
  - `rank`: Dificuldade da missão.
  - `titulo_missao`: O nome da sua aventura.
  - `resumo`: Uma sinopse da missão.
  - `data_hora`: Quando a aventura será narrada (ex: 24/08 17:00).
- **Descrição**: Cria uma nova missão no quadro de missões da guilda.

### `/mission_success`
Registra o sucesso de uma missão.
- **Uso**: `/mission_success`
- **Descrição**: Registra o sucesso de uma missão no quadro de missões.

### `/mission_failed`
Registra a falha de uma missão.
- **Uso**: `/mission_failed`
- **Descrição**: Registra a falha de uma missão no quadro de missões.