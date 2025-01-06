import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Título
st.title("Solicitação de Serviços")

# Listas de serviços, instrumentos e instituições
SERVICOS = [
    'Análise Instrumental',
    'Consultoria',
    'Curso ou Treinamento'
]

INSTRUMENTOS =[
    'Espectrofotômetro UV/Vis',
    'Epectrofotômetro NIR',
    'Espectrofotômetro Raman',
    'Espectrofluorímetro',
    'Microscópio Confocal Raman'
]

INSTITUICOES = [
    'UERJ',
    'UFRJ',
    'UFF',
    'UNIRIO',
    'UFFRJ',
    'UENF',
    'Outra IES ou ICT',
    'Empresa ou Instituição Privada'
]

# Início do formulário

servico = st.selectbox('Serviço Requerido',
                        options=SERVICOS,
                        index=0)

nome = st.text_input(label='Nome Completo do Requerente*')
email = st.text_input("Email para contato*",
                        placeholder='email@email.com')
instituicao = st.selectbox('Instituição', 
                            options=INSTITUICOES,
                            index=0)
if instituicao == 'Outra IES ou ICT' or 'Empresa ou Instituição Privada':
    nome_instituicao = st.text_input('Nome da Instituição ou Empresa')

departamento = st.text_input('Departamento')
if instituicao != 'Empresa ou Instituição Privada':
    responsavel = st.text_input("Nome do Professor ou Técnico vinculado ao ICT")

# Se o serviço for análise instrumental...
if servico == 'Análise Instrumental':
    # Escolher o placeholder para o caso de análise instrumental.
    placeholder = "Insira aqui número de amostras, tipo etc." 

    #Fazer aparecer a opção de instrumento e coleta
    instrumento = st.selectbox('Instrumento',
                                options=INSTRUMENTOS,
                                index=0)
    coleta = st.date_input('Data da Coleta',
                            min_value=datetime.datetime.now(),
                            format="DD/MM/YYYY"
                            )
    tempo = 6

else: placeholder, tempo = 'Informe os detalhes relevantes como número de envolvidos ou área.', None

informacoes = st.text_area('Observações*',
                            placeholder=placeholder)

# Indicação dos campos obrigatórios
st.markdown('**campos obrigatórios*')

data = datetime.datetime.now()

def atualizar_dados(nome = None, 
                    instituicao = None, 
                    nome_instituicao = None, 
                    departamento= None, 
                    responsavel = None,
                    email = None, 
                    servico = None, 
                    instrumento = None, 
                    coleta = None, 
                    informacoes = None, 
                    data = None, 
                    tempo = None):
    # Criar um novo dataframe
    novos_dados = pd.DataFrame(
       [{
            "Nome" : nome,
            "Instituição" : instituicao,
            "Nome da Instituição" : nome_instituicao,
            "Departamento" : departamento,
            "Responsável" : responsavel,
            "Email" : email,
            "Serviço" : servico,
            "Instrumento" : instrumento,
            "Data de Coleta": coleta.strftime("%d/%m/%Y"),
            "Observações" : informacoes,
            "Dia de Preenchimento" : data,
            "Tempo de Análise" : tempo
        }]
    )
    
    # Estabelecendo conexão com Google Sheets
    # Pegar dados antigos
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read(worksheet='Servicos', 
                                usecols=list(range(12)),
                                ttl=5
                                )
    dados_existentes = dados_existentes[dados_existentes['Nome'].notna()]
    # Juntar os dois daframes
    dados_atualizados = pd.concat([dados_existentes, novos_dados], ignore_index=True)
    
    # Enviar para o google sheet
    conn.update(worksheet='Servicos', data = dados_atualizados)

st.text(departamento)

if nome and email and informacoes: 
    submit_button = st.button(
        'Enviar',
        type='primary',
        on_click= atualizar_dados,
        args=(nome, instituicao, nome_instituicao, departamento, responsavel,
            email, servico, instrumento, coleta, informacoes, data, tempo)
        )
    if submit_button:
        st.warning("Seu formulário foi enviado! Aguarde nosso contato.")
    
    
    
    