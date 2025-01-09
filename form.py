import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time
from mycalendar import calendar


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

# calendarios
calendarPrymary = "ltapuerj@gmail.com"
calendarMeet = "7042b7d1f94002434ed5e186c3fb929d0c584ff979f4186bd29a9dd04da69b95@group.calendar.google.com"
calendarAdmin = "40dbd23a8914741688d55678459c6e49ffa273ef8ec01026b7268515286dea67@group.calendar.google.com"

def DateCheck(calendarID, date):
    toISO = datetime.datetime.combine(date, datetime.datetime.min.time())
    timeMin = (toISO - datetime.timedelta(2)).isoformat() + 'Z'
    timeMax = (toISO + datetime.timedelta(2)).isoformat() + 'Z'
    #timeMax = timeMax.strftime('%Y-%m-%dT%H:%M:%S%z')
    call = calendar()
    lst = call.GetBusy(calendarID, timeMin, timeMax)
    if lst:
        busyDates = [
            datetime.datetime.strptime(
                x['start'], '%Y-%m-%dT%H:%M:%S%z'
            ).date() for x in lst
            ]
    else: busyDates = []
    return date in busyDates

# Início do formulário
servico = st.selectbox('Serviço Requerido',
                        options=SERVICOS,
                        index=0)

nome = st.text_input(label='Nome Completo do Requerente*')
email = st.text_input("Email para contato*",
                        placeholder='nome@dominio.com')
instituicao = st.selectbox('Instituição', 
                            options=INSTITUICOES,
                            index=0)
if instituicao == 'Outra IES ou ICT' or 'Empresa ou Instituição Privada':
    nome_instituicao = st.text_input('Nome da Instituição ou Empresa')

departamento = st.text_input('Departamento')
if instituicao != 'Empresa ou Instituição Privada':
    responsavel = st.text_input("Nome do Professor ou Técnico vinculado ao ICT")

# Se o serviço for análise instrumental...
match servico:
    case 'Análise Instrumental':
        # Escolher o placeholder para o caso de análise instrumental.
        placeholder = "Insira aqui número de amostras, tipo etc." 

        #Fazer aparecer a opção de instrumento e coleta
        instrumento = st.selectbox('Instrumento',
                                    options=INSTRUMENTOS,
                                    index=0)
        coleta = st.date_input('Data da Coleta',
                                min_value=datetime.datetime.now() + datetime.timedelta(2),
                                max_value=datetime.datetime.now() + datetime.timedelta(180),
                                format="DD/MM/YYYY"
                                )
        check = DateCheck(calendarPrymary, coleta)
        tempo = 6
    case 'Curso ou Treinamento':
        placeholder = 'Informe os detalhes relevantes como número de envolvidos, área de desejo do curso e carga horária.'
        coleta = st.date_input('Data Requerida',
                                min_value=datetime.datetime.now() + datetime.timedelta(30),
                                max_value=datetime.datetime.now() + datetime.timedelta(180),
                                format="DD/MM/YYYY"
                                )
        check = DateCheck(calendarMeet, coleta) | DateCheck(calendarAdmin, coleta)
        tempo = None
    case 'Consultoria':
        placeholder, tempo = 'Escreva aqui informações importantes sobre o tema da consultoria.', None
        coleta = st.date_input('Data Requerida para Reunião',
                                min_value=datetime.datetime.now() + datetime.timedelta(2),
                                max_value=datetime.datetime.now() + datetime.timedelta(180),
                                format="DD/MM/YYYY"
                               )
        check = DateCheck(calendarMeet, coleta) | DateCheck(calendarAdmin, coleta)

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
    dados_existentes = conn.read(worksheet='2025', 
                                usecols=list(range(12)),
                                ttl=5
                                )
    dados_existentes = dados_existentes[dados_existentes['Nome'].notna()]
    # Juntar os dois daframes
    dados_atualizados = pd.concat([dados_existentes, novos_dados], ignore_index=True)
    
    # Enviar para o google sheet
    conn.update(worksheet='2025', data = dados_atualizados)

# Adicionar os novos dados à agenda
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

if nome and email and informacoes:
    if not check:
        submit_button = st.button(
            'Enviar',
            type='primary',
            on_click= atualizar_dados,
            args=(nome, instituicao, nome_instituicao, departamento, responsavel,
                email, servico, instrumento, coleta, informacoes, data, tempo)
            )
        if submit_button:
            match servico:
                case "Consultoria":
                    call = calendar()
                    call.CreateEvent(calendarAdmin, novos_dados)
                case "Curso ou Treinamento":
                    call = calendar()
                    call.CreateEvent(calendarAdmin, novos_dados)
                case "Análise Instrumental":
                    call = calendar()
                    call.CreateEvent(calendarPrymary, novos_dados)
            st.warning("Seu formulário foi enviado! Aguarde nosso contato.")
            time.sleep(15)
            st.rerun()
    else: 
        st.error("Data ocupada, escolha uma outra data!")
    
    
    
    