from flask import Flask, render_template, request
import pandas as pd
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sortear', methods=['POST'])
def sortear():
    # Load the CSV file
    file = request.files['file']
    df = pd.read_csv(file)

    # Organize teams into pots
    potes = {}
    for _, row in df.iterrows():
        nome = row['Times']
        dono = row['Dono']
        pote = row['Pote']
        chave_pote = f'{dono} Pote {pote}'
        if chave_pote not in potes:
            potes[chave_pote] = []
        potes[chave_pote].append(nome)

    # Function to sort the matches of a round
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

    # Function to adjust repeated matchups
    def ajustar_confrontos(rodadas):
        todos_confrontos = [confronto for rodada in rodadas for confronto in rodada]
        confrontos_unicos = set()

        for rodada in rodadas:
            nova_rodada = []
            for time1, time2 in rodada:
                while (time1, time2) in confrontos_unicos or (time2, time1) in confrontos_unicos:
                    # Try swapping time2 with another team
                    times_pote_2 = potes[f'{df.loc[df["Times"] == time1, "Dono"].values[0]} Pote {df.loc[df["Times"] == time1, "Pote"].values[0]}'][:]
                    time2 = random.choice(times_pote_2)
                nova_rodada.append((time1, time2))
                confrontos_unicos.add((time1, time2))
            rodadas[rodadas.index(rodada)] = nova_rodada

        return rodadas

    # Define mandatory matchups for rounds
    confrontos_obrigatorios_1_2 = [
        ('Gui Pote 1', 'Pedro Pote 4'),
        ('Pedro Pote 1', 'Gui Pote 4'),
        ('Pedro Pote 3', 'Gui Pote 2'),
        ('Gui Pote 3', 'Pedro Pote 2'),
    ]

    confrontos_obrigatorios_3_4 = [
        ('Pedro Pote 2', 'Gui Pote 4'),
        ('Gui Pote 2', 'Pedro Pote 4'),
        ('Gui Pote 1', 'Pedro Pote 3'),
        ('Pedro Pote 1', 'Gui Pote 3'),
    ]

    confrontos_obrigatorios_5_6 = [
        ('Pedro Pote 3', 'Gui Pote 4'),
        ('Gui Pote 3', 'Pedro Pote 4'),
        ('Pedro Pote 1', 'Gui Pote 2'),
        ('Gui Pote 1', 'Pedro Pote 2'),
    ]

    confrontos_obrigatorios_7_8 = [
        ('Pedro Pote 4', 'Gui Pote 4'),
        ('Gui Pote 3', 'Pedro Pote 3'),
        ('Gui Pote 2', 'Pedro Pote 2'),
        ('Pedro Pote 1', 'Gui Pote 1'),
    ]

    # Function to draw rounds and adjust repeated matchups
    def sortear_rodadas(potes):
        rodadas = []
        confrontos_previos = []

        # Rounds 1 and 2
        for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_1_2, confrontos_obrigatorios_1_2]):
            rodada = sortear_rodada(potes, confrontos_obrigatorios)
            rodadas.append(rodada)

        # Rounds 3 and 4
        for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_3_4, confrontos_obrigatorios_3_4]):
            rodada = sortear_rodada(potes, confrontos_obrigatorios)
            rodadas.append(rodada)

        # Rounds 5 and 6
        for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_5_6, confrontos_obrigatorios_5_6]):
            rodada = sortear_rodada(potes, confrontos_obrigatorios)
            rodadas.append(rodada)

        # Rounds 7 and 8
        for i, confrontos_obrigatorios in enumerate([confrontos_obrigatorios_7_8, confrontos_obrigatorios_7_8]):
            rodada = sortear_rodada(potes, confrontos_obrigatorios)
            rodadas.append(rodada)

        # Adjust repeated matchups
        rodadas = ajustar_confrontos(rodadas)

        # Print adjusted rounds and game count
        for i, rodada in enumerate(rodadas, 1):
            print(f"\nRodada {i}:")
            for time1, time2 in rodada:
                dono_time1 = df.loc[df['Times'] == time1, 'Dono']
                dono_time2 = df.loc[df['Times'] == time2, 'Dono']
                if not dono_time1.empty and not dono_time2.empty:
                    print(f"{time1} - {dono_time1.values[0]} vs {time2} - {dono_time2.values[0]}")
            print(f"Número de jogos na rodada {i}: {len(rodada)}")

        return rodadas

    # Draw rounds
    rodadas = sortear_rodadas(potes)

    # Render or return the results as desired
    return render_template('result.html', rodadas=rodadas)

if __name__ == '__main__':
    app.run(debug=True)
