import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ler o arquivo de conclusão
with open("conclusao.txt", "r", encoding="utf-8") as f:
    conclusao_texto = f.read()

# Simulação de Assistants (você pode conectar com OpenAI depois)
suspect_assistants = {
    "Lucas Mendes": "asst_VqBHLmsDiSctPiBrgwPs6Ids",
    "Maya Tanaka Monteiro": "asst_0LHiAAzNdxaInzKt7F1ZzXAP",
    "Misa Smith": "asst_J1ursZZn2ZlX8f0sI5RrkdCv",
    "Morgan Miller": "asst_I5f5zViFQVZXRrgIsmJps0pC",
    "Richard Ortiz": "asst_lrwMFuqZ8L107MIN0MaX4EzN",
    "Victor Castellani": "asst_pzcGdEQNniwbzZRCuaNbJI8Y"
}

# Guardar estado da página
if "page" not in st.session_state:
    st.session_state.page = "home"

# Guardar histórico de chat por suspeito
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {suspect: [] for suspect in suspect_assistants.keys()}

if "selected_suspect" not in st.session_state:
    st.session_state.selected_suspect = list(suspect_assistants.keys())[0]

def go_to_interview():
    st.session_state.page = "interview"

def go_home():
    st.session_state.page = "home"

def get_assistant_response(suspect, user_message):
    try:
        print(f"\n[DEBUG] Iniciando conversa com {suspect}")
        print(f"[DEBUG] Mensagem do usuário: {user_message}")
        
        # Criar uma thread para a conversa
        thread = client.beta.threads.create()
        print(f"[DEBUG] Thread criada com ID: {thread.id}")
        
        # Adicionar a mensagem do usuário à thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        print("[DEBUG] Mensagem adicionada à thread")
        
        # Executar o assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=suspect_assistants[suspect]
        )
        print(f"[DEBUG] Run iniciado com ID: {run.id}")
        
        # Aguardar a conclusão da execução
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"[DEBUG] Status do run: {run_status.status}")
            if run_status.status == "completed":
                break
        
        # Obter a resposta do assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = messages.data[0].content[0].text.value
        print(f"[DEBUG] Resposta recebida: {assistant_message[:100]}...")
        
        return assistant_message
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {str(e)}")
        return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"

# Página Inicial
if st.session_state.page == "home":
    st.title("🕵️‍♂️ Jogo de Detetive")

    st.markdown("""
    ### Instruções do Jogo
    Você é um detetive encarregado de solucionar um misterioso assassinato. Analise as provas, entreviste os suspeitos e descubra quem é o culpado!

    **Como jogar?**
    1. Imprima os arquivos PDF por completo (ou visualize-o no seu notebook.
    2. Analise atentamente a narrativa e os indícios, abrindo um arquivo por vez, começando pela História e seguindo para os outros.
    3. Entreviste os suspeitos para encontrar inconsistências nas histórias.
    4. Acuse o culpado!
    """)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with open("./files/Historia.pdf", "rb") as f:
            st.download_button("📖 Baixar História", f, file_name="./files/Historia.pdf")

    with col2:
        with open("./files/Files01.pdf", "rb") as f:
            st.download_button("📄 Baixar Prova 1", f, file_name="./files/Files01.pdf")

    with col3:
        with open("./files/Files02.pdf", "rb") as f:
            st.download_button("📄 Baixar Prova 2", f, file_name="./files/Files02.pdf")

    with col4:
        st.button("🎙️ Interrogatório", on_click=go_to_interview)

    # Seção para acusar o culpado
    st.markdown("---")
    st.markdown("### 🎯 Acusar o Culpado")
    
    # Combo Box para selecionar o suspeito
    accused_suspect = st.selectbox(
        "Selecione quem você acredita ser o culpado:",
        ["Selecione um suspeito..."] + list(suspect_assistants.keys())
    )
    
    # Botão para confirmar a acusação
    if st.button("🔍 Confirmar Acusação", disabled=accused_suspect == "Selecione um suspeito..."):
        if accused_suspect in suspect_assistants:
            if accused_suspect == "Maya Tanaka Monteiro":
                st.success("🎉 Parabéns! Você acertou! Maya Tanaka Monteiro é a culpada!")
                st.balloons()
                
                # Exibir a conclusão em um container expansível
                with st.expander("📖 A Execução do Plano de Maya", expanded=True):
                    st.markdown(conclusao_texto)
            else:
                st.error(f"❌ Você errou! {accused_suspect} não é o(a) culpado(a). Tente novamente!")
                st.snow()

# Página de Entrevista
elif st.session_state.page == "interview":
    st.title("🎙️ Entrevista com Suspeitos")
    st.button("🔙 Voltar", on_click=go_home)

    # Selecionar suspeito
    suspect = st.selectbox("Selecione um suspeito para conversar:", list(suspect_assistants.keys()))
    st.session_state.selected_suspect = suspect

    # Exibir histórico de chat do suspeito selecionado
    for role, msg in st.session_state.chat_histories[suspect]:
        if role == "user":
            st.markdown(f"**Você:** {msg}")
        else:
            st.markdown(f"**{suspect}:** {msg}")

    # Container para a resposta do assistant
    response_container = st.empty()

    user_input = st.chat_input("Digite sua pergunta ao suspeito...")

    if user_input:
        # Adicionar mensagem do usuário ao histórico e mostrar imediatamente
        st.session_state.chat_histories[suspect].append(("user", user_input))
        st.markdown(f"**Você:** {user_input}")
        
        # Mostrar indicador de carregamento
        with response_container:
            st.markdown("**Aguardando resposta...**")
        
        # Obter resposta do assistant
        assistant_response = get_assistant_response(suspect, user_input)
        
        # Adicionar resposta ao histórico e mostrar
        st.session_state.chat_histories[suspect].append(("assistant", assistant_response))
        st.markdown(f"**{suspect}:** {assistant_response}")
        
        # Limpar o container de resposta
        response_container.empty()
