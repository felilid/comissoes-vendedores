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

if vendas_file and extratos_file:
    # Lê os dados
    vendas = pd.read_excel(vendas_file)
    extratos = pd.read_excel(extratos_file)

    # Remove espaços extras dos nomes das colunas
    vendas.columns = vendas.columns.str.strip()
    extratos.columns = extratos.columns.str.strip()

    # Verifica se 'Data Fechamento' existe no extrato
    if "Data Fechamento" not in extratos.columns:
        st.error("❌ A planilha EXTRATOS deve conter a coluna 'Data Fechamento'.")
        st.stop()

    # Converte datas e cria coluna de Mês/Ano
    extratos["Data Fechamento"] = pd.to_datetime(extratos["Data Fechamento"])
    extratos["Mês/Ano"] = extratos["Data Fechamento"].dt.strftime("%m/%Y")

    # Verifica se a coluna 'CONTRATO' existe nas duas planilhas
    if "CONTRATO" not in vendas.columns or "CONTRATO" not in extratos.columns:
        st.error("❌ A coluna 'CONTRATO' deve existir nas duas planilhas.")
        st.stop()

    # Converte para string antes de comparar
    extratos["CONTRATO"] = extratos["CONTRATO"].astype(str)
    vendas["CONTRATO"] = vendas["CONTRATO"].astype(str)

    # Filtra extratos do mês
    extratos_mes = extratos[extratos["Mês/Ano"] == mes_ano].copy()

    # Filtra apenas os contratos que estão na planilha de vendas
    extratos_validos = extratos_mes[extratos_mes["CONTRATO"].isin(vendas["CONTRATO"])]

    # Verifica se colunas necessárias para cálculo existem
    colunas_necessarias = ["Vlr Vendido", "% COMISSÃO", "Quantidade de Parcelas", "Vendedor"]
    for coluna in colunas_necessarias:
        if coluna not in extratos_validos.columns:
            st.error(f"❌ A coluna '{coluna}' está faltando na planilha EXTRATOS.")
            st.stop()

    # Cálculo da comissão total
    extratos_validos["Valor Comissão Total"] = (
        extratos_validos["Vlr Vendido"] * (extratos_validos["% COMISSÃO"] / 100)
    )

    # Comissão por parcela
    extratos_validos["Valor Comissão Parcela"] = (
        extratos_validos["Valor Comissão Total"] / extratos_validos["Quantidade de Parcelas"]
    )

    # Agrupamento por vendedor
    resumo = extratos_validos.groupby("Vendedor")["Valor Comissão Parcela"].sum().reset_index()
    resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
    resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

    # Exibe os resultados
    st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
    st.dataframe(resumo, use_container_width=True)

    # Botão para download
    csv = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Resumo em CSV", csv, "comissoes.csv", "text/csv")
else:
    st.warning("⚠️ Envie as duas planilhas e selecione um mês.")
