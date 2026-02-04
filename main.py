from flask import Flask,render_template,request,session,redirect, url_for
from db_wrapper import db
from werkzeug.security import generate_password_hash,check_password_hash
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'kqlsfhdsjkhfdsqflhdsqfhdskfhflhqlfkq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'




@app.route('/')
def home():
    return render_template('main.html')

@app.route('/singuppage',methods=['POST'])
def signuppage():
    username = request.form['username']
    password= request.form["password"]
    hashed_password = generate_password_hash(password)
    if db.execute("select name from users where name=%s", username):
        return 'naam als in dingen'
    if password:
        db.execute("insert into users (name,password) VALUES(%s,%s)", username, hashed_password)
        session['name'] = username
        userrr = db.execute("SELECT id, name FROM users where name=%s", username)
        user = userrr[0]['id']
        iedereen = db.execute(
            "SELECT id, name FROM users "
            "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
            "AND id != %s",
            user, user
        )
        dat = db.execute("select * from contacts where user_id=%s", user)
        return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)

    else:
        return "Fout, paswoord niet opgegeven"

@app.route("/signup")
def signup():
    return render_template('signuppage.html')

@app.route("/login",methods=['POST'])
def login():
    return render_template("loginpage.html")

@app.route("/login2", methods=['POST'])
def login2():
    username = request.form['username']
    password = request.form.get('password')
    if not db.execute("select password from users where name=%s", username):
        return 'foutje'
    stored_hash_row = db.execute("select password from users where name=%s", username)
    if stored_hash_row is None:
        return 'user niet gevonden'
    stored_hash = stored_hash_row[0]["password"]
    if check_password_hash(stored_hash, password):
        session['name'] = username
        userrr = db.execute("SELECT id, name FROM users where name=%s",username)
        user=userrr[0]['id']
        iedereen = db.execute(
            "SELECT id, name FROM users "
            "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
            "AND id != %s",
            user, user
        )
        dat = db.execute("select * from contacts where user_id=%s",user)
        return render_template('template.html',user=username,userD=user, dat=dat, iedereen=iedereen)

    else:
        return 'fout'

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
    user= db.execute("SELECT id, name FROM users")
    iedereen=db.execute("select * from users")
    dat=db.execute("select * from contacts")
    return render_template("database.html",user=user,dat=dat,iedereen=iedereen)

@app.route("/toevoegen",methods=['POST'])
def toev():
    username= request.form["user"]
    id = request.form["id"]
    name = request.form["name"]
    userrr = db.execute("SELECT id, name FROM users where name=%s", username)
    user = userrr[0]['id']
    if id in [i['contact_ID'] for i in db.execute("select contact_ID from contacts where user_id=%s", user)] or user==id:
        return  "fout"
    db.execute("insert into contacts (user_id,contact_ID,contact_name,contact_phone) VALUES(%s,%s,%s,%s)", user,
               id, name, None)
    db.execute("insert into contacts (user_id,contact_ID,contact_name,contact_phone) VALUES(%s,%s,%s,%s)", id,
               user, username, None)
    dat = db.execute("select * from contacts where user_id=%s", user)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )
    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)

@app.route("/bericht",methods=['POST'])
def bericht():
    sender_id = request.form["userID"]
    receiver_id = request.form["receiver_id"]
    username = request.form["name"]
    userrr = db.execute("SELECT id, name FROM users where name=%s", username)
    name = db.execute("SELECT name FROM users where id=%s", sender_id)[0]["name"]
    chats = db.execute("""
    SELECT
        m.sender_id,
        m.receiver_id,
        m.message_text,
        m.timestamp,
        sender.name   AS sender_name,
        receiver.name AS receiver_name
    FROM messages AS m
    JOIN users   AS sender   ON m.sender_id   = sender.id
    JOIN users   AS receiver ON m.receiver_id = receiver.id
    WHERE (m.sender_id = %s AND m.receiver_id = %s)
       OR (m.sender_id = %s AND m.receiver_id = %s)
    ORDER BY m.timestamp
    """, sender_id, receiver_id, receiver_id, sender_id)
    return render_template("berichtUI.html", user=name, userD=sender_id, andere=receiver_id, anderen=username,
                           chats=chats)

@app.route("/verwijder",methods=['POST'])
def verwijder():
    username= request.form["user"]
    id = request.form["id"]
    name = request.form["name"]
    userrr = db.execute("SELECT id, name FROM users where name=%s", username)
    user = userrr[0]['id']
    db.execute("DELETE FROM contacts WHERE (user_id = %s AND contact_ID = %s) OR (user_id = %s AND contact_ID = %s)", user,
               id, id, user)
    db.execute('''
    DELETE
    FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
       OR (sender_id = %s AND receiver_id = %s)
    ''', user,id,id,user)

    dat = db.execute("select * from contacts where user_id=%s", user)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )
    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)

@app.route("/back",methods=['POST'])
def back():
    username = request.form["user"]
    userrr = db.execute("SELECT id FROM users where name=%s", username)
    user = userrr[0]['id']
    dat = db.execute("select * from contacts where user_id=%s", user)
    iedereen = db.execute(
        "SELECT id, name FROM users "
        "WHERE id NOT IN (SELECT contact_ID FROM contacts WHERE user_id = %s) "
        "AND id != %s",
        user, user
    )
    return render_template('template.html', user=username, userD=user, dat=dat, iedereen=iedereen)

@app.route("/joeri",methods=['POST'])
def joeri():
    sender_id = request.form["userID"]
    name = db.execute("SELECT name FROM users where id=%s", sender_id)[0]["name"]
    return render_template("joeriAI.html", name=name, userD=sender_id)

@app.route("/send",methods=['POST'])
def send():
    sender_id = request.form["userID"]
    receiver_id = request.form["id"]
    message_text = request.form["message"]
    timestamp = datetime.datetime.now().isoformat()

    # Bewaar in DB
    db.execute('''
        INSERT INTO messages (sender_id, receiver_id, message_text, timestamp)
        VALUES (%s, %s, %s, %s)
    ''', sender_id, receiver_id, message_text, timestamp)

    # Redirect naar chatpagina (GET)
    return redirect(url_for('chat', sender_id=sender_id, receiver_id=receiver_id))

@app.route("/chat/<int:sender_id>/<int:receiver_id>")
def chat(sender_id, receiver_id):
    # haal users op
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
#iets