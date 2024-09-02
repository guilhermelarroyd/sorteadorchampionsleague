from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)

# Configura o diretório de upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para sortear os confrontos de uma rodada
def sortear_rodada(potes, confrontos_obrigatorios=None):
    rodada = []
    usados = set()
    
    for pote_1, pote_2 in (confrontos_obrigatorios or []):
        times_pote_1 = potes[pote_1][:]
        times_pote_2 = potes[pote_2][:]
        
        while times_pote_1 and times_pote_2:
            time_1 = random.choice(times_pote_1)
            time_2 = random.choice(times_pote_2)
            
            if time_1 != time_2 and (time_1, time_2) not in usados and (time_2, time_1) not in usados:
                confronto = (time_1, time_2)
                rodada.append(confronto)
                usados.add(confronto)
                times_pote_1.remove(time_1)
                times_pote_2.remove(time_2)
    
    if len(rodada) != 20:
        print("Erro: Não foi possível sortear 20 jogos únicos.")
    
    return rodada

# Função para ajustar confrontos repetidos
def ajustar_confrontos(rodadas, potes):
    todos_confrontos = [confronto for rodada in rodadas for confronto in rodada]
    confrontos_unicos = set()
    
    for rodada in rodadas:
        nova_rodada = []
        for time1, time2 in rodada:
            while (time1, time2) in confrontos_unicos or (time2, time1) in confrontos_unicos:
                # Tenta trocar o time2 com outro time
                times_pote_2 = potes[f'{df.loc[df["Times"] == time1, "Dono"].values[0]} Pote {df.loc[df["Times"] == time1, "Pote"].values[0]}'][:]
                time2 = random.choice(times_pote_2)
            nova_rodada.append((time1, time2))
            confrontos_unicos.add((time1, time2))
        rodadas[rodadas.index(rodada)] = nova_rodada
    
    return rodadas

# Função para sortear as rodadas e ajustar confrontos repetidos
def sortear_rodadas(potes):
    rodadas = []
    confrontos_previos = []

    # Rodadas 1 e 2
    for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_1_2, confrontos_obrigatorios_1_2]):
        rodada = sortear_rodada(potes, confrontos_obrigatorios)
        rodadas.append(rodada)
    
    # Rodadas 3 e 4
    for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_3_4, confrontos_obrigatorios_3_4]):
        rodada = sortear_rodada(potes, confrontos_obrigatorios)
        rodadas.append(rodada)
    
    # Rodadas 5 e 6
    for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_5_6, confrontos_obrigatorios_5_6]):
        rodada = sortear_rodada(potes, confrontos_obrigatorios)
        rodadas.append(rodada)
    
    # Rodadas 7 e 8
    for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_7_8, confrontos_obrigatorios_7_8]):
        rodada = sortear_rodada(potes, confrontos_obrigatorios)
        rodadas.append(rodada)
    
    # Ajustar confrontos repetidos
    rodadas = ajustar_confrontos(rodadas, potes)
    
    return rodadas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        global df
        df = pd.read_csv(filepath)
        
        potes = {}
        for _, row in df.iterrows():
            nome = row['Times']
            dono = row['Dono']
            pote = row['Pote']
            chave_pote = f'{dono} Pote {pote}'
            if chave_pote not in potes:
                potes[chave_pote] = []
            potes[chave_pote].append(nome)
        
        rodadas = sortear_rodadas(potes)
        
        return render_template('resultados.html', rodadas=rodadas)

if __name__ == '__main__':
    app.run(debug=True)
