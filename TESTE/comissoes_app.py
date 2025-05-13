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

# Linha de cabeçalho da planilha VENDAS
linha_cabecalho_vendas = 0  # Ajuste aqui se necessário

if vendas_file and extratos_file:
    vendas = pd.read_excel(vendas_file, skiprows=linha_cabecalho_vendas)
    extratos = pd.read_excel(extratos_file)

    vendas.columns = vendas.columns.str.strip().str.upper()
    extratos.columns = extratos.columns.str.strip().str.upper()

    colunas_necessarias = ["CONTRATO", "VALOR BASE", "DATA FECHAMENTO", "% DE COMISSÃO"]
    for col in ["CONTRATO"]:
        if col not in vendas.columns or col not in extratos.columns:
            st.error(f"❌ A coluna '{col}' deve existir nas duas planilhas.")
            st.stop()
    for col in colunas_necessarias:
        if col not in extratos.columns and col not in vendas.columns:
            st.error(f"❌ A coluna '{col}' está faltando em ambas as planilhas.")
            st.stop()

    extratos["DATA FECHAMENTO"] = pd.to_datetime(extratos["DATA FECHAMENTO"])
    extratos["MÊS/ANO"] = extratos["DATA FECHAMENTO"].dt.strftime("%m/%Y")
    extratos_mes = extratos[extratos["MÊS/ANO"] == mes_ano].copy()

    extratos_mes["CONTRATO"] = extratos_mes["CONTRATO"].astype(str)
    vendas["CONTRATO"] = vendas["CONTRATO"].astype(str)

    extratos_validos = extratos_mes.merge(
        vendas[["CONTRATO", "% DE COMISSÃO", "VENDEDOR", "QUANTIDADE DE PARCELAS"]],
        on="CONTRATO",
        how="left"
    )

    extratos_validos["VALOR COMISSÃO TOTAL"] = (
        extratos_validos["VALOR BASE"] * (extratos_validos["% DE COMISSÃO"] / 100)
    )
    extratos_validos["VALOR COMISSÃO PARCELA"] = (
        extratos_validos["VALOR COMISSÃO TOTAL"] / extratos_validos["QUANTIDADE DE PARCELAS"]
    )

    resumo = extratos_validos.groupby("VENDEDOR")["VALOR COMISSÃO PARCELA"].sum().reset_index()
    resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
    resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

    st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
    st.dataframe(resumo, use_container_width=True)

    # Cria arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resumo.to_excel(writer, sheet_name="Comissões", index=False)
    output.seek(0)

    st.download_button(
        label="📥 Baixar Resumo em Excel (.xlsx)",
        data=output,
        file_name="comissoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Envie as duas planilhas e selecione um mês.")
