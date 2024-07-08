import openai
from youtube_transcript_api import YouTubeTranscriptApi as yta
import re
import os
from datetime import datetime

# Defina sua chave de API OpenAI usando variáveis de ambiente para maior segurança
openai.api_key = os.getenv('OPENAI_API_KEY', '')

# Função para extrair metadados da transcrição
def extrair_metadados(transcricao):
    titulo = transcricao.split('\n')[0]
    data = datetime.now().strftime('%d/%m/%Y')  # Gera a data atual no formato dd/mm/aaaa
    topicos = re.findall(r'\b([A-Za-zÀ-ÿ0-9\s]+)\b', transcricao)  # Extrai palavras e frases significativas
    topicos = list(dict.fromkeys(topicos))  # Remove duplicatas mantendo a ordem
    topicos = topicos[:10]  # Limita a lista de tópicos aos primeiros 10
    return titulo, data, topicos

# Função para gerar FAQ usando a API OpenAI
def gerar_faq(transcricao):
    prompt = f"Baseado no conteúdo da seguinte transcrição em português, gere 30 perguntas e respostas:\n\n{transcricao}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            n=1,
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Erro ao gerar FAQ: {e}")
        return None

# Função para gerar resumo usando a API OpenAI
def gerar_resumo(transcricao):
    prompt = f"Resuma a seguinte transcrição em português, destacando os pontos principais e as informações mais importantes:\n\n{transcricao}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            n=1,
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")
        return None

# Função para extrair transcrição do YouTube
def extrair_transcricao_youtube(vid_id, language='pt'):
    try:
        data = yta.get_transcript(vid_id, languages=[language])
        transcript_plana = '\n'.join([value['text'] for value in data])
        return transcript_plana
    except Exception as e:
        print(f"Erro ao extrair transcrição: {e}")
        return None

# Função para salvar conteúdo em um arquivo
def salvar_arquivo(conteudo, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(conteudo)
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

# Solicitar a URL do vídeo do YouTube ao usuário
video_url = input("Por favor, insira a URL do vídeo do YouTube: ")

# Extrair o ID do vídeo da URL
vid_id = re.search(r"v=([^&]+)", video_url)
if vid_id:
    vid_id = vid_id.group(1)
else:
    print("URL inválida.")
    exit()

# Extrair transcrição do YouTube
transcricao_plana = extrair_transcricao_youtube(vid_id, language='pt')

if transcricao_plana:
    # Salvar transcrição em texto plano
    salvar_arquivo(transcricao_plana, "transcricao_plana_pt.txt")

    # Extrair metadados
    titulo, data, topicos = extrair_metadados(transcricao_plana)

    # Criar string dos metadados
    metadados = f"Título da aula: {titulo}\nData da aula: {data}\nTópicos principais cobertos na aula:\n"
    for i, topico in enumerate(topicos, start=1):
        metadados += f"{i}. {topico}\n"

    # Salvar metadados em um arquivo
    salvar_arquivo(metadados, 'metadados.txt')

    # Gerar FAQ
    faq = gerar_faq(transcricao_plana)
    if faq:
        salvar_arquivo(faq, 'faq.txt')

    # Gerar resumo
    resumo = gerar_resumo(transcricao_plana)
    if resumo:
        salvar_arquivo(resumo, 'resumo.txt')

    print("Transcrição, FAQ, metadados e resumo gerados e salvos.")
else:
    print("Não foi possível processar a transcrição.")