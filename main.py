import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import json

# --- Autenticação com Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
#creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
creds_json = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

# --- Abrir a planilha pelo ID ---
SPREADSHEET_ID = "13VfkL3y2SXrU8OhnXND8saWF7NcgtGoPyRSc6Kb7Z8M" 
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Primeira aba da planilha


st.set_page_config(
    page_title="Finanças Pessoais",  # título da aba do navegador
    layout="centered",  # layout da página: "wide" ou "centered"
    page_icon="💰",  # opcional: ícone da aba
)
st.title("Dinheiro Ana 💗")

st.markdown("""---""")

tab1, tab2 = st.tabs(["💰 Gastos", "📊 Gráficos"])

with tab1:
    with st.form(key="form_financas"):
        st.title("Meus Gastos Pessoais")
        input_valor = st.number_input("Valor:", min_value=0.0, step=0.01, format="%.2f")
        input_categoria = st.selectbox(
            "Categoria:",
            options=[
                "Alimentação",
                "Plano de Saúde",
                "Consultório",
                "Balé",
                "Lazer",
                "Educação",
                "Mercado",
                "Compras",
                "Shopping",
                "Saídas",
                "Livros pessoal",
                "Cartão C6 colorido"
                "Outros",
            ],
        )
        input_data = st.date_input("Data:")
        input_descricao = st.text_input("Descrição:")
        
        submit_button = st.form_submit_button(label="Adicionar")

        if submit_button:
            nova_linha = [input_valor, input_categoria, str(input_data), input_descricao]
            sheet.append_row(nova_linha)
            st.success("✅ Registro adicionado com sucesso ao Google Sheets!")
            st.balloons()

with tab2:
    st.title("📊 Análise de Gastos")

    try:
        # Lendo os dados do Google Sheets
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)

        # Converter a coluna 'Data' para datetime
        df["Data"] = pd.to_datetime(df["Data"])

        # -----------------------------
        # Gráfico de Pizza: Gastos por Categoria
        # -----------------------------
        st.subheader("Distribuição por Categoria")
        categoria_sum = df.groupby("Categoria")["Valor"].sum()
        st.pyplot(categoria_sum.plot.pie(autopct='%1.1f%%', figsize=(6, 6)).figure)

        # -----------------------------
        # Gráfico de Barras: Total por Mês
        # -----------------------------
        st.subheader("Gastos Totais por Mês")
        df["AnoMes"] = df["Data"].dt.to_period("M").astype(str)
        mes_sum = df.groupby("AnoMes")["Valor"].sum().reset_index()

        st.bar_chart(mes_sum.set_index("AnoMes"))
        
        st.markdown("#### Total de Gastos por Mês")
        cols = st.columns(len(mes_sum))
        for idx, row in mes_sum.iterrows():
            st.metric(label=row["AnoMes"], value=f"R$ {row['Valor']:.2f}")

        # -----------------------------
        # Linha: Evolução dos Gastos ao Longo do Tempo
        # -----------------------------
        st.subheader("Evolução Acumulada ao Longo do Tempo")
        df_sorted = df.sort_values("Data")
        df_sorted["Gasto Acumulado"] = df_sorted["Valor"].cumsum()
        st.line_chart(df_sorted.set_index("Data")["Gasto Acumulado"])

        # -----------------------------
        # Tabela Resumo por Categoria
        # -----------------------------
        st.subheader("Resumo por Categoria")
        st.dataframe(categoria_sum.reset_index().rename(columns={"Valor": "Total (R$)"}))

    except Exception as e:
        st.error(f"Erro ao carregar ou processar os dados: {e}")

        
        
            