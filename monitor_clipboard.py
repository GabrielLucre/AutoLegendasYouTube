import pyperclip
import time
import os
import subprocess
import json
import re

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

PASTA_LEGENDAS = 'legendas'
PLAYER_PATH = config['player_path']

def gerar_nome(video_id, lang='en'):
    return f'{video_id}.{lang}.srt'

def baixar_legenda(video_url):
    print(f'Baixando legenda de {video_url}...')

    video_id = video_url.split('=')[1].split('&')[0]
    lang_forcada = None

    if '&pt' in video_url:
        lang_forcada = 'pt'
    elif '&en' in video_url:
        lang_forcada = 'en'

    comando = [
        'yt-dlp',
        '--write-sub',
        '--sub-lang', 'en,pt',
        '--write-auto-sub',
        '--skip-download',
        '--sub-format', 'srt/vtt',
        '-o', f'{PASTA_LEGENDAS}/%(id)s.%(ext)s'
    ]

    if 'list=' in video_url:
        comando += ['--playlist-items', '1']

    comando.append(video_url)

    subprocess.run(comando)

    vtt_path_en = os.path.join(PASTA_LEGENDAS, f'{video_id}.en.vtt')
    vtt_path_pt = os.path.join(PASTA_LEGENDAS, f'{video_id}.pt.vtt')

    if lang_forcada == 'pt' and os.path.exists(vtt_path_pt):
        lang = 'pt'
        vtt_path = vtt_path_pt
    elif lang_forcada == 'en' and os.path.exists(vtt_path_en):
        lang = 'en'
        vtt_path = vtt_path_en
    elif os.path.exists(vtt_path_en):
        lang = 'en'
        vtt_path = vtt_path_en
    elif os.path.exists(vtt_path_pt):
        lang = 'pt'
        vtt_path = vtt_path_pt
    else:
        print('Nenhuma legenda .vtt encontrada!')
        return None

    srt_path = os.path.join(PASTA_LEGENDAS, gerar_nome(video_id, lang))

    if not os.path.exists(srt_path):
        print(f'Convertendo {lang.upper()} VTT para SRT...')
        subprocess.run(['ffmpeg', '-y', '-i', vtt_path, srt_path])
        
        if not os.path.exists(srt_path):
            print('Falha ao converter VTT para SRT!')
            return None

    return srt_path

def abrir_player(arquivo_srt):
    if arquivo_srt and os.path.exists(arquivo_srt):
        print('Abrindo legenda...')
        subprocess.Popen([PLAYER_PATH, os.path.abspath(arquivo_srt)])
    else:
        print('Legenda não encontrada!')

def processar_url(video_url):
    if 'youtube.com/watch?v=' not in video_url:
        return

    if not os.path.exists(PASTA_LEGENDAS):
        os.makedirs(PASTA_LEGENDAS)

    video_id = video_url.split('=')[1].split('&')[0]

    lang_forcada = None
    if '&pt' in video_url:
        lang_forcada = 'pt'
    elif '&en' in video_url:
        lang_forcada = 'en'

    if lang_forcada:
        arquivo_srt = baixar_legenda(video_url)
        abrir_player(arquivo_srt)
        return

    arquivo_srt_en = os.path.join(PASTA_LEGENDAS, f'{video_id}.en.srt')
    arquivo_srt_pt = os.path.join(PASTA_LEGENDAS, f'{video_id}.pt.srt')

    if os.path.exists(arquivo_srt_en):
        print('Legenda EN já existe!')
        abrir_player(arquivo_srt_en)
        return
    if os.path.exists(arquivo_srt_pt):
        print('Legenda PT já existe!')
        abrir_player(arquivo_srt_pt)
        return

    arquivo_srt = baixar_legenda(video_url)
    abrir_player(arquivo_srt)

def main():
    print('Monitorando sua área de transferência... (CTRL+C para parar)')
    ultimo = ''

    while True:
        clipboard = pyperclip.paste()

        if clipboard != ultimo and re.match(r'^https://(www\.)?youtube\.com/watch\?v=', clipboard):
            ultimo = clipboard
            processar_url(clipboard)

        time.sleep(1)

if __name__ == '__main__':
    main()
