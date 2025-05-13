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
    vendas = pd.read_excel(vendas_file)
    extratos = pd.read_excel(extratos_file)

    vendas.columns = vendas.columns.str.strip().str.upper()
    extratos.columns = extratos.columns.str.strip().str.upper()

    if "CONTRATO" not in vendas.columns or "CONTRATO" not in extratos.columns:
        st.error("❌ A coluna 'CONTRATO' deve existir nas duas planilhas.")
    else:
        extratos["DATA FECHAMENTO"] = pd.to_datetime(extratos["DATA FECHAMENTO"], errors='coerce')
        extratos["MÊS/ANO"] = extratos["DATA FECHAMENTO"].dt.strftime("%m/%Y")

        extratos_mes = extratos[extratos["MÊS/ANO"] == mes_ano].copy()
        extratos_mes["CONTRATO"] = extratos_mes["CONTRATO"].astype(str)
        vendas["CONTRATO"] = vendas["CONTRATO"].astype(str)

        # Junta % comissão da planilha de vendas
        vendas_comissao = vendas[["CONTRATO", "% DE COMISSÃO"]].drop_duplicates()
        extratos_validos = pd.merge(extratos_mes, vendas_comissao, on="CONTRATO", how="left")

        extratos_validos["VALOR COMISSÃO TOTAL"] = (
            extratos_validos["VALOR BASE"] * (extratos_validos["% DE COMISSÃO"] / 100)
        )

        extratos_validos["VALOR COMISSÃO PARCELA"] = extratos_validos["VALOR COMISSÃO TOTAL"] / extratos_validos["PARCELA"]

        resumo = extratos_validos.groupby("VENDEDOR")["VALOR COMISSÃO PARCELA"].sum().reset_index()
        resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
        resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

        st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
        st.dataframe(resumo, use_container_width=True)

        # Gera arquivo XLSX
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            resumo.to_excel(writer, index=False, sheet_name="Comissões")
        output.seek(0)

        st.download_button("📥 Baixar Resumo em XLSX", output, "comissoes.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.warning("Envie as duas planilhas e selecione um mês.")
