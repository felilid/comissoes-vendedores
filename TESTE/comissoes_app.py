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

    # Padroniza os nomes das colunas (remove espaços extras)
    vendas.columns = vendas.columns.str.strip()
    extratos.columns = extratos.columns.str.strip()

    # Converte datas
    extratos["Data Fechamento"] = pd.to_datetime(extratos["Data Fechamento"])
    extratos["Mês/Ano"] = extratos["Data Fechamento"].dt.strftime("%m/%Y")

    # Filtra o extrato pelo mês selecionado
    extratos_mes = extratos[extratos["Mês/Ano"] == mes_ano].copy()

    # Garante que a coluna CONTRATO é string
    extratos_mes["CONTRATO"] = extratos_mes["CONTRATO"].astype(str)

    # Filtra apenas contratos que estão na planilha de vendas (se existir a coluna "CONTRATO")
    if "CONTRATO" in vendas.columns and "CONTRATO" in extratos_mes.columns:
        contratos_validos = vendas["CONTRATO"].astype(str).unique()
        extratos_mes = extratos_mes[extratos_mes["CONTRATO"].isin(contratos_validos)]

    # Cálculo da comissão total
    extratos_mes["Valor Comissão Total"] = (
        extratos_mes["Vlr Vendido"] * (extratos_mes["% COMISSÃO"] / 100)
    )

    # Comissão proporcional por parcela
    extratos_mes["Valor Comissão Parcela"] = (
        extratos_mes["Valor Comissão Total"] / extratos_mes["Quantidade de Parcelas"]
    )

    # Agrupamento por vendedor
    resumo = extratos_mes.groupby("Vendedor")["Valor Comissão Parcela"].sum().reset_index()
    resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
    resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

    # Exibição do resultado
    st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
    st.dataframe(resumo, use_container_width=True)

    # Download em CSV
    csv = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Resumo em CSV", csv, "comissoes.csv", "text/csv")

else:
    st.warning("Envie as duas planilhas e selecione um mês.")
