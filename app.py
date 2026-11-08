from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_practica_2026'
DATABASE = 'gastos.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )''')
        
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios VALUES (NULL, 'admin', '123')")
        
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (u, p))
        if cur.fetchone():
            session['user'] = u
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html', error=None)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    cur = get_db().cursor()
    cur.execute("SELECT * FROM gastos ORDER BY fecha DESC")
    return render_template('dashboard.html', gastos=cur.fetchall())

@app.route('/agregar', methods=['POST'])
def agregar_gasto():
    if 'user' not in session:
        return redirect(url_for('login'))
    cur = get_db().cursor()
    cur.execute("INSERT INTO gastos VALUES (NULL, ?, ?, ?)",
        (request.form['fecha'], request.form['descripcion'], float(request.form['monto'])))
    get_db().commit()
    return redirect(url_for('dashboard'))

@app.route('/eliminar/<int:gasto_id>')
def eliminar_gasto(gasto_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    cur = get_db().cursor()
    cur.execute("DELETE FROM gastos WHERE id=?", (gasto_id,))
    get_db().commit()
    return redirect(url_for('dashboard'))

@app.route('/reporte')
def reporte():
    if 'user' not in session:
        return redirect(url_for('login'))
    cur = get_db().cursor()
    cur.execute("SELECT * FROM gastos ORDER BY fecha DESC")
    gastos = cur.fetchall()
    cur.execute("SELECT SUM(monto) FROM gastos")
    total = cur.fetchone()[0] or 0
    mes = datetime.now().strftime('%Y-%m')
    cur.execute("SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?", (f'{mes}%',))
    total_mes = cur.fetchone()[0] or 0
    return render_template('reporte.html', gastos=gastos, total=total, total_mes=total_mes, mes_actual=mes)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)