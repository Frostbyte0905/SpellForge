import sqlite3

conn = sqlite3.connect("spells.db")
c = conn.cursor()

# Create known_spells table
c.execute("""
CREATE TABLE IF NOT EXISTS known_spells (
    mage_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    PRIMARY KEY (mage_id, spell_id)
)
""")

conn.commit()
conn.close()
