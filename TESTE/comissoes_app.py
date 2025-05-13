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

    # Renomeia colunas para facilitar (caso venham com nomes diferentes)
    vendas.columns = vendas.columns.str.strip()
    extratos.columns = extratos.columns.str.strip()

    # Corrige tipos de dados
    extratos["Data Fechamento"] = pd.to_datetime(extratos["Data Fechamento"])
    vendas["Mês/Ano"] = vendas["Data Fechamento"].dt.strftime("%m/%Y")

    # Filtra pelo mês selecionado
    vendas_mes = vendas[vendas["Mês/Ano"] == mes_ano]

    # Contratos pagos no extrato
    contratos_recebidos = extratos["CONTRATO"].astype(str).unique()
    vendas_mes["CONTRATO"] = vendas_mes["CONTRATO"].astype(str)
    vendas_validas = vendas_mes[vendas_mes["CONTRATO"].isin(contratos_recebidos)]

    # Calcula a comissão
    vendas_validas["Valor Comissão Total"] = (
        vendas_validas["Vlr Vendido"] *
        (vendas_validas["% COMISSÃO"] / 100)
    )

    # Divide conforme quantidade de parcelas
    vendas_validas["Valor Comissão Parcela"] = (
        vendas_validas["Valor Comissão Total"] / vendas_validas["Quantidade de Parcelas"]
    )

    # Agrupa por vendedor
    resumo = vendas_validas.groupby("Vendedor")["Valor Comissão Parcela"].sum().reset_index()
    resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
    resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

    # Exibe os resultados
    st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
    st.dataframe(resumo, use_container_width=True)

    # Botão para baixar em Excel
    csv = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Resumo em CSV", csv, "comissoes.csv", "text/csv")

else:
    st.warning("Envie as duas planilhas e selecione um mês.")

