from flask import Flask, render_template, request, session, redirect, url_for
from db_wrapper import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'kqlsfhdsjkhfdsqflhdsqfhdskfhflhqlfkq'


@app.route('/')
def home():
    return render_template('main.html')


@app.route("/signup")
def signup():
    return render_template('signuppage.html')


@app.route('/singuppage', methods=['POST'])
def signuppage():
    try:
        # Haal data op
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validatie
        if not username:
            return "❌ Error: Vul een gebruikersnaam in!", 400

        if not password:
            return "❌ Error: Vul een wachtwoord in!", 400

        if len(username) < 3:
            return "❌ Error: Gebruikersnaam moet minimaal 3 karakters zijn!", 400

        if len(password) < 6:
            return "❌ Error: Wachtwoord moet minimaal 6 karakters zijn!", 400

        # Check of gebruiker al bestaat
        print(f"🔍 Checking if user '{username}' already exists...")
        existing = db.execute("SELECT id FROM users WHERE name=%s", username)

        if existing and len(existing) > 0:
            return f"❌ Error: Gebruikersnaam '{username}' bestaat al! Kies een andere naam.", 400

        # Hash wachtwoord
        hashed_password = generate_password_hash(password)
        print(f"✅ Creating new user: {username}")

        # Maak gebruiker aan
        db.execute("INSERT INTO users (name, password) VALUES(%s, %s)", username, hashed_password)

        # Haal de nieuwe gebruiker op
        user_result = db.execute("SELECT id, name FROM users WHERE name=%s", username)
        if not user_result:
            return "❌ Error: Gebruiker aanmaken mislukt!", 500

        user_id = user_result[0]['id']
        print(f"✅ User created with ID: {user_id}")

        # Log gebruiker in
        session['name'] = username
        session['user_id'] = user_id

        # Haal contacten en beschikbare gebruikers op
        dat = db.execute("SELECT * FROM contacts WHERE user_id=%s", user_id)
        iedereen = db.execute(
            "SELECT id, name FROM users "
            "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
            "AND id != %s",
            user_id, user_id
        )

        print(f"✅ Login successful for {username}")
        return render_template('template.html', user=username, userD=user_id, dat=dat, iedereen=iedereen)

    except Exception as e:
        print(f"❌ SIGNUP ERROR: {str(e)}")
        return f"❌ Error bij aanmelden: {str(e)}", 500


@app.route("/login", methods=['POST'])
def login():
    return render_template("loginpage.html")



@app.route("/login2", methods=['POST'])
def login2():
    try:
        # Haal data op
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validatie
        if not username:
            return "❌ Error: Vul een gebruikersnaam in!", 400

        if not password:
            return "❌ Error: Vul een wachtwoord in!", 400

        print(f"🔍 Login attempt for user: {username}")

        # Haal gebruiker op
        user_result = db.execute("SELECT id, name, password FROM users WHERE name=%s", username)

        if not user_result or len(user_result) == 0:
            print(f"❌ User '{username}' not found")
            return f"❌ Error: Gebruiker '{username}' bestaat niet! Maak eerst een account aan.", 400

        user_data = user_result[0]
        stored_hash = user_data['password']
        user_id = user_data['id']

        # Check wachtwoord
        if not check_password_hash(stored_hash, password):
            print(f"❌ Wrong password for user: {username}")
            return "❌ Error: Verkeerd wachtwoord!", 400

        print(f"✅ Password correct for user: {username}")

        # Log gebruiker in
        session['name'] = username
        session['user_id'] = user_id

        print(f"✅ Login successful for {username}")

        # ⭐ REDIRECT naar dashboard in plaats van direct renderen
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"❌ LOGIN ERROR: {str(e)}")
        return f"❌ Error bij inloggen: {str(e)}", 500


# ⭐ NIEUWE ROUTE: Dashboard
@app.route('/dashboard')
def dashboard():
    # Check of gebruiker is ingelogd
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    username = session['name']

    # Haal contacten en beschikbare gebruikers op
    dat = db.execute("SELECT * FROM contacts WHERE user_id=%s", user_id)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user_id, user_id
    )

    return render_template('template.html', user=username, userD=user_id, dat=dat, iedereen=iedereen)
@app.route("/FAQ")
def FAQ():
    return render_template("FAQ.html")


@app.route("/SUPPORT")
def SUPPORT():
    return render_template("SUPPORT.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template('main.html')


@app.route("/database")
def database():
    user = db.execute("SELECT id, name FROM users")
    iedereen = db.execute("SELECT * FROM users")
    dat = db.execute("SELECT * FROM contacts")
    return render_template("database.html", user=user, dat=dat, iedereen=iedereen)


@app.route("/toevoegen", methods=['POST'])
def toev():
    username = request.form["user"]
    contact_id = request.form["id"]
    name = request.form["name"]

    userrr = db.execute("SELECT id, name FROM users WHERE name=%s", username)
    user = userrr[0]['id']

    # ⭐ Gebruik 'contact_id' (kleine letters)
    existing_contacts = db.execute("SELECT contact_id FROM contacts WHERE user_id=%s", user)

    if contact_id in [str(i['contact_id']) for i in existing_contacts] or str(user) == str(contact_id):
        return "fout"

    # ⭐ Gebruik 'contact_id' in INSERT (kleine letters)
    db.execute("INSERT INTO contacts (user_id, contact_id, contact_name, contact_phone) VALUES(%s, %s, %s, %s)",
               user, contact_id, name, None)
    db.execute("INSERT INTO contacts (user_id, contact_id, contact_name, contact_phone) VALUES(%s, %s, %s, %s)",
               contact_id, user, username, None)

    dat = db.execute("SELECT * FROM contacts WHERE user_id=%s", user)

    # ⭐ Ook hier: 'contact_id' (kleine letters)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_id FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )

    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)
@app.route("/bericht", methods=['POST'])
def bericht():
    try:
        sender_id = request.form.get("userID", "").strip()
        # ⭐ Probeer beide veldnamen
        receiver_id = request.form.get("receiver_id", "").strip() or request.form.get("id", "").strip()
        username = request.form.get("name", "").strip()

        # Validatie
        if not sender_id or not receiver_id:
            # ⭐ Voeg debug info toe
            print(f"❌ Missing IDs - sender_id: '{sender_id}', receiver_id: '{receiver_id}'")
            print(f"Form data: {request.form}")
            return "❌ Error: Gebruiker IDs ontbreken!", 400

        # Convert naar integers
        try:
            sender_id = int(sender_id)
            receiver_id = int(receiver_id)
        except ValueError:
            return "❌ Error: Ongeldige gebruiker IDs!", 400

        # Haal naam op
        name_result = db.execute("SELECT name FROM users WHERE id=%s", sender_id)
        if not name_result:
            return "❌ Error: Gebruiker niet gevonden!", 400

        name = name_result[0]["name"]

        # Haal berichten op
        chats = db.execute("""
            SELECT
                m.sender_id,
                m.receiver_id,
                m.message_text,
                m.timestamp,
                sender.name   AS sender_name,
                receiver.name AS receiver_name
            FROM messages AS m
            JOIN users AS sender ON m.sender_id = sender.id
            JOIN users AS receiver ON m.receiver_id = receiver.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.timestamp
        """, sender_id, receiver_id, receiver_id, sender_id)

        return render_template("berichtUI.html",
                               user=name,
                               userD=sender_id,
                               andere=receiver_id,
                               anderen=username,
                               chats=chats)

    except Exception as e:
        print(f"❌ BERICHT ERROR: {str(e)}")
        return f"❌ Error: {str(e)}", 500
@app.route("/verwijder", methods=['POST'])
def verwijder():
    username = request.form["user"]
    id = request.form["id"]
    name = request.form["name"]
    userrr = db.execute("SELECT id, name FROM users WHERE name=%s", username)
    user = userrr[0]['id']
    db.execute("DELETE FROM contacts WHERE (user_id = %s AND contact_ID = %s) OR (user_id = %s AND contact_ID = %s)",
               user, id, id, user)
    db.execute('''
    DELETE FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
       OR (sender_id = %s AND receiver_id = %s)
    ''', user, id, id, user)

    dat = db.execute("SELECT * FROM contacts WHERE user_id=%s", user)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )
    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)


@app.route("/back", methods=['POST'])
def back():
    username = request.form["user"]
    userrr = db.execute("SELECT id FROM users WHERE name=%s", username)
    user = userrr[0]['id']
    dat = db.execute("SELECT * FROM contacts WHERE user_id=%s", user)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )
    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)


@app.route("/joeri", methods=['POST'])
def joeri():
    sender_id = request.form["userID"]
    name = db.execute("SELECT name FROM users WHERE id=%s", sender_id)[0]["name"]
    return render_template("joeriAI.html", name=name, userD=sender_id)


@app.route("/send", methods=['POST'])
def send():
    sender_id = request.form["userID"]
    receiver_id = request.form["id"]
    message_text = request.form["message"]
    timestamp = datetime.datetime.now().isoformat()

    db.execute('''
        INSERT INTO messages (sender_id, receiver_id, message_text, timestamp)
        VALUES (%s, %s, %s, %s)
    ''', sender_id, receiver_id, message_text, timestamp)

    return redirect(url_for('chat', sender_id=sender_id, receiver_id=receiver_id))


@app.route("/chat/<int:sender_id>/<int:receiver_id>")
def chat(sender_id, receiver_id):
    name = db.execute("SELECT name FROM users WHERE id=%s", sender_id)[0]["name"]
    anderen = db.execute("SELECT name FROM users WHERE id=%s", receiver_id)[0]["name"]

    chats = db.execute('''
        SELECT
            m.sender_id,
            m.receiver_id,
            m.message_text,
            m.timestamp,
            sender.name AS sender_name,
            receiver.name AS receiver_name
        FROM messages AS m
        JOIN users AS sender ON m.sender_id = sender.id
        JOIN users AS receiver ON m.receiver_id = receiver.id
        WHERE (m.sender_id = %s AND m.receiver_id = %s)
           OR (m.sender_id = %s AND m.receiver_id = %s)
        ORDER BY m.timestamp
    ''', sender_id, receiver_id, receiver_id, sender_id)

    return render_template("berichtUI.html",
                           user=name,
                           userD=sender_id,
                           andere=receiver_id,
                           anderen=anderen,
                           chats=chats)