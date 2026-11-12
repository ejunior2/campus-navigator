# Campus Navigator

Roteamento com consciência de conectividade em um mapa de campus simulado,
com dashboard, agente de LLM e roteador com Q-Learning. (Em desenvolvimento.)

## Gerador de dados

Gera um grid de campus 20x20, pontos de acesso Wi-Fi e leituras horárias
de qualidade de sinal por 14 dias.

> Todos os dados são **sintéticos**. O modelo de sinal é uma simplificação
> inventada, não uma medição real.

## Instalação

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt

## Como rodar

    python -m src.data_gen.generate
    python -m pytest
    python -m src.kpis.db
    python -m src.kpis.queries
    python -m streamlit run dashboard/app.py
    python -m src.agent.agent
    python -m src.agent.evaluate
    python -m uvicorn src.api:app --port 8000
    python -m src.router.compare

## Agente de LLM

Gemini com tool calling sobre os KPIs em SQL. O script `evaluate` roda 10 perguntas (dentro do escopo, fora do escopo e entrada inválida) e obtém 10/10 nos dados atuais. A avaliação é por palavra-chave, o que é uma limitação conhecida; usar um LLM como juiz seria a evolução natural.

## Automação (n8n)

Um workflow no n8n (`automation/daily_report.json`) chama o endpoint `/report` da API todos os dias às 8h e, se alguma zona passa de 45% de leituras com sinal fraco, monta a mensagem de alerta. Para usar: suba a API, rode `npx n8n` e importe o arquivo.

## Roteamento (BFS, A* e Q-Learning)

Mesmo ambiente (grid 20x20 com sinal médio por célula), comparando BFS (custo
uniforme), A* por distância, A* com custo de sinal e um agente Q-Learning
tabular. Resultados em `results/route_comparison.csv` (3 pares
origem/destino, 5 seeds para o Q-Learning).

| Par | Algoritmo | Passos | Sinal médio | Sinal mín. | Células fracas |
|---|---|---|---|---|---|
| (0,15)→(19,0) | BFS / A* distância | 37 | 48,7 | 1,2 | 13 |
| | A* sinal / Q-Learning | 37 | 60,2 | 15,7 | 7 |
| (1,1)→(18,18) | BFS / A* distância | 35 | 45,2 | 1,1 | 13 |
| | A* sinal | 37 | 56,7 | 4,7 | 9 |
| | Q-Learning | 35 | 52,8 | 4,7 | 11 |
| (2,16)→(18,1) | BFS / A* distância | 32 | 47,2 | 1,2 | 11 |
| | A* sinal / Q-Learning | 32 | 60,6 | 29,8 | 5 |

**Observações e limitações**
- O A* com sinal otimiza um custo diferente de BFS e A* por distância, então a comparação não é direta.
- O tempo do Q-Learning (~4 s) é de treino, feito uma vez; as buscas levam milissegundos.
- Apenas 3 pares; o sinal por célula é a média de todos os horários.
- A primeira versão do agente não convergiu (recompensa esparsa) e foi corrigida com reward shaping por distância.

## Roadmap

- [x] Dia 1: gerador de dados sintéticos
- [x] Dia 2: banco SQLite e KPIs em SQL
- [x] Dia 3: dashboard Streamlit publicado
- [x] Dia 4: agente de LLM com tool calling e avaliação
- [x] Dia 5: API FastAPI e automação n8n
- [x] Dia 6: sinal com paredes, ambiente em grid, BFS e A*
- [x] Dia 7: Q-Learning e comparação quantitativa
- [ ] Mapa de calor e rotas no dashboard, agente com roteador, chat no Streamlit

**Live demo:** <https://campus-navigator-bccc.streamlit.app/>