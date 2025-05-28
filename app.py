from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import os
import shutil

DB_PATH = os.getenv("SPELLFORGE_DB", "spells.db")

# Automatically copy from local template if the persistent DB doesn't exist
if not os.path.exists(DB_PATH):
    if os.path.exists("spells.db"):
        print("[INFO] No persistent DB found. Copying local spells.db to disk...")
        shutil.copyfile("spells.db", DB_PATH)
    else:
        print("[WARNING] No spells.db found to copy!")

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

ADMIN_PASSWORD = "FORGE!"  # change this as needed

def get_db_connection():
    import os
    DB_PATH = os.getenv("SPELLFORGE_DB", "spells.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mage_id = request.form["mage_id"].strip()
        if mage_id:
            session["mage_id"] = mage_id
            return redirect(url_for("menu", mage_id=mage_id))
        else:
            flash("Please enter a valid Mage ID.")
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        mage_id = request.form["mage_id"]
        return redirect(url_for("menu", mage_id=mage_id))
    return render_template("home.html")

@app.route("/menu/<mage_id>")
def menu(mage_id):
    return render_template("menu.html", mage_id=mage_id)

@app.route("/known/<mage_id>")
def known_spells(mage_id):
    sort = request.args.get("sort", "learned")  # default to order learned
    conn = get_db_connection()

    if mage_id == "Nendo":
        query = "SELECT * FROM spell"
        params = ()
    else:
        query = "SELECT * FROM spell WHERE id IN (SELECT spell_id FROM known_spells WHERE mage_id = ?)"
        params = (mage_id,)

    if sort == "alpha":
        query += " ORDER BY name COLLATE NOCASE"
    elif sort == "core":
        query += " ORDER BY id COLLATE NOCASE"
    # 'learned' means no specific ORDER BY clause (or we could add a timestamp later)

    spells = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("known_spells.html", spells=spells, mage_id=mage_id, current_sort=sort)

@app.route("/forge/<mage_id>", methods=["GET", "POST"])
def forge(mage_id):
    if request.method == "POST":
        core = request.form["core"]
        shape_input = request.form["shape"]
        element = request.form["element"]

        # Normalize shorthand shapes
        shape_map = {
            "Proj": "Projectile",
            "AoE": "Area of Effect"
        }
        shape = shape_map.get(shape_input, shape_input)
        spell_id = f"{core}{shape}+{element}"

        print(f"[DEBUG] Attempting to forge spell with ID: {spell_id}")

        conn = get_db_connection()
        spell = conn.execute("SELECT * FROM spell WHERE id = ?", (spell_id,)).fetchone()

        if not spell:
            conn.close()
            flash(f"Invalid spell combination: {spell_id}")
            return redirect(url_for("forge", mage_id=mage_id))

        known = conn.execute("SELECT * FROM known_spells WHERE mage_id = ? AND spell_id = ?",
                             (mage_id, spell_id)).fetchone()
        conn.close()

        if known:
            return render_template("spell_result.html", spell=spell, known=True, mage_id=mage_id)
        else:
            return render_template("confirm_forge.html", spell=spell, spell_id=spell_id, mage_id=mage_id)

    return render_template("forge.html", mage_id=mage_id)

@app.route("/confirm_forge/<mage_id>", methods=["POST"])
def confirm_forge(mage_id):
    spell_id = request.form["spell_id"]
    password = request.form["admin_password"]

    conn = get_db_connection()
    spell = conn.execute("SELECT * FROM spell WHERE id = ?", (spell_id,)).fetchone()

    if password == ADMIN_PASSWORD:
        conn.execute("INSERT INTO known_spells (mage_id, spell_id) VALUES (?, ?)", (mage_id, spell_id))
        conn.commit()
        conn.close()
        return render_template("spell_result.html", spell=spell, known=False, mage_id=mage_id)
    else:
        conn.close()
        flash("Admin password incorrect.")
        return render_template("confirm_forge.html", spell=spell, spell_id=spell_id, mage_id=mage_id)

@app.route("/spell/<spell_id>")
def spell_detail(spell_id):
    conn = get_db_connection()
    spell = conn.execute("SELECT * FROM spell WHERE id = ?", (spell_id,)).fetchone()
    conn.close()

    if spell:
        return render_template("spell_result.html", spell=spell, known=True, mage_id="Nendo")  # Mage ID optional here
    else:
        return "Spell not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
