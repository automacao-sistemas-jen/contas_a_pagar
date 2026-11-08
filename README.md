# 💰 Contas a Pagar JEN

Um aplicativo web completo e responsivo (Mobile First) para gestão de contas pessoais. Desenvolvido para ser prático, seguro e acessível diretamente pelo celular.

## 🎯 Funcionalidades Principais
* **Gestão Multi-mês:** Navegue facilmente entre meses e anos.
* **Resumo Financeiro:** Visão rápida de valores A Pagar, Pago e Pendente.
* **Cadastro Inteligente:** Sistema de autocompletar descrições de contas já cadastradas.
* **Filtros Avançados:** Busque contas por período, banco, status ou descrição.
* **Ordenação Persistente:** Escolha se as contas pagas ou pendentes ficam no topo (a preferência é salva).
* **Relatórios em PDF:** Geração de relatórios completos com totais coloridos e alinhados.
* **Contas Recorrentes:** Função de copiar contas para os próximos meses ajustando os vencimentos.

## 🛠️ Tecnologias Utilizadas
* **Python:** Linguagem base.
* **Streamlit:** Interface web interativa.
* **Pandas:** Manipulação e filtragem de dados.
* **Google Sheets API:** Banco de dados em nuvem (armazenamento dos usuários e contas).
* **FPDF2:** Geração de relatórios PDF.
* **GitHub Actions:** Automação para manter o app online 24/7 (Keep Alive).

## 🚀 Como rodar o projeto localmente
1. Clone o repositório:
   `git clone https://github.com/automacao-sistemas-jen/contas_a_pagar.git`
2. Instale as dependências:
   `pip install -r requirements.txt`
3. Configure as credenciais do Google Sheets no arquivo `.streamlit/secrets.toml`.
4. Execute o app:
   `streamlit run app.py`

## 👤 Desenvolvedor
* **João Evangelista Neto**
* **Contato:** automacaodesistemas.jen@gmail.com
* **Data:** Novembro / 2026