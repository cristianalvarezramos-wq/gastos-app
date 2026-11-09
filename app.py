from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave123'

def iniciar_base():
    conn = sqlite3.connect('gastos.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        descripcion TEXT,
        monto REAL
    )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == 'admin' and request.form['clave'] == '123':
            session['entra'] = True
            return redirect('/registrar')
        return "Usuario o clave malos. Vuelve atrás."
    return '''
<html>
<body>
<h2>INICIAR SESION</h2>
<form method=post>
Usuario: <input name=usuario><br>
Clave: <input type=password name=clave><br>
<button>ENTRAR</button>
</form>
</body>
</html>
'''

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    if not session.get('entra'):
        return redirect('/')
    if request.method == 'POST':
        conn = sqlite3.connect('gastos.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO gastos VALUES (NULL, ?, ?, ?)',
                    (request.form['fecha'], request.form['descripcion'], request.form['monto']))
        conn.commit()
        conn.close()
        return redirect('/reporte')
    return '''
<html>
<body>
<h2>REGISTRAR GASTO</h2>
<form method=post>
Fecha: <input type=date name=fecha required><br>
Descripcion: <textarea name=descripcion></textarea><br>
Monto: <input type=number step=0.01 name=monto required><br>
<button>GUARDAR</button>
</form>
<a href="/reporte">VER REPORTE</a> | <a href="/salir">SALIR</a>
</body>
</html>
'''

@app.route('/reporte')
def reporte():
    if not session.get('entra'):
        return redirect('/')
    conn = sqlite3.connect('gastos.db')
    cur = conn.cursor()
    lista = cur.execute('SELECT * FROM gastos ORDER BY fecha DESC').fetchall()
    total = sum(f[3] for f in lista)
    conn.close()
    tabla = '<table border=1><tr><th>Fecha</th><th>Descripcion</th><th>Monto</th></tr>'
    for f in lista:
        tabla += f'<tr><td>{f[1]}</td><td>{f[2]}</td><td>S/ {f[3]}</td></tr>'
    tabla += f'</table><h3>TOTAL: S/ {total}</h3>'
    return f'''
<html>
<body>
<h2>REPORTE DE GASTOS</h2>
{tabla}
<a href="/registrar">NUEVO GASTO</a> | <a href="/salir">SALIR</a>
</body>
</html>
'''

@app.route('/salir')
def salir():
    session.clear()
    return redirect('/')

with app.app_context():
    iniciar_base()

if __name__ == '__main__':
    app.run(debug=True)