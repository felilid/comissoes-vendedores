import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Cálculo de Comissões", layout="wide")
st.title("🔍 Cálculo de Comissões dos Vendedores")

# Upload dos arquivos
vendas_file = st.file_uploader("📄 Upload da Planilha VENDAS.xlsx", type="xlsx")
extratos_file = st.file_uploader("📄 Upload da Planilha EXTRATOS.xlsx", type="xlsx")

# Seleção do mês
mes_ano = st.selectbox("📅 Selecione o mês/ano de pagamento:", [
    "01/2025", "02/2025", "03/2025", "04/2025", "05/2025"
])

if vendas_file and extratos_file:
    try:
        vendas = pd.read_excel(vendas_file, engine="openpyxl")
        extratos = pd.read_excel(extratos_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Erro ao ler os arquivos: {e}")
    else:
        # Padroniza nomes das colunas
        vendas.columns = vendas.columns.str.upper().str.strip()
        extratos.columns = extratos.columns.str.upper().str.strip()

        # Verifica se as colunas essenciais existem
        colunas_necessarias = ["CONTRATO", "% DE COMISSÃO", "VLR VENDIDO", "VENDEDOR", "QUANTIDADE DE PARCELAS"]
        if not all(col in vendas.columns for col in colunas_necessarias):
            st.error("❌ A planilha VENDAS deve conter as colunas: " + ", ".join(colunas_necessarias))
        elif "CONTRATO" not in extratos.columns or "DATA FECHAMENTO" not in extratos.columns:
            st.error("❌ A planilha EXTRATOS deve conter as colunas 'CONTRATO' e 'DATA FECHAMENTO'.")
        else:
            extratos["DATA FECHAMENTO"] = pd.to_datetime(extratos["DATA FECHAMENTO"], errors="coerce")
            extratos = extratos.dropna(subset=["DATA FECHAMENTO"])
            extratos["MÊS/ANO"] = extratos["DATA FECHAMENTO"].dt.strftime("%m/%Y")

            extratos_mes = extratos[extratos["MÊS/ANO"] == mes_ano]
            contratos_pagos = extratos_mes["CONTRATO"].astype(str).unique()

            # Filtra apenas contratos pagos na planilha de vendas
            vendas["CONTRATO"] = vendas["CONTRATO"].astype(str)
            vendas_filtradas = vendas[vendas["CONTRATO"].isin(contratos_pagos)].copy()

            # Conversão de tipos
            vendas_filtradas["% DE COMISSÃO"] = pd.to_numeric(vendas_filtradas["% DE COMISSÃO"], errors="coerce")
            vendas_filtradas["VLR VENDIDO"] = pd.to_
