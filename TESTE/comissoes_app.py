import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cálculo de Comissões", layout="wide")
st.title("🔍 Cálculo de Comissões dos Vendedores")

# Upload dos arquivos
vendas_file = st.file_uploader("📄 Upload da Planilha VENDAS.xlsx", type="xlsx")
extratos_file = st.file_uploader("📄 Upload da Planilha EXTRATOS.xlsx", type="xlsx")

# Seleção do mês
mes_ano = st.selectbox("📅 Selecione o mês/ano de pagamento:", [
    "01/2025", "02/2025", "03/2025", "04/2025", "05/2025"
])

# Linha de cabeçalho (ajuste aqui se necessário)
linha_cabecalho_vendas = 0  # Ex: se começa na linha 3, coloque 2

if vendas_file and extratos_file:
    # Lê os dados
    vendas = pd.read_excel(vendas_file, skiprows=linha_cabecalho_vendas)
    extratos = pd.read_excel(extratos_file)

    # Padroniza colunas
    vendas.columns = vendas.columns.str.strip().str.upper()
    extratos.columns = extratos.columns.str.strip().str.upper()

    # Verifica colunas obrigatórias
    colunas_necessarias = ["CONTRATO", "VALOR BASE", "DATA FECHAMENTO", "% DE COMISSÃO"]
    for col in ["CONTRATO"]:
        if col not in vendas.columns or col not in extratos.columns:
            st.error(f"❌ A coluna '{col}' deve existir nas duas planilhas.")
            st.stop()
    for col in colunas_necessarias:
        if col not in extratos.columns and col not in vendas.columns:
            st.error(f"❌ A coluna '{col}' está faltando em ambas as planilhas.")
            st.stop()

    # Processa datas e filtra mês
    extratos["DATA FECHAMENTO"] = pd.to_datetime(extratos["DATA FECHAMENTO"])
    extratos["MÊS/ANO"] = extratos["DATA FECHAMENTO"].dt.strftime("%m/%Y")
    extratos_mes = extratos[extratos["MÊS/ANO"] == mes_ano].copy()

    # Converte campos e junta % de comissão da planilha VENDAS
    extratos_mes["CONTRATO"] = extratos_mes["CONTRATO"].astype(str)
    vendas["CONTRATO"] = vendas["CONTRATO"].astype(str)

    extratos_validos = extratos_mes.merge(
        vendas[["CONTRATO", "% DE COMISSÃO", "VENDEDOR", "QUANTIDADE DE PARCELAS"]],
        on="CONTRATO",
        how="left"
    )

    # Cálculo da comissão
    extratos_validos["VALOR COMISSÃO TOTAL"] = (
        extratos_validos["VALOR BASE"] * (extratos_validos["% DE COMISSÃO"] / 100)
    )
    extratos_validos["VALOR COMISSÃO PARCELA"] = (
        extratos_validos["VALOR COMISSÃO TOTAL"] / extratos_validos["QUANTIDADE DE PARCELAS"]
    )

    # Agrupamento por vendedor
    resumo = extratos_validos.groupby("VENDEDOR")["VALOR COMISSÃO PARCELA"].sum().reset_index()
    resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
    resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

    # Exibe e exporta
    st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
    st.dataframe(resumo, use_container_width=True)
    csv = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Resumo em CSV", csv, "comissoes.csv", "text/csv")
else:
    st.warning("Envie as duas planilhas e selecione um mês.")
