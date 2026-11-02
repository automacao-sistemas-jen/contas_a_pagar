import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import hashlib

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_ID = "1x6v-gZnPsgBGhgkpf82qYG-9tnA9qirG-mQDbyaNMZs" # ID da sua planilha
USUARIOS_WORKSHEET = "Usuarios"

_usuarios_worksheet_cache = None

def _get_credentials():
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    import os
    if os.path.exists("google_credentials.json"):
        return Credentials.from_service_account_file("google_credentials.json", scopes=SCOPES)
    raise FileNotFoundError("Credenciais não encontradas.")

def _get_usuarios_ws():
    global _usuarios_worksheet_cache
    if _usuarios_worksheet_cache is None:
        creds = _get_credentials()
        client = gspread.authorize(creds)
        planilha = client.open_by_key(SPREADSHEET_ID)
        try:
            _usuarios_worksheet_cache = planilha.worksheet(USUARIOS_WORKSHEET)
        except gspread.exceptions.WorksheetNotFound:
            ws = planilha.add_worksheet(title=USUARIOS_WORKSHEET, rows="100", cols="2")
            ws.append_row(["Email", "Senha_Hash"])
            _usuarios_worksheet_cache = ws
    return _usuarios_worksheet_cache

def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(email: str, senha: str) -> bool:
    try:
        ws = _get_usuarios_ws()
        registros = ws.get_all_records()
        for reg in registros:
            if str(reg.get("Email", "")).strip().lower() == email.lower(): return False
        ws.append_row([email.lower(), _hash_senha(senha)])
        return True
    except Exception as e:
        print(f"[google_sheets] erro ao cadastrar: {e}")
        return False

def autenticar_usuario(email: str, senha: str) -> bool:
    try:
        ws = _get_usuarios_ws()
        registros = ws.get_all_records()
        hash_digitado = _hash_senha(senha)
        for reg in registros:
            if str(reg.get("Email", "")).strip().lower() == email.lower():
                if str(reg.get("Senha_Hash", "")).strip() == hash_digitado: return True
                return False
        return False
    except Exception as e:
        print(f"[google_sheets] erro ao autenticar: {e}")
        return False

# ---------------------------------------------------------------------------
# Funções para Contas a Pagar
# ---------------------------------------------------------------------------
CONTAS_WORKSHEET = "Contas"
_contas_worksheet_cache = None

def _get_contas_ws():
    global _contas_worksheet_cache
    if _contas_worksheet_cache is None:
        creds = _get_credentials()
        client = gspread.authorize(creds)
        planilha = client.open_by_key(SPREADSHEET_ID)
        try:
            _contas_worksheet_cache = planilha.worksheet(CONTAS_WORKSHEET)
        except gspread.exceptions.WorksheetNotFound:
            ws = planilha.add_worksheet(title=CONTAS_WORKSHEET, rows="1000", cols="9")
            # Cria o cabeçalho da tabela
            ws.append_row(["ID_Unico", "Email", "Mes_Ref", "Descricao", "Valor", "Vencimento", "Status", "Data_Pagamento", "Observacao"])
            _contas_worksheet_cache = ws
    return _contas_worksheet_cache

def salvar_conta(email, mes_ref, descricao, valor, vencimento, observacao=""):
    try:
        import uuid
        ws = _get_contas_ws()
        id_unico = str(uuid.uuid4())
        # Formato do mês: YYYY-MM (ex: 2026-11)
        ws.append_row([id_unico, email.lower(), mes_ref, descricao, float(valor), vencimento, "Pendente", "", observacao])
        return True
    except Exception as e:
        print(f"Erro ao salvar conta: {e}")
        return False

def carregar_contas(email, mes_ref):
    try:
        ws = _get_contas_ws()
        registros = ws.get_all_records()
        contas = []
        for reg in registros:
            if str(reg.get("Email", "")).lower() == email.lower() and str(reg.get("Mes_Ref", "")) == mes_ref:
                contas.append(reg)
        return contas
    except Exception as e:
        print(f"Erro ao carregar contas: {e}")
        return []

def atualizar_status_conta(id_unico, novo_status, data_pagamento=""):
    try:
        ws = _get_contas_ws()
        cell = ws.find(id_unico)
        if cell:
            ws.update_cell(cell.row, 7, novo_status) # Coluna 7: Status
            ws.update_cell(cell.row, 8, data_pagamento) # Coluna 8: Data_Pagamento
            return True
        return False
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return False

def obter_descricoes_usuario(email):
    try:
        ws = _get_contas_ws()
        registros = ws.get_all_records()
        descricoes = set()
        for reg in registros:
            if str(reg.get("Email", "")).lower() == email.lower():
                desc = str(reg.get("Descricao", "")).strip()
                if desc:
                    # Deixa a primeira letra maiúscula para ficar bonito (ex: Internet)
                    descricoes.add(desc.capitalize())
        return sorted(list(descricoes))
    except Exception as e:
        print(f"Erro ao buscar descrições: {e}")
        return []

def editar_conta(id_unico, descricao, valor, vencimento, observacao):
    try:
        ws = _get_contas_ws()
        cell = ws.find(id_unico)
        if cell:
            ws.update_cell(cell.row, 4, descricao)   # Coluna 4: Descrição
            ws.update_cell(cell.row, 5, float(valor)) # Coluna 5: Valor
            ws.update_cell(cell.row, 6, vencimento)  # Coluna 6: Vencimento
            ws.update_cell(cell.row, 9, observacao)  # Coluna 9: Observação
            return True
        return False
    except Exception as e:
        print(f"Erro ao editar conta: {e}")
        return False

def excluir_conta(id_unico):
    try:
        ws = _get_contas_ws()
        cell = ws.find(id_unico)
        if cell:
            ws.delete_rows(cell.row)
            return True
        return False
    except Exception as e:
        print(f"Erro ao excluir conta: {e}")
        return False