#Get user input and check the database for hits
import sqlite3

#Get user input
while True:
    try:
        user_numbers = [int(n) for n in input(
            "Insira 6 números de 1 a 60, separados por espaço: ").split()]

        if len(user_numbers) != 6:
            raise ValueError
        if any(n < 1 or n > 60 for n in user_numbers):
            raise ValueError
        if len(set(user_numbers)) != 6:
            raise ValueError

        break

    except ValueError:
        print("Entrada inválida. Tente novamente.")

conn = sqlite3.connect("megasena.db")
cur = conn.cursor()

cur.execute("SELECT * FROM draws")
draws = cur.fetchall()

#draws table schema:
'''
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
'''

total_jackpot = 0

print("-------------------------------------------------------------------------\nResultados dos concursos com prêmios ganhos:\n")

for draw in draws:
    contest = draw[0]
    draw_numbers = draw[2:8]  # Extract drawn numbers from the database row
    hits = set(user_numbers).intersection(set(draw_numbers)) #Find matching numbers
    if len(hits) >=4:
        if len(hits) == 6:
            total_jackpot += draw[8]  # jackpot_sena
            print(f"Concurso {contest}: Acertos {len(hits)} - Números: {sorted(hits)} - Premiação: R${draw[8]:,.2f}")
        elif len(hits) == 5:
            total_jackpot += draw[9]  # jackpot_quina
            print(f"Concurso {contest}: Acertos {len(hits)} - Números: {sorted(hits)} - Premiação: R${draw[9]:,.2f}")
        elif len(hits) == 4:
            total_jackpot += draw[10] # jackpot_quadra  
            print(f"Concurso {contest}: Acertos {len(hits)} - Números: {sorted(hits)} - Premiação: R${draw[10]:,.2f}")  

if total_jackpot == 0:
    print("Nenhum prêmio ganho.")
else:
    print(f"Premiação total: R${total_jackpot:,.2f}")     
print("-------------------------------------------------------------------------")
conn.close()