#This script fetches Mega Sena lottery draw data from the Caixa API and stores it in a SQLite database

import requests
import sqlite3
import time

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"

conn = sqlite3.connect("megasena.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS draws (
    contest INTEGER PRIMARY KEY,
    draw_date TEXT,
    d1 INTEGER,
    d2 INTEGER,
    d3 INTEGER,
    d4 INTEGER,
    d5 INTEGER,
    d6 INTEGER,
    jackpot_sena REAL,
    jackpot_quina REAL,
    jackpot_quadra REAL
)
""")

def get_latest_contest():
    r = requests.get(BASE_URL)
    return r.json()["numero"]

latest = get_latest_contest()

for contest in range(1, latest + 1):
    url = f"{BASE_URL}/{contest}"
    r = requests.get(url)

    if r.status_code != 200: #HTTP 200 means success
        continue

    #Parse the JSON response
    data = r.json()

    #Get the jackpock values for sena, quina, and quadra
    rateio = data["listaRateioPremio"]
    jackpot = {}
    for faixa in rateio:
        # Sena
        if faixa["faixa"] == 1:      
            if faixa["valorPremio"] == 0:
                jackpot["sena"] = data["valorAcumuladoProximoConcurso"]
            else:
                jackpot["sena"] = faixa["valorPremio"]
        # Quina
        elif faixa["faixa"] == 2:    
            jackpot["quina"] = faixa["valorPremio"]
        # Quadra
        elif faixa["faixa"] == 3:    
            jackpot["quadra"] = faixa["valorPremio"]

    #Drawn numbers
    draw = list(map(int, data["listaDezenas"])) #Convert the drawn numbers to integers and store them in a list
    #Date of the draw
    date = data["dataApuracao"]

    #Insert the draw data into the database
    cur.execute("""
        INSERT OR IGNORE INTO draws
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contest,
        date,
        *draw, #The * unpacks the list into individual values
        jackpot["sena"],
        jackpot["quina"],
        jackpot["quadra"]
    ))

    conn.commit()
    time.sleep(0.2)  #Give some time to the API

conn.close()