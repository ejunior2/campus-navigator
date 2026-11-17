import os

import streamlit as st

MAX_QUESTIONS = 10  # por sessão, para proteger o limite gratuito da API
EXAMPLES = [
    "Qual zona tem o pior sinal?",
    "Qual a melhor rota da Biblioteca até o Bloco B?",
    "Qual a diferença entre a rota mais curta e a de melhor sinal da Biblioteca ao Bloco B?",
]


def _load_secrets():
    # Na nuvem a chave vem dos Secrets do Streamlit; localmente, do .env
    try:
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if name in st.secrets:
                os.environ[name] = st.secrets[name]
    except Exception:
        pass


def _answer(question):
    # import tardio: se algo falhar aqui, só o chat é afetado
    from src.agent.agent import ask_agent

    return ask_agent(question, retries=1)


def _friendly_error(exc):
    if getattr(exc, "code", None) == 429:
        return ("O limite gratuito de requisições do Gemini foi atingido. "
                "Tente de novo em cerca de 1 minuto.")
    return ("Não consegui responder agora (o serviço do Gemini pode estar "
            "indisponível ou a chave não está configurada). Tente novamente "
            "em instantes.")


def render_chat_tab():
    _load_secrets()
    st.subheader("Assistente de IA")
    st.caption(
        "Pergunte sobre o sinal, as zonas e as rotas. O modelo consulta "
        "ferramentas que leem os dados e rodam o A*, então os números vêm do "
        "cálculo e não de estimativa. Cada pergunta é independente (o "
        "assistente não lembra das anteriores). Dados sintéticos."
    )

    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("n_questions", 0)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("Exemplos:")
    cols = st.columns(len(EXAMPLES))
    for col, example in zip(cols, EXAMPLES):
        if col.button(example, key=f"ex_{example}"):
            st.session_state.pending = example

    question = st.chat_input("Digite sua pergunta") or st.session_state.pop(
        "pending", None)
    if not question:
        return

    if st.session_state.n_questions >= MAX_QUESTIONS:
        st.info(f"Limite de {MAX_QUESTIONS} perguntas por sessão atingido. "
                "Atualize a página para recomeçar.")
        return

    st.session_state.n_questions += 1
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando os dados..."):
            try:
                answer = _answer(question)
            except Exception as exc:
                answer = _friendly_error(exc)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})