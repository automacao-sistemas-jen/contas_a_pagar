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
    
    /* 1. Bordas dos inputs e Expander */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stDateInput"] > div,
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 1.2px solid #0d6efd !important;
        border-radius: 8px !important;
        transition: all 0.25s ease-in-out !important;
    }
    div[data-testid="stTextInput"] > div:focus-within,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stDateInput"] > div:focus-within,
    div[data-testid="stSelectbox"] > div:focus-within,
    div[data-testid="stNumberInput"] > div:focus-within {
        border-color: #198754 !important;
        box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.15) !important;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stDateInput"] input, div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Borda do Expander */
    div[data-testid="stExpander"] {
        border: 1.2px solid #0d6efd !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    /* 2. Cor do botão Sair */
    div.st-key-btn_sair button { background-color: #dc3545 !important; border: 1px solid #dc3545 !important; }
    div.st-key-btn_sair button * { color: white !important; }

    /* 3. Cabeçalho do Mês (Reduzido) */
    div[class*="st-key-nav_mes"] div[data-testid="stHorizontalBlock"] { 
        background-color: #e3f2fd !important; 
        border-radius: 10px !important;
        padding: 3px 8px !important; /* Reduzido */
        display: flex !important; 
        flex-direction: row !important;
        flex-wrap: nowrap !important; 
        align-items: center !important;
        justify-content: space-between !important;
    }
    div[class*="st-key-nav_mes"] div[data-testid="stColumn"] { padding: 0 !important; min-width: 0 !important; }
    div[class*="st-key-nav_mes"] button { 
        background-color: #0d6efd !important; border: 1px solid #0d6efd !important; 
        height: 32px !important; /* Reduzido de 38 para 32 */
        padding: 0 !important; width: 100% !important; font-size: 12px !important;
    }
    div[class*="st-key-nav_mes"] button * { color: white !important; }
    div[class*="st-key-nav_mes"] h4 {
        padding-top: 5px !important;
        font-size: 15px !important; /* Fonte um pouco menor */
    }

    /* 4. Força a linha de botões (Pagar, Editar, Excluir) a ficar lado a lado e mais fina */
    div[class*="st-key-btn_row_"] div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 4px !important;
    }
    div[class*="st-key-btn_row_"] div[data-testid="stColumn"] {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important;
    }
    div[class*="st-key-btn_row_"] button {
        font-size: 11px !important; 
        height: 30px !important; /* Força altura fixa menor */
        min-height: 30px !important;
        padding: 0 !important; 
        width: 100% !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    /* 🎯 Borda e Destaque no Checkbox */
    div[data-testid="stCheckbox"] {
        background-color: #f8f9fa !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: 1.2px solid #0d6efd !important;
        margin-bottom: 12px !important;
    }
    
    /* Deixa o quadradinho do checkbox com borda visível */
    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] > div:first-child {
        border: 2px solid #0d6efd !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
    }
    
    /* Deixa o texto do checkbox azul e em negrito */
    div[data-testid="stCheckbox"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #0d6efd !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- ESTADOS DA SESSÃO ----------------
if "logado" not in st.session_state: st.session_state["logado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = ""
if "mes_atual" not in st.session_state: st.session_state["mes_atual"] = datetime.date.today().replace(day=1)

BANCOS = ["", "Banco do Brasil", "Bradesco", "C6 Bank", "Caixa", "Dinheiro", "Inter", "Itaú", "Nubank", "PicPay", "Santander", "Sicredi"]

# ---------------- MODAIS ----------------
@st.dialog("Confirmar Pagamento")
def modal_pagar(conta_id, valor):
    st.write(f"Deseja confirmar o pagamento de **R$ {valor:.2f}**?")
    data_pag = st.date_input("Data do Pagamento", value=datetime.date.today(), format="DD/MM/YYYY")
    
    # Checkbox para cadastrar novo banco na hora do pagamento
    novo_banco = st.checkbox("Cadastrar novo banco")
    
    if novo_banco:
        banco_final = st.text_input("Digite o nome do banco")
    else:
        banco_final = st.selectbox("Banco utilizado", BANCOS)
    
    if st.button("Confirmar e Pagar", type="primary", use_container_width=True):
        if gs.atualizar_status_conta(conta_id, "Pago", data_pag.strftime("%d/%m/%Y"), banco_final):
            st.rerun()

@st.dialog("Adicionar Nova Conta")
def modal_adicionar():
    sugestoes = gs.obter_descricoes_usuario(st.session_state["usuario"])
    
    nova_conta = st.checkbox("Cadastrar nova conta")
    
    if nova_conta:
        desc = st.text_input("Digite o nome da nova conta")
    else:
        if not sugestoes:
            st.warning("Nenhuma conta cadastrada. Marque a caixa acima para criar a primeira.")
            desc = ""
        else:
            desc = st.selectbox("Selecione uma conta", sugestoes)
    
    col_val, col_venc = st.columns(2)
    with col_val:
        val_input = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", value=None, placeholder="0,00")
    with col_venc:
        proximo_mes = st.session_state["mes_atual"] + relativedelta(months=1)
        ultimo_dia = proximo_mes - datetime.timedelta(days=1)
        venc = st.date_input("Vencimento", value=ultimo_dia, format="DD/MM/YYYY")
        
    obs = st.text_input("Observação (Opcional)")
    mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
    
    if st.button("Salvar Conta", type="primary", use_container_width=True):
        val_final = val_input if val_input is not None else 0.0
        if not desc:
            st.error("Por favor, preencha ou selecione uma conta.")
        else:
            if gs.salvar_conta(st.session_state["usuario"], mes_busca, desc, val_final, venc.strftime("%d/%m/%Y"), obs):
                st.rerun()

@st.dialog("Editar Conta")
def modal_editar(conta):
    st.markdown(f"**Editando:** {conta['Descricao']}")
    
    col_val, col_venc = st.columns(2)
    with col_val:
        val_atual = float(conta['Valor'])
        val_input = st.number_input("Valor (R$)", min_value=0.0, value=val_atual if val_atual > 0 else None, format="%.2f", placeholder="0,00")
    with col_venc:
        data_venc_obj = datetime.datetime.strptime(conta['Vencimento'], "%d/%m/%Y").date()
        novo_venc = st.date_input("Vencimento", value=data_venc_obj, format="DD/MM/YYYY")
    
    # Lógica inteligente do Banco
    banco_salvo = conta.get('Banco', '')
    
    # Se o banco salvo existir, mas não estiver na lista padrão, já abre o checkbox preenchido
    if banco_salvo and banco_salvo not in BANCOS:
        novo_banco = st.checkbox("Cadastrar novo banco", value=True)
        banco_final = st.text_input("Digite o nome do banco", value=banco_salvo)
    else:
        novo_banco = st.checkbox("Cadastrar novo banco")
        if novo_banco:
            banco_final = st.text_input("Digite o nome do banco")
        else:
            # Se estiver vazio ou na lista, seleciona a opção correta
            idx_banco = BANCOS.index(banco_salvo) if banco_salvo in BANCOS else 0
            banco_final = st.selectbox("Banco utilizado", BANCOS, index=idx_banco)
        
    nova_obs = st.text_input("Observação", value=conta.get('Observacao', ''))
    
    if st.button("Salvar Alterações", type="primary", use_container_width=True):
        val_final = val_input if val_input is not None else 0.0
        if gs.editar_conta(conta['ID_Unico'], conta['Descricao'], val_final, novo_venc.strftime("%d/%m/%Y"), nova_obs, banco_final):
            st.rerun()

@st.dialog("Excluir Conta")
def modal_excluir(conta_id, descricao):
    st.warning(f"Tem certeza que deseja excluir a conta **{descricao}**?")
    if st.button("Sim, Excluir", type="primary", use_container_width=True):
        if gs.excluir_conta(conta_id):
            st.rerun()

# ---------------- TELA DE LOGIN ----------------
if not st.session_state["logado"]:
    st.markdown("<h2 style='text-align: center;'>💰 Contas a Pagar</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Acesse sua conta</p>", unsafe_allow_html=True)
    
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
            elif gs.cadastrar_usuario(cad_email, cad_senha): st.success("Conta criada!")
            else: st.error("E-mail já cadastrado.")
    st.stop()

# ---------------- TELA PRINCIPAL ----------------
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
    col_prev, col_titulo, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.button("◀ Anterior", key="btn_prev", use_container_width=True):
            st.session_state["mes_atual"] -= relativedelta(months=1)
            st.rerun()
            
    with col_titulo:
        nome_mes = st.session_state["mes_atual"].strftime("%B/%Y").capitalize()
        meses_pt = {"January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"}
        for en, pt in meses_pt.items():
            if en in nome_mes: nome_mes = nome_mes.replace(en, pt)
        st.markdown(f"<h4 style='text-align: center; margin: 0; font-size: 15px; color: #0d6efd; font-weight: bold; padding-top: 6px;'>{nome_mes}</h4>", unsafe_allow_html=True)
            
    with col_next:
        if st.button("Próximo ▶", key="btn_next", use_container_width=True):
            st.session_state["mes_atual"] += relativedelta(months=1)
            st.rerun()

st.write("")

mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
contas_do_mes = gs.carregar_contas(st.session_state["usuario"], mes_busca)

total_mes = sum(float(c['Valor']) for c in contas_do_mes)
total_pago = sum(float(c['Valor']) for c in contas_do_mes if c['Status'] == 'Pago')
total_pendente = total_mes - total_pago

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

if st.button("➕ Adicionar Nova Conta", type="primary", use_container_width=True):
    modal_adicionar()

st.write("")

# --- LISTA DE CONTAS DO MÊS ---
if not contas_do_mes:
    st.info("Nenhuma conta cadastrada para este mês.")
else:
    for conta in contas_do_mes:
        valor_fmt = fmt_moeda(float(conta['Valor']))
        
        # Define as cores dinâmicas
        if conta['Status'] == 'Pago':
            bg_color, border_color = "#d4edda", "#198754"
            btn_bg, btn_border = "#198754", "#198754"
            selo = '<span style="background:#198754; color:#fff; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👍 PAGO</span>'
        else:
            bg_color, border_color = "#f8d7da", "#dc3545"
            btn_bg, btn_border = "#dc3545", "#dc3545"
            selo = '<span style="background:#dc3545; color:#fff; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👎 A PAGAR</span>'
            
        # Injeta o CSS específico para ESTE card e SEUS botões
        st.markdown(f"""
        <style>
        div[class*="st-key-card_{conta['ID_Unico']}"] {{
            background-color: {bg_color} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 10px !important;
            padding: 12px !important;
            margin-bottom: 10px !important;
        }}
        /* Pinta todos os botões dentro deste card específico */
        div[class*="st-key-card_{conta['ID_Unico']}"] div[class*="st-key-btn_row_"] button {{
            background-color: {btn_bg} !important;
            border-color: {btn_border} !important;
        }}
        div[class*="st-key-card_{conta['ID_Unico']}"] div[class*="st-key-btn_row_"] button * {{
            color: white !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        with st.container(key=f"card_{conta['ID_Unico']}"):
            
            # Cabeçalho: Descrição e Valor
            st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;'><div style='font-weight: 700; font-size: 16px; color: #000;'>{conta['Descricao']}</div><div style='font-weight: 700; font-size: 16px; color: #0d6efd;'>{valor_fmt}</div></div>", unsafe_allow_html=True)
            
            # Bloco Esquerdo (Vencimento, Pago em, Banco)
            bloco_esq = f"<div style='font-size: 12px; color: #000;'>📅 Vence: <b>{conta['Vencimento']}</b></div>"
            if conta['Status'] == 'Pago' and conta.get('Data_Pagamento'):
                bloco_esq += f"<div style='font-size: 12px; color: #000;'>💵 Pago em: <b>{conta['Data_Pagamento']}</b></div>"
                if conta.get('Banco'):
                    bloco_esq += f"<div style='font-size: 12px; color: #000;'>🏦 Banco: <b>{conta['Banco']}</b></div>"
            
            # Bloco Direito (Status e Observação)
            bloco_dir = f"<div style='text-align: right;'><div style='font-size: 9px; color: #333; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;'>STATUS</div><div>{selo}</div></div>"
            
            # Observação com fonte preta e visível
            if conta.get('Observacao'):
                bloco_dir += f"<div style='font-size: 12px; color: #000; text-align: right; margin-top: 6px; word-break: break-word;'>📝 <b>{conta['Observacao']}</b></div>"

            st.markdown(f"<div style='display: flex; justify-content: space-between;'><div style='display: flex; flex-direction: column; gap: 6px;'>{bloco_esq}</div><div style='display: flex; flex-direction: column; align-items: flex-end;'>{bloco_dir}</div></div>", unsafe_allow_html=True)
            
            st.write("")
            
            with st.container(key=f"btn_row_{conta['ID_Unico']}"):
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if conta['Status'] == 'Pendente':
                        if st.button("✅ Pagar", key=f"btn_pagar_{conta['ID_Unico']}", use_container_width=True):
                            modal_pagar(conta['ID_Unico'], float(conta['Valor']))
                    else:
                        if st.button("↩️ Desmarcar", key=f"btn_desmarcar_{conta['ID_Unico']}", use_container_width=True):
                            if gs.atualizar_status_conta(conta['ID_Unico'], "Pendente", "", ""):
                                st.rerun()
                                
                with btn_col2:
                    if st.button("✏️ Editar", key=f"btn_edit_{conta['ID_Unico']}", use_container_width=True):
                        modal_editar(conta)
                        
                with btn_col3:
                    if st.button("🗑️ Excluir", key=f"btn_del_{conta['ID_Unico']}", use_container_width=True):
                        modal_excluir(conta['ID_Unico'], conta['Descricao'])