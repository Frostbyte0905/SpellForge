import sqlite3

conn = sqlite3.connect("spells.db")
cursor = conn.cursor()

cursor.execute("SELECT id FROM spell")
all_spells = cursor.fetchall()

for (spell_id,) in all_spells:
    cursor.execute("INSERT OR IGNORE INTO known_spells (mage_id, spell_id) VALUES (?, ?)", ("Nendo", spell_id))

conn.commit()
conn.close()

print("Nendo now knows all spells.")
