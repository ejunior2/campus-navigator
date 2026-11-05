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

## Roadmap

- [x] Dia 1: gerador de dados sintéticos
- [x] Dia 2: banco SQLite e KPIs em SQL
- [x] Dia 3: dashboard Streamlit publicado
- [ ] Agente de LLM, automação n8n, roteador Q-Learning

**Live demo:** <https://campus-navigator-bccc.streamlit.app/>