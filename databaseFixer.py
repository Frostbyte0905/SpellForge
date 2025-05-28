import sqlite3

conn = sqlite3.connect("spells.db")
cursor = conn.cursor()

# Fetch all spell IDs
cursor.execute("SELECT id FROM spell")
spells = cursor.fetchall()

updates = []
for (spell_id,) in spells:
    new_id = spell_id
    if "+Proj+" in spell_id:
        new_id = new_id.replace("+Proj+", "+Projectile+")
    if "+AoE+" in spell_id:
        new_id = new_id.replace("+AoE+", "+Area of Effect+")
    if new_id != spell_id:
        updates.append((new_id, spell_id))

# Apply updates
for new_id, old_id in updates:
    cursor.execute("UPDATE spell SET id = ? WHERE id = ?", (new_id, old_id))

conn.commit()
conn.close()

print(f"Updated {len(updates)} spell IDs.")
