import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
from services import google_sheets as gs

st.set_page_config(page_title="Contas a Pagar", page_icon="💰", layout="centered")

# CSS Básico e Cores
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; max-width: 600px; }
    
    /* 1. Bordas dos inputs (Padrão Conf. Jogos) */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stDateInput"] > div,
    div[data-testid="stSelectbox"] > div {
        background-color: #ffffff !important;
        border: 1.2px solid #0d6efd !important;
        border-radius: 8px !important;
        transition: all 0.25s ease-in-out !important;
    }
    /* Foco verde */
    div[data-testid="stTextInput"] > div:focus-within,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stDateInput"] > div:focus-within,
    div[data-testid="stSelectbox"] > div:focus-within {
        border-color: #198754 !important;
        box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.15) !important;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stDateInput"] input {
        background-color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 2. Cor do botão Sair */
    div.st-key-btn_sair button { background-color: #dc3545 !important; border: 1px solid #dc3545 !important; }
    div.st-key-btn_sair button * { color: white !important; }

    /* 3. Cor das Setas e Fundo Azul Claro do Mês */
    div.st-key-btn_prev button, div.st-key-btn_next button { 
        background-color: #0d6efd !important; border: 1px solid #0d6efd !important; 
        height: 38px !important; padding: 0 !important;
    }
    div.st-key-btn_prev button *, div.st-key-btn_next button * { color: white !important; }
    
    div[class*="st-key-nav_mes"] div[data-testid="stHorizontalBlock"] { 
        background-color: #e3f2fd !important; /* Azul bem claro */
        border-radius: 10px !important;
        padding: 5px 10px !important;
        display: flex !important; flex-wrap: nowrap !important; align-items: center !important;
    }
    div[class*="st-key-nav_mes"] div[data-testid="stColumn"] { padding: 0 !important; min-width: 0 !important; }

    /* 4. Cor do botão Desmarcar Pagamento (Laranja) */
    div[class*="st-key-btn_desmarcar_"] button {
        background-color: #fd7e14 !important; border: 1px solid #fd7e14 !important;
    }
    div[class*="st-key-btn_desmarcar_"] button * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- ESTADOS DA SESSÃO ----------------
if "logado" not in st.session_state: st.session_state["logado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = ""
if "mes_atual" not in st.session_state: st.session_state["mes_atual"] = datetime.date.today().replace(day=1)

# ---------------- MODAIS ----------------
@st.dialog("Confirmar Pagamento")
def modal_pagar(conta_id, valor):
    st.write(f"Deseja confirmar o pagamento de **R$ {valor:.2f}**?")
    data_pag = st.date_input("Data do Pagamento", value=datetime.date.today(), format="DD/MM/YYYY")
    if st.button("Confirmar e Pagar", type="primary", use_container_width=True):
        if gs.atualizar_status_conta(conta_id, "Pago", data_pag.strftime("%d/%m/%Y")):
            st.rerun()

@st.dialog("Adicionar Nova Conta")
def modal_adicionar():
    sugestoes = gs.obter_descricoes_usuario(st.session_state["usuario"])
    opcoes = ["Nova Conta..."] + sugestoes
    
    with st.form("form_nova_conta", clear_on_submit=True):
        desc_escolhida = st.selectbox("Selecione uma conta", opcoes)
        
        desc = desc_escolhida
        if desc_escolhida == "Nova Conta...":
            desc = st.text_input("Cadastre uma nova conta (Ex: Internet, Aluguel)")
        
        col_val, col_venc = st.columns(2)
        with col_val:
            val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        with col_venc:
            proximo_mes = st.session_state["mes_atual"] + relativedelta(months=1)
            ultimo_dia = proximo_mes - datetime.timedelta(days=1)
            venc = st.date_input("Vencimento", value=ultimo_dia, format="DD/MM/YYYY")
            
        obs = st.text_input("Observação (Opcional)")
        mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
        
        if st.form_submit_button("Salvar Conta", type="primary", use_container_width=True):
            if not desc or desc == "Nova Conta..." or val < 0:
                st.error("Preencha a descrição corretamente.")
            else:
                if gs.salvar_conta(st.session_state["usuario"], mes_busca, desc, val, venc.strftime("%d/%m/%Y"), obs):
                    st.rerun()

@st.dialog("Editar Conta")
def modal_editar(conta):
    with st.form("form_editar_conta"):
        st.markdown(f"**Editando:** {conta['Descricao']}")
        
        col_val, col_venc = st.columns(2)
        with col_val:
            novo_val = st.number_input("Valor (R$)", min_value=0.0, value=float(conta['Valor']), format="%.2f")
        with col_venc:
            data_venc_obj = datetime.datetime.strptime(conta['Vencimento'], "%d/%m/%Y").date()
            novo_venc = st.date_input("Vencimento", value=data_venc_obj, format="DD/MM/YYYY")
            
        nova_obs = st.text_input("Observação", value=conta.get('Observacao', ''))
        
        if st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True):
            if gs.editar_conta(conta['ID_Unico'], conta['Descricao'], novo_val, novo_venc.strftime("%d/%m/%Y"), nova_obs):
                st.rerun()

@st.dialog("Excluir Conta")
def modal_excluir(conta_id, descricao):
    st.warning(f"Tem certeza que deseja excluir a conta **{descricao}**? Essa ação não pode ser desfeita.")
    if st.button("Sim, Excluir", type="primary", use_container_width=True):
        if gs.excluir_conta(conta_id):
            st.rerun()

# ---------------- TELA DE LOGIN ----------------
if not st.session_state["logado"]:
    st.markdown("<h2 style='text-align: center;'>💰 Contas a Pagar</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Acesse sua conta para gerenciar suas finanças</p>", unsafe_allow_html=True)
    
    tab_login, tab_cadastro = st.tabs(["🔒 Login", "📝 Criar Conta"])
    
    with tab_login:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", type="primary", use_container_width=True):
            if gs.autenticar_usuario(email, senha):
                st.session_state["logado"] = True
                st.session_state["usuario"] = email.lower()
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")
                
    with tab_cadastro:
        cad_email = st.text_input("E-mail", key="cad_email")
        cad_senha = st.text_input("Senha", type="password", key="cad_senha")
        cad_senha2 = st.text_input("Confirme a Senha", type="password", key="cad_senha2")
        if st.button("Cadastrar", type="primary", use_container_width=True):
            if not cad_email or not cad_senha: st.warning("Preencha tudo.")
            elif cad_senha != cad_senha2: st.error("Senhas não coincidem.")
            elif gs.cadastrar_usuario(cad_email, cad_senha): st.success("Conta criada! Faça o login.")
            else: st.error("E-mail já cadastrado.")
    st.stop()

# ---------------- TELA PRINCIPAL ----------------
# Topo: Usuário e Logout (Agora dentro de um Expander)
with st.expander("👤 Conta e Configurações", expanded=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h5 style='margin-top: 10px;'>👤 {st.session_state['usuario']}</h5>", unsafe_allow_html=True)
    with col2:
        if st.button("Sair", use_container_width=True, key="btn_sair"):
            st.session_state["logado"] = False
            st.session_state["usuario"] = ""
            st.rerun()

# Cabeçalho do Mês
with st.container(key="nav_mes"):
    col_prev, col_titulo, col_next = st.columns([1, 3, 1])
    
    with col_prev:
        if st.button("◀", use_container_width=True, key="btn_prev"):
            st.session_state["mes_atual"] -= relativedelta(months=1)
            st.rerun()

    with col_titulo:
        nome_mes = st.session_state["mes_atual"].strftime("%B/%Y").capitalize()
        meses_pt = {"January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"}
        for en, pt in meses_pt.items():
            if en in nome_mes: nome_mes = nome_mes.replace(en, pt)
        st.markdown(f"<h4 style='text-align: center; margin: 0; font-size: 18px; color: #0d6efd; font-weight: bold;'>{nome_mes}</h4>", unsafe_allow_html=True)

    with col_next:
        if st.button("▶", use_container_width=True, key="btn_next"):
            st.session_state["mes_atual"] += relativedelta(months=1)
            st.rerun()

st.write("")

mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
contas_do_mes = gs.carregar_contas(st.session_state["usuario"], mes_busca)

# Calcula os totais
total_mes = sum(float(c['Valor']) for c in contas_do_mes)
total_pago = sum(float(c['Valor']) for c in contas_do_mes if c['Status'] == 'Pago')
total_pendente = total_mes - total_pago

# --- CARDS DE RESUMO ---
def fmt_moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown(f"""
<div style="display: flex; justify-content: space-between; gap: 8px; margin-bottom: 15px;">
    <div style="flex: 1; background: #e3f2fd; padding: 12px 5px; border-radius: 10px; text-align: center; border: 1px solid #b6d4fe;">
        <div style="font-size: 11px; color: #0d6efd; font-weight: 700; text-transform: uppercase;">A Pagar</div>
        <div style="font-size: 15px; font-weight: 800; color: #0d6efd;">{fmt_moeda(total_mes)}</div>
    </div>
    <div style="flex: 1; background: #d4edda; padding: 12px 5px; border-radius: 10px; text-align: center; border: 1px solid #c3e6cb;">
        <div style="font-size: 11px; color: #155724; font-weight: 700; text-transform: uppercase;">Pago</div>
        <div style="font-size: 15px; font-weight: 800; color: #155724;">{fmt_moeda(total_pago)}</div>
    </div>
    <div style="flex: 1; background: #fff3cd; padding: 12px 5px; border-radius: 10px; text-align: center; border: 1px solid #ffe69c;">
        <div style="font-size: 11px; color: #856404; font-weight: 700; text-transform: uppercase;">Pendente</div>
        <div style="font-size: 15px; font-weight: 800; color: #856404;">{fmt_moeda(total_pendente)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- BOTÃO ADICIONAR CONTA ---
if st.button("➕ Adicionar Nova Conta", type="primary", use_container_width=True):
    modal_adicionar()

st.write("")

# --- LISTA DE CONTAS DO MÊS ---
if not contas_do_mes:
    st.info("Nenhuma conta cadastrada para este mês.")
else:
    for conta in contas_do_mes:
        valor_fmt = fmt_moeda(float(conta['Valor']))
        
        with st.container(border=True):
            # Linha 1: Descrição e Valor
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="font-weight: 700; font-size: 16px; color: #333;">{conta['Descricao']}</div>
                <div style="font-weight: 700; font-size: 16px; color: #0d6efd;">{valor_fmt}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Linha 2: Vencimento e Status (com a label STATUS acima)
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 5px;">
                <div style="font-size: 12px; color: #6c757d; margin-bottom: 2px;">📅 Vence: {conta['Vencimento']}</div>
                <div style="text-align: right;">
                    <div style="font-size: 9px; color: #adb5bd; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">STATUS</div>
                    <div>
                        {'<span style="background:#d4edda; color:#155724; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👍 PAGO</span>' if conta['Status'] == 'Pago' else '<span style="background:#fff3cd; color:#856404; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👎 A PAGAR</span>'}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if conta['Status'] == 'Pago' and conta.get('Data_Pagamento'):
                 st.markdown(f"<div style='font-size: 12px; color: #6c757d; margin-top: 8px;'>💵 Pago em: {conta['Data_Pagamento']}</div>", unsafe_allow_html=True)
            
            if conta.get('Observacao'):
                st.markdown(f"<div style='font-size: 12px; color: #6c757d; margin-top: 5px;'>📝 {conta['Observacao']}</div>", unsafe_allow_html=True)
            
            st.write("")
            
            # --- BOTÕES DE AÇÃO ---
            btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
            
            with btn_col1:
                if conta['Status'] == 'Pendente':
                    if st.button("✅ Pagar", key=f"btn_pagar_{conta['ID_Unico']}", use_container_width=True, type="primary"):
                        modal_pagar(conta['ID_Unico'], float(conta['Valor']))
                else:
                    if st.button("↩️ Desmarcar", key=f"btn_desmarcar_{conta['ID_Unico']}", use_container_width=True):
                        if gs.atualizar_status_conta(conta['ID_Unico'], "Pendente", ""):
                            st.rerun()
                            
            with btn_col2:
                if st.button("✏️ Editar", key=f"btn_edit_{conta['ID_Unico']}", use_container_width=True):
                    modal_editar(conta)
                    
            with btn_col3:
                if st.button("🗑️ Excluir", key=f"btn_del_{conta['ID_Unico']}", use_container_width=True):
                    modal_excluir(conta['ID_Unico'], conta['Descricao'])