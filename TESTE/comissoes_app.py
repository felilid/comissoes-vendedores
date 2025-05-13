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

    # Padroniza nomes de colunas (tira espaços e deixa maiúsculo)
    vendas.columns = vendas.columns.str.strip().str.upper()
    extratos.columns = extratos.columns.str.strip().str.upper()

    # Exibe os nomes das colunas carregadas (para debug)
    st.write("🧾 Colunas em VENDAS:", vendas.columns.tolist())
    st.write("🧾 Colunas em EXTRATOS:", extratos.columns.tolist())

    # Verifica se a coluna 'CONTRATO' existe nas duas
    if 'CONTRATO' in vendas.columns and 'CONTRATO' in extratos.columns:

        # Corrige tipos de dados
        if 'DATA FECHAMENTO' in extratos.columns:
            extratos["DATA FECHAMENTO"] = pd.to_datetime(extratos["DATA FECHAMENTO"])
            extratos["MÊS/ANO"] = extratos["DATA FECHAMENTO"].dt.strftime("%m/%Y")
        else:
            st.error("❌ A planilha EXTRATOS precisa ter a coluna 'Data Fechamento'")
            st.stop()

        # Filtra pelo mês selecionado
        extratos_mes = extratos[extratos["MÊS/ANO"] == mes_ano]

        # Contratos pagos no extrato
        contratos_recebidos = extratos["CONTRATO"].astype(str).unique()
        extratos_mes["CONTRATO"] = extratos_mes["CONTRATO"].astype(str)
        extratos_validos = extratos_mes[extratos_mes["CONTRATO"].isin(contratos_recebidos)]

        # Calcula a comissão
        extratos_validos["VALOR COMISSÃO TOTAL"] = (
            extratos_validos["VLR VENDIDO"] *
            (extratos_validos["% COMISSÃO"] / 100)
        )

        # Divide conforme quantidade de parcelas
        extratos_validos["VALOR COMISSÃO PARCELA"] = (
            extratos_validos["VALOR COMISSÃO TOTAL"] / extratos_validos["QUANTIDADE DE PARCELAS"]
        )

        # Agrupa por vendedor
        resumo = extratos_validos.groupby("VENDEDOR")["VALOR COMISSÃO PARCELA"].sum().reset_index()
        resumo.columns = ["Vendedor", "Comissão do Mês (R$)"]
        resumo["Comissão do Mês (R$)"] = resumo["Comissão do Mês (R$)"].round(2)

        # Exibe os resultados
        st.subheader(f"📌 Resumo de Comissões para {mes_ano}")
        st.dataframe(resumo, use_container_width=True)

        # Botão para baixar em CSV
        csv = resumo.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar Resumo em CSV", csv, "comissoes.csv", "text/csv")

    else:
        st.error("❌ A coluna 'CONTRATO' deve existir **nas duas planilhas**.")
else:
    st.warning("📤 Envie as duas planilhas e selecione um mês.")
