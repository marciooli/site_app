import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# Utilizar o estilo do documento .css
with open( ".streamlit/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# Buscar dados na tabela
data = dt.datetime.now()
conn = st.connection("gsheets", type=GSheetsConnection)
dados = conn.read(worksheet='Sheet1', 
                                usecols=list(range(12)),
                                ttl=5
                                )
dados = dados[dados['Nome'].notna()]

col1, col2, col3 = st.columns([1, 2, 2], vertical_alignment="center", border =True)

format = "%I:%M %p"
lst = []
for i in range(dados.shape[0]):
    td = dt.datetime.strptime(dados['Horário Final'].iloc[i], format) - dt.datetime.strptime(dados['Horário Inicial'].iloc[i], format)
    lst.append(int(td.total_seconds()/3600))

dados['Horas trabalhadas'] = lst

meses = []
anos = []

for i in range(dados.shape[0]):
    m, d, a = dados["Data de Coleta"].iloc[i].split("-")
    meses.append(m+"/"+a)
    anos.append(a)

dados["Mês"] = meses
dados["Mês"] = pd.to_datetime(dados['Mês'],format='%m/%Y').dt.to_period('M')
dados["Ano"] = anos
dados2 = dados.copy()

with col1:
    anos_disponiveis = sorted(dados["Ano"].unique(), reverse=True)
    ano = st.selectbox("Selecione o ano:", anos_disponiveis, index=0)
    dados = dados[dados["Ano"] == ano]

    if ano == "2024": 
            delta1, delta2, delta3 = 0, 0, 0
    else: 
        dados_anterior = dados2[dados2["Ano"] == str(int(ano)-1)]
        horas_anterior = dados_anterior['Horas trabalhadas'].sum()
        departamentos_anterior = len(pd.unique(dados_anterior["Departamento"]))
        agendamentos_anterior = dados_anterior.shape[0]
        delta1 = str(dados['Horas trabalhadas'].sum() - horas_anterior)
        delta2 = str(len(pd.unique(dados["Departamento"])) - departamentos_anterior)
        delta3 = str(dados.shape[0] - agendamentos_anterior)

    st.metric(
    label="Horas Totais",
    value=dados['Horas trabalhadas'].sum(),
    delta=delta1
    )

    st.metric(
    label = "Departamentos",
    value=len(pd.unique(dados["Departamento"])),
    delta=delta2
    )

    st.metric(
        label = "Agendamentos",
        value = dados.shape[0],
        delta=delta3
        )
    
    dados3 = conn.read(
        worksheet='Sheet2', 
        usecols=list(range(12)),
        ttl=5,
        )
    dados3 = dados3[dados3['Nome completo'].notna()]
    st.metric(
        label="Integrantes",
        value = dados3.shape[0]
    )

lst = []
for i in range(dados.shape[0]):
    lst.append(dados["Departamento"].iloc[i] + "/" + dados["Instituição ou Empresa"].iloc[i])
dados["Departamento e Instituição"] = lst


graph1_table = dados[["Departamento e Instituição", "Horas trabalhadas"]].groupby("Departamento e Instituição").sum()
graph2_table = dados[["Instrumento Requisitado", "Horas trabalhadas"]].groupby("Instrumento Requisitado").sum()

layout1 = go.Layout(
    {
        "showlegend" : False
    }
)
layout2 = go.Layout(
    {
        "showlegend" : False
    }
)

with col2:
    st.markdown("Horas por Departamento")
    st.plotly_chart(
        go.Figure(data = [go.Pie(
            labels=graph1_table.index,
            values=graph1_table["Horas trabalhadas"],
            hole = .4,
            textinfo = "none",
            marker_colors=px.colors.qualitative.Vivid,
            )],
            layout=layout1
        )
    )

with col3:
    st.markdown("Horas por Instrumento")
    st.plotly_chart(
        go.Figure(data = [go.Pie(
            labels=graph2_table.index,
            values=graph2_table["Horas trabalhadas"],
            hole = .4,
            textinfo = "none",
            marker_colors=px.colors.qualitative.Vivid_r,
            )],
            layout=layout2,
            
        ))

graph3_table = dados2[["Mês", "Horas trabalhadas"]].groupby("Mês").sum()
index = pd.date_range(dados2["Mês"].min().to_timestamp(), dt.datetime.now(), freq="ME").to_period("M")#.to_timestamp()
serie = pd.Series(index = index)
graph3_table = pd.concat([graph3_table, serie[~serie.index.isin(graph3_table.index)]]).sort_index()
graph3_table = graph3_table.drop([0], axis=1).fillna(0).astype("Int64")

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=graph3_table.index.map(str), 
        y=graph3_table["Horas trabalhadas"],
        mode="lines+markers",
        line=dict(color="#4C78A8")
        )
)
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="12m",
                     step="year",
                     stepmode="todate"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
st.plotly_chart(fig)
