import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from fpdf import FPDF
from services import google_sheets as gs
from decimal import Decimal, InvalidOperation

st.cache_data.clear()

st.set_page_config(page_title="Contas a Pagar", page_icon="💰", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; max-width: 600px; }

    div[class*="st-key-main_box"] {
        border: 2px solid #0d6efd !important; 
        border-radius: 12px !important;
        padding: 15px !important;
        background-color: #ffffff !important;
    }

    div[class*="st-key-modal_box"] {
        border: 1.2px solid #0d6efd !important;
        border-radius: 10px !important;
        padding: 15px !important;
        background-color: #f8f9fa !important;
        margin-bottom: 10px !important;
    }

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

    div[class*="st-key-nav_icons"] div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 6px !important; margin-top: 10px !important; margin-bottom: 10px !important;
    }
    div[class*="st-key-nav_icons"] div[data-testid="stColumn"] {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important;
    }
    div[class*="st-key-nav_icons"] button {
        background-color: #e3f2fd !important; 
        border: 1px solid #90caf9 !important; 
        border-radius: 8px !important;
        height: 42px !important; padding: 0 !important; font-size: 20px !important;
    }
    div[class*="st-key-nav_icons"] button * { color: #0d6efd !important; }

    div[class*="st-key-nav_mes"] div[data-testid="stHorizontalBlock"] { 
        background-color: #e3f2fd !important; border-radius: 10px !important;
        padding: 2px 6px !important; display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; align-items: center !important; justify-content: space-between !important;
    }
    div[class*="st-key-nav_mes"] div[data-testid="stColumn"] { padding: 0 !important; min-width: 0 !important; }
    div[class*="st-key-nav_mes"] button { 
        background-color: #0d6efd !important; border: 1px solid #0d6efd !important; 
        height: 30px !important; min-height: 30px !important;
        padding: 0 !important; width: 100% !important; font-size: 12px !important;
    }
    div[class*="st-key-nav_mes"] button * { color: white !important; }
    div[class*="st-key-nav_mes"] h4 { padding-top: 5px !important; font-size: 14px !important; }

    div[class*="st-key-btn_row_"] div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important;
    }
    div[class*="st-key-btn_row_"] div[data-testid="stColumn"] {
        min-width: 0 !important; padding: 0 !important;
    }
    div[class*="st-key-btn_row_"] button {
        font-size: 10px !important; 
        height: 28px !important; 
        min-height: 28px !important;
        padding: 0 2px !important; 
        width: 100% !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }

    div[class*="st-key-btn_limpar_modal"] button {
        background-color: #dc3545 !important; 
        border: 1px solid #dc3545 !important;
    }
    div[class*="st-key-btn_limpar_modal"] button * { color: white !important; }

    div[class*="st-key-btn_limpar_topo"] button {
        background-color: #dc3545 !important; 
        border: 1px solid #dc3545 !important;
    }
    div[class*="st-key-btn_limpar_topo"] button * { color: white !important; }

    div[data-testid="stCheckbox"] {
        background-color: #f8f9fa !important; padding: 8px 12px !important;
        border-radius: 8px !important; border: 1.2px solid #0d6efd !important; margin-bottom: 12px !important;
    }
    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] > div:first-child {
        border: 2px solid #0d6efd !important; border-radius: 4px !important; background-color: #ffffff !important;
    }
    div[data-testid="stCheckbox"] p { font-size: 15px !important; font-weight: 600 !important; color: #0d6efd !important; }

    div[class*="st-key-btn_sair"] button { background-color: #dc3545 !important; border: 1px solid #dc3545 !important; }
    div[class*="st-key-btn_sair"] button * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- ESTADOS DA SESSÃO ----------------
if "logado" not in st.session_state: st.session_state["logado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = ""
if "mes_atual" not in st.session_state: st.session_state["mes_atual"] = datetime.date.today().replace(day=1)
if "filtro_ativo" not in st.session_state: st.session_state["filtro_ativo"] = False
if "ordem_padrao" not in st.session_state: st.session_state["ordem_padrao"] = "pendente"

BANCOS = ["", "Banco do Brasil", "Bradesco", "C6 Bank", "Caixa", "Dinheiro", "Inter", "Itaú", "Nubank", "PicPay", "Santander", "Sicredi"]

def obter_nome_mes_atual():
    nome_mes = st.session_state["mes_atual"].strftime("%B de %Y").capitalize()
    meses_en = {"January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"}
    for en, pt in meses_en.items():
        if en in nome_mes: nome_mes = nome_mes.replace(en, pt)
    return nome_mes

def parse_valor(txt):
    if not txt or not str(txt).strip():
        raise ValueError("Informe o valor da conta.")
    s = str(txt).strip().replace("R$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(s).quantize(Decimal("0.01"))
        if not valor.is_finite() or valor <= 0:
            raise ValueError("Informe um valor maior que zero.")
        return float(valor)
    except (InvalidOperation, ValueError):
        raise ValueError("Valor inválido. Exemplo: 100,50.")

def sanitizar_pdf(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf(contas, periodo_txt=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Relatorio de Contas a Pagar", ln=True, align="C")
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Referencia: {sanitizar_pdf(periodo_txt)}", ln=True, align="C")
    
    t_total = sum(float(c.get('Valor', 0)) for c in contas)
    t_pago = sum(float(c.get('Valor', 0)) for c in contas if c.get('Status') == 'Pago')
    t_pend = t_total - t_pago
    
    def fmt_pdf(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    pdf.ln(3)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(63, 8, f"Total Geral: {fmt_pdf(t_total)}", align="C")
    pdf.set_text_color(0, 128, 0)
    pdf.cell(63, 8, f"Total Pago: {fmt_pdf(t_pago)}", align="C")
    pdf.set_text_color(200, 0, 0)
    pdf.cell(63, 8, f"Total Pendente: {fmt_pdf(t_pend)}", align="C", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(70, 8, "Descricao", border=1, fill=True)
    pdf.cell(25, 8, "Vencimento", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Pagamento", border=1, fill=True, align="C")
    pdf.cell(22, 8, "Status", border=1, fill=True, align="C")
    pdf.cell(28, 8, "Valor", border=1, fill=True, align="C")
    pdf.cell(20, 8, "Banco", border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    for c in contas:
        valor = float(c.get('Valor', 0))
        val_fmt = fmt_pdf(valor)
        desc = sanitizar_pdf(c.get('Descricao', ''))[:38]
        venc = sanitizar_pdf(c.get('Vencimento', ''))
        pag = sanitizar_pdf(c.get('Data_Pagamento', '-')) if c.get('Data_Pagamento') else '-'
        status = sanitizar_pdf(c.get('Status', ''))
        banco = sanitizar_pdf(c.get('Banco', ''))[:14]
        
        pdf.cell(70, 8, desc, border=1)
        pdf.cell(25, 8, venc, border=1, align="C")
        pdf.cell(25, 8, pag, border=1, align="C")
        pdf.cell(22, 8, status, border=1, align="C")
        pdf.cell(28, 8, val_fmt, border=1, align="R")
        pdf.cell(20, 8, banco, border=1)
        pdf.ln()
    
    pdf.ln(5)
    return bytes(pdf.output())

@st.dialog("Confirmar Pagamento")
def modal_pagar(conta_id, valor):
    with st.container(key="modal_box"):
        st.write(f"Deseja confirmar o pagamento de **R$ {valor:.2f}**?")
        data_pag = st.date_input("Data do Pagamento", value=datetime.date.today(), format="DD/MM/YYYY")
        novo_banco = st.checkbox("Cadastrar novo banco")
        if novo_banco:
            banco_final = st.text_input("Digite o nome do banco")
        else:
            banco_final = st.selectbox("Banco utilizado", BANCOS)
    if st.button("Confirmar e Pagar", type="primary", use_container_width=True):
        if gs.atualizar_status_conta(conta_id, "Pago", data_pag.strftime("%d/%m/%Y"), banco_final):
            st.rerun()

@st.dialog(f"Nova Conta para {obter_nome_mes_atual()}")
def modal_adicionar():
    sugestoes = gs.obter_descricoes_usuario(st.session_state["usuario"])
    nova_conta = st.checkbox("Cadastrar nova conta")
    
    with st.container(key="modal_box"):
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
            val_str = st.text_input("Valor (R$)", placeholder="0,00")
        with col_venc:
            proximo_mes = st.session_state["mes_atual"] + relativedelta(months=1)
            ultimo_dia = proximo_mes - datetime.timedelta(days=1)
            venc = st.date_input("Vencimento", value=ultimo_dia, format="DD/MM/YYYY")
            
        obs = st.text_input("Observação (Opcional)")
    
    mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
    
    if st.button("Salvar Conta", type="primary", use_container_width=True):
        try:
            val_final = parse_valor(val_str)
            if not desc:
                st.error("Por favor, preencha ou selecione uma conta.")
            else:
                if gs.salvar_conta(st.session_state["usuario"], mes_busca, desc, val_final, venc.strftime("%d/%m/%Y"), obs):
                    st.rerun()
                else:
                    st.error("Não foi possível salvar a conta.")
        except ValueError as e:
            st.error(str(e))

@st.dialog("Editar Conta")
def modal_editar(conta):
    st.markdown(f"**Editando:** {conta.get('Descricao', '')}")
    
    with st.container(key="modal_box"):
        col_val, col_venc = st.columns(2)
        with col_val:
            val_atual = float(conta.get('Valor', 0))
            val_str_atual = f"{val_atual:.2f}".replace(".", ",")
            val_str = st.text_input("Valor (R$)", value=val_str_atual)
        with col_venc:
            data_venc_obj = datetime.datetime.strptime(conta.get('Vencimento', ''), "%d/%m/%Y").date()
            novo_venc = st.date_input("Vencimento", value=data_venc_obj, format="DD/MM/YYYY")
        banco_salvo = conta.get('Banco', '')
        if banco_salvo and banco_salvo not in BANCOS:
            novo_banco = st.checkbox("Cadastrar novo banco", value=True)
            banco_final = st.text_input("Digite o nome do banco", value=banco_salvo)
        else:
            novo_banco = st.checkbox("Cadastrar novo banco")
            if novo_banco:
                banco_final = st.text_input("Digite o nome do banco")
            else:
                idx_banco = BANCOS.index(banco_salvo) if banco_salvo in BANCOS else 0
                banco_final = st.selectbox("Banco utilizado", BANCOS, index=idx_banco)
        nova_obs = st.text_input("Observação", value=conta.get('Observacao', ''))
    
    if st.button("Salvar Alterações", type="primary", use_container_width=True):
        try:
            val_final = parse_valor(val_str)
            if gs.editar_conta(conta.get('ID_Unico'), conta.get('Descricao', ''), val_final, novo_venc.strftime("%d/%m/%Y"), nova_obs, banco_final):
                st.rerun()
            else:
                st.error("Não foi possível salvar as alterações.")
        except ValueError as e:
            st.error(str(e))

@st.dialog("Copiar Conta")
def modal_copiar(conta):
    valor = float(conta.get('Valor', 0))
    st.write(f"Copiar **{conta.get('Descricao', '')}** (R$ {valor:.2f}) para os próximos meses.")
    qtd = st.number_input("Para quantos meses deseja copiar?", min_value=1, max_value=12, value=1)
    
    if st.button("Confirmar Cópia", type="primary", use_container_width=True):
        with st.spinner("Copiando..."):
            data_venc_obj = datetime.datetime.strptime(conta.get('Vencimento', ''), "%d/%m/%Y").date()
            for i in range(1, int(qtd)+1):
                novo_mes = st.session_state["mes_atual"] + relativedelta(months=i)
                mes_busca = novo_mes.strftime("%Y-%m")
                nova_data_venc = data_venc_obj + relativedelta(months=i)
                gs.salvar_conta(st.session_state["usuario"], mes_busca, conta.get('Descricao', ''), valor, nova_data_venc.strftime("%d/%m/%Y"), conta.get('Observacao', ''))
            st.success("Copiado com sucesso!")
            st.rerun()

@st.dialog("Excluir Conta")
def modal_excluir(conta_id, descricao):
    st.warning(f"Tem certeza que deseja excluir a conta **{descricao}**?")
    if st.button("Sim, Excluir", type="primary", use_container_width=True):
        if gs.excluir_conta(conta_id):
            st.rerun()

@st.dialog("⚙️ Configurações e Ajuda")
def modal_configuracoes():
    st.markdown(f"**Usuário Logado:** {st.session_state['usuario']}")
    if st.button("🚪 Sair do App", type="primary", use_container_width=True, key="btn_sair"):
        st.session_state["logado"] = False
        st.rerun()
    st.divider()
    tab_sobre, tab_como, tab_creditos = st.tabs(["Sobre", "Como Usar", "Tecnologias"])
    
    with tab_sobre:
        st.markdown("### 💰 Contas a Pagar JEN")
        st.markdown("**Versão:** 1.3")
        st.markdown("O melhor gerenciador de contas pessoais. Organize seus pagamentos, acompanhe seus gastos e nunca perca um vencimento.")
        st.write("")
        st.markdown("**Desenvolvido em:** Novembro / 2026")
        st.markdown("**Contato:** automacaodesistemas.jen@gmail.com")
        
    with tab_como:
        st.markdown("Conheça as funcionalidades de cada botão:")
        st.markdown("**➕ Adicionar:** Inclui uma nova conta no mês selecionado ou em meses futuros.")
        st.markdown("**🔍 Filtros:** Pesquisa contas em qualquer período, banco, status ou descrição.")
        st.markdown("**⇧ Ordenar:** Alterna entre Pagos no topo (botão verde) e Pendentes no topo (botão vermelho). A preferência é salva automaticamente.")
        st.markdown("**📊 Relatório:** Gera um PDF completo com as contas exibidas na tela.")
        st.markdown("**Marcar Pago/Desmarcar:** Altera o status da conta e registra a data e banco de pagamento.")
        st.markdown("**Editar:** Modifica o valor, vencimento, banco ou observação de uma conta.")
        st.markdown("**Copiar:** Duplica a conta para os próximos meses, ajustando os vencimentos.")
        st.markdown("**Excluir:** Remove a conta definitivamente.")
        
    with tab_creditos:
        st.markdown("**Desenvolvido por:** João Evangelista Neto")
        st.markdown("**Tecnologias Utilizadas:**")
        st.markdown("- **Python:** Linguagem base do projeto.")
        st.markdown("- **Streamlit:** Framework para a interface visual.")
        st.markdown("- **Pandas:** Manipulação dos dados.")
        st.markdown("- **Google Sheets API:** Armazenamento em nuvem.")
        st.markdown("- **FPDF:** Geração dos relatórios em PDF.")

@st.dialog("🔍 Filtros Avançados")
def modal_filtros():
    with st.container(key="modal_box"):
        sugestoes = gs.obter_descricoes_usuario(st.session_state["usuario"])
        f_desc = st.selectbox("Descrição", [""] + sugestoes)
        
        hoje = datetime.date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_data_ini = st.date_input("Data Inicial", value=primeiro_dia_mes, format="DD/MM/YYYY", key="f_ini")
        with col_f2:
            f_data_fim = st.date_input("Data Final", value=hoje, format="DD/MM/YYYY", key="f_fim")
            
        col_f3, col_f4 = st.columns(2)
        with col_f3:
            f_banco = st.selectbox("Banco", ["Todos"] + BANCOS[1:])
        with col_f4:
            f_status = st.selectbox("Status", ["Todos", "Pago", "Pendente"])
    
    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Aplicar Filtros", type="primary", use_container_width=True):
            st.session_state["filtro_ativo"] = True
            st.session_state["f_desc"] = f_desc
            st.session_state["f_data_ini"] = f_data_ini
            st.session_state["f_data_fim"] = f_data_fim
            st.session_state["f_banco"] = f_banco
            st.session_state["f_status"] = f_status
            st.session_state["modal_filtro_aberto"] = False
            st.rerun()
    with col_btn2:
        if st.button("Limpar Filtros", use_container_width=True, key="btn_limpar_modal"):
            st.session_state["filtro_ativo"] = False
            st.session_state["f_desc"] = None
            st.session_state["f_data_ini"] = None
            st.session_state["f_data_fim"] = None
            st.session_state["f_banco"] = None
            st.session_state["f_status"] = None
            st.session_state["modal_filtro_aberto"] = False
            st.rerun()

# ---------------- TELA DE LOGIN ----------------
if not st.session_state["logado"]:
    st.markdown("<h2 style='text-align: center;'>💰 Contas a Pagar</h2>", unsafe_allow_html=True)
    tab_login, tab_cadastro = st.tabs(["🔒 Login", "📝 Criar Conta"])
    with tab_login:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", type="primary", use_container_width=True):
            if gs.autenticar_usuario(email, senha):
                st.session_state["logado"] = True
                st.session_state["usuario"] = email.lower()
                st.session_state["ordem_padrao"] = gs.carregar_preferencia_ordem(email.lower())
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

# ---------------- LÓGICA DE DADOS ----------------
if st.session_state["filtro_ativo"]:
    todas_contas = gs.carregar_todas_contas(st.session_state["usuario"])
    if not todas_contas:
        contas_exibicao = []
    else:
        df = pd.DataFrame(todas_contas)
        if 'Valor' not in df.columns:
            df['Valor'] = 0.0
        df['Data_Venc_Obj'] = pd.to_datetime(df['Vencimento'], format='%d/%m/%Y', errors='coerce')
        if st.session_state.get("f_desc") and st.session_state["f_desc"] != "":
            df = df[df['Descricao'].str.contains(st.session_state["f_desc"], case=False, na=False)]
        if st.session_state.get("f_data_ini"):
            df = df[df['Data_Venc_Obj'].dt.date >= st.session_state["f_data_ini"]]
        if st.session_state.get("f_data_fim"):
            df = df[df['Data_Venc_Obj'].dt.date <= st.session_state["f_data_fim"]]
        if st.session_state.get("f_banco") and st.session_state["f_banco"] != "Todos":
            df = df[df['Banco'] == st.session_state["f_banco"]]
        if st.session_state.get("f_status") and st.session_state["f_status"] != "Todos":
            df = df[df['Status'] == st.session_state["f_status"]]
        contas_exibicao = df.to_dict('records')
else:
    mes_busca = st.session_state["mes_atual"].strftime("%Y-%m")
    contas_exibicao = gs.carregar_contas(st.session_state["usuario"], mes_busca)

def _parse_data(v):
    try: return datetime.datetime.strptime(v, '%d/%m/%Y')
    except: return datetime.datetime.max

ordem = st.session_state["ordem_padrao"]
if ordem == "pago":
    contas_exibicao = sorted(contas_exibicao, key=lambda c: (0 if c.get('Status') == 'Pago' else 1, _parse_data(c.get('Vencimento', ''))))
else:
    contas_exibicao = sorted(contas_exibicao, key=lambda c: (0 if c.get('Status') == 'Pendente' else 1, _parse_data(c.get('Vencimento', ''))))

total_mes = sum(float(c.get('Valor', 0)) for c in contas_exibicao)
total_pago = sum(float(c.get('Valor', 0)) for c in contas_exibicao if c.get('Status') == 'Pago')
total_pendente = total_mes - total_pago

def fmt_moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- TELA PRINCIPAL ----------------

# CSS dinâmico para o botão de ordenação
cor_order = "#198754" if ordem == "pago" else "#dc3545"
st.markdown(f"""
<style>
div[class*="st-key-nav_icons"] div[class*="st-key-btn_order"] button {{
    background-color: {cor_order} !important;
    border-color: {cor_order} !important;
}}
div[class*="st-key-nav_icons"] div[class*="st-key-btn_order"] button * {{
    color: white !important;
}}
</style>
""", unsafe_allow_html=True)

with st.container(key="main_box"):
    
    if not st.session_state["filtro_ativo"]:
        with st.container(key="nav_mes"):
            col_prev, col_titulo, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("◀ Anterior", key="btn_prev", use_container_width=True):
                    st.session_state["mes_atual"] -= relativedelta(months=1)
                    st.rerun()
            with col_titulo:
                st.markdown(f"<h4 style='text-align: center; margin: 0; font-size: 14px; color: #0d6efd; font-weight: bold; padding-top: 6px;'>{obter_nome_mes_atual()}</h4>", unsafe_allow_html=True)
            with col_next:
                if st.button("Próximo ▶", key="btn_next", use_container_width=True):
                    st.session_state["mes_atual"] += relativedelta(months=1)
                    st.rerun()
    else:
        col_info, col_btn_clear = st.columns([2, 1])
        with col_info:
            st.info("🔍 Filtros Ativos")
        with col_btn_clear:
            if st.button("❌ Limpar", use_container_width=True, key="btn_limpar_topo"):
                st.session_state["filtro_ativo"] = False
                st.session_state["f_desc"] = None
                st.session_state["f_data_ini"] = None
                st.session_state["f_data_fim"] = None
                st.session_state["f_banco"] = None
                st.session_state["f_status"] = None
                st.rerun()

    with st.container(key="nav_icons"):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("👤", use_container_width=True, help="Ajuda e Configurações"):
                modal_configuracoes()
        with c2:
            if st.button("➕", use_container_width=True, key="btn_add", help="Adicionar Conta"):
                modal_adicionar()
        with c3:
            if st.button("🔍", use_container_width=True, help="Filtros"):
                st.session_state["modal_filtro_aberto"] = True
                st.rerun()
        with c4:
            # Botão de ordenação único: muda entre pago/pendente
            if st.button("⇧", use_container_width=True, key="btn_order", help="Alternar Ordenação (Pago/Pendente no Topo)"):
                st.session_state["ordem_padrao"] = "pendente" if ordem == "pago" else "pago"
                gs.salvar_preferencia_ordem(st.session_state["usuario"], st.session_state["ordem_padrao"])
                st.rerun()
        with c5:
            if st.button("📊", use_container_width=True, help="Relatório PDF"):
                st.session_state["_gerar_relatorio"] = True
                st.rerun()

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; gap: 8px; margin-top: 5px;">
        <div style="flex: 1; background: #e3f2fd; padding: 5px; border-radius: 10px; text-align: center; border: 1px solid #b6d4fe;">
            <div style="font-size: 10px; color: #0d6efd; font-weight: 700; text-transform: uppercase;">A Pagar</div>
            <div style="font-size: 15px; font-weight: 800; color: #0d6efd;">{fmt_moeda(total_mes)}</div>
        </div>
        <div style="flex: 1; background: #d4edda; padding: 5px; border-radius: 10px; text-align: center; border: 1px solid #c3e6cb;">
            <div style="font-size: 10px; color: #155724; font-weight: 700; text-transform: uppercase;">Pago</div>
            <div style="font-size: 15px; font-weight: 800; color: #155724;">{fmt_moeda(total_pago)}</div>
        </div>
        <div style="flex: 1; background: #fff3cd; padding: 5px; border-radius: 10px; text-align: center; border: 1px solid #ffe69c;">
            <div style="font-size: 10px; color: #856404; font-weight: 700; text-transform: uppercase;">Pendente</div>
            <div style="font-size: 15px; font-weight: 800; color: #856404;">{fmt_moeda(total_pendente)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

if st.session_state.get("_gerar_relatorio", False):
    st.session_state["_gerar_relatorio"] = False
    if st.session_state["filtro_ativo"]:
        data_i = st.session_state.get("f_data_ini")
        data_f = st.session_state.get("f_data_fim")
        periodo_txt = f"Filtro: {data_i.strftime('%d/%m/%Y')} a {data_f.strftime('%d/%m/%Y')}"
    else:
        periodo_txt = obter_nome_mes_atual()
        
    pdf_bytes = gerar_pdf(contas_exibicao, periodo_txt)
    st.download_button(
        label="📥 Clique aqui para baixar o Relatório em PDF", 
        data=pdf_bytes, 
        file_name="relatorio_contas.pdf", 
        mime="application/pdf", 
        key="download_pdf_relatorio",
        use_container_width=True
    )

st.write("")

with st.container(height=500, border=False):
    if not contas_exibicao:
        st.info("Nenhuma conta encontrada.")
    else:
        for conta in contas_exibicao:
            v_real = float(conta.get('Valor', 0))
            valor_fmt = fmt_moeda(v_real)
            
            if conta.get('Status') == 'Pago':
                bg_color, border_color = "#d4edda", "#198754"
                btn_bg, btn_border = "#198754", "#198754"
                selo = '<span style="background:#198754; color:#fff; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👍 PAGO</span>'
                texto_btn_status = "Desmarcar"
            else:
                bg_color, border_color = "#f8d7da", "#dc3545"
                btn_bg, btn_border = "#dc3545", "#dc3545"
                selo = '<span style="background:#dc3545; color:#fff; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">👎 A PAGAR</span>'
                texto_btn_status = "Marcar Pago"
                
            st.markdown(f"""
            <style>
            div[class*="st-key-card_{conta.get('ID_Unico', '')}"] {{
                background-color: {bg_color} !important;
                border: 1.5px solid {border_color} !important;
                border-radius: 10px !important;
                padding: 12px !important;
                margin-bottom: 10px !important;
            }}
            div[class*="st-key-card_{conta.get('ID_Unico', '')}"] div[class*="st-key-btn_row_"] button {{
                background-color: {btn_bg} !important;
                border-color: {btn_border} !important;
            }}
            div[class*="st-key-card_{conta.get('ID_Unico', '')}"] div[class*="st-key-btn_row_"] button * {{
                color: white !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            with st.container(key=f"card_{conta.get('ID_Unico', '')}"):
                ref_txt = ""
                if st.session_state["filtro_ativo"]:
                    m_ref = conta.get('Mes_Ref', '')
                    if "-" in m_ref:
                        y, m = m_ref.split("-")
                        ref_txt = f" | Ref: {m}/{y}"
                    else:
                        ref_txt = f" | Ref: {m_ref}"
                
                st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;'><div style='font-weight: 700; font-size: 16px; color: #000;'>{conta.get('Descricao', '')}{ref_txt}</div><div style='font-weight: 700; font-size: 16px; color: #0d6efd;'>{valor_fmt}</div></div>", unsafe_allow_html=True)
                
                bloco_esq = f"<div style='font-size: 14px; color: #000;'>📅 Vence: <b>{conta.get('Vencimento', '')}</b></div>"
                if conta.get('Status') == 'Pago' and conta.get('Data_Pagamento'):
                    bloco_esq += f"<div style='font-size: 14px; color: #000; margin-top: 2px;'>💵 Pago em: <b>{conta.get('Data_Pagamento', '')}</b></div>"
                    if conta.get('Banco'):
                        bloco_esq += f"<div style='font-size: 12px; color: #000; margin-top: 2px;'>🏦 Banco: <b>{conta.get('Banco', '')}</b></div>"
                
                bloco_dir = f"<div style='text-align: right;'><div style='font-size: 9px; color: #333; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;'>STATUS</div><div>{selo}</div></div>"
                
                if conta.get('Observacao'):
                    bloco_dir += f"<div style='font-size: 12px; color: #000; text-align: right; margin-top: 6px; word-break: break-word;'>📝 <b>{conta.get('Observacao', '')}</b></div>"

                st.markdown(f"<div style='display: flex; justify-content: space-between;'><div style='display: flex; flex-direction: column; gap: 6px;'>{bloco_esq}</div><div style='display: flex; flex-direction: column; align-items: flex-end;'>{bloco_dir}</div></div>", unsafe_allow_html=True)
                
                st.write("")
                
                with st.container(key=f"btn_row_{conta.get('ID_Unico', '')}"):
                    b1, b2, b3, b4 = st.columns([2.2, 1, 1, 1])
                    
                    with b1:
                        if st.button(texto_btn_status, key=f"btn_status_{conta.get('ID_Unico', '')}", use_container_width=True):
                            if conta.get('Status') == 'Pendente':
                                modal_pagar(conta.get('ID_Unico', ''), v_real)
                            else:
                                if gs.atualizar_status_conta(conta.get('ID_Unico', ''), "Pendente", "", ""):
                                    st.rerun()
                                    
                    with b2:
                        if st.button("Editar", key=f"btn_edit_{conta.get('ID_Unico', '')}", use_container_width=True):
                            modal_editar(conta)
                    
                    with b3:
                        if st.button("Copiar", key=f"btn_copiar_{conta.get('ID_Unico', '')}", use_container_width=True):
                            modal_copiar(conta)
                            
                    with b4:
                        if st.button("Excluir", key=f"btn_del_{conta.get('ID_Unico', '')}", use_container_width=True):
                            modal_excluir(conta.get('ID_Unico', ''), conta.get('Descricao', ''))

if st.session_state.get("modal_filtro_aberto", False):
    modal_filtros()