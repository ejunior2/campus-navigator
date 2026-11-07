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

## Agente de LLM

Gemini com tool calling sobre os KPIs em SQL. O script `evaluate` roda 10
perguntas (dentro do escopo, fora do escopo e entrada inválida). A avaliação
é por palavra-chave, o que é uma limitação conhecida; usar um LLM como juiz
seria a evolução natural.

## Automação (n8n)

Um workflow no n8n (`automation/daily_report.json`) chama o endpoint `/report` da API todos os dias às 8h e, se alguma zona passa de 45% de leituras com sinal fraco, monta a mensagem de alerta. Para usar: suba a API, rode `npx n8n` e importe o arquivo.

## Roadmap

- [x] Dia 1: gerador de dados sintéticos
- [x] Dia 2: banco SQLite e KPIs em SQL
- [x] Dia 3: dashboard Streamlit publicado
- [x] Dia 4: agente de LLM com tool calling e avaliação (10 casos)
- [x] Dia 5: API FastAPI e automação n8n
- [ ] Roteador Q-Learning

**Live demo:** <https://campus-navigator-bccc.streamlit.app/>