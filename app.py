from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave123'

def iniciar_bd():
    conn = sqlite3.connect('gastos.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS gastos (
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
            session['activo'] = True
            return redirect('/registrar')
        return "<h3>❌ Credenciales incorrectas</h3><a href='/'>Volver</a>"
    return '''
<h2>🔐 Iniciar Sesión</h2>
<form method="post">
<p>Usuario: <input name="usuario" required></p>
<p>Clave: <input type="password" name="clave" required></p>
<button>Entrar</button>
</form>
'''

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    if not session.get('activo'): return redirect('/')
    if request.method == 'POST':
        conn = sqlite3.connect('gastos.db')
        conn.execute('INSERT INTO gastos VALUES (NULL, ?, ?, ?)',
            (request.form['fecha'], request.form['descripcion'], request.form['monto']))
        conn.commit()
        conn.close()
        return redirect('/reporte')
    return '''
<h2>📝 Registrar Gasto</h2>
<form method="post">
<p>Fecha: <input type="date" name="fecha" required></p>
<p>Descripción: <input name="descripcion" required></p>
<p>Monto: <input type="number" step="0.01" name="monto" required></p>
<button>Guardar</button>
</form>
<p><a href="/reporte">📊 Ver Reporte</a> | <a href="/salir">🚪 Cerrar Sesión</a></p>
'''

@app.route('/reporte')
def reporte():
    if not session.get('activo'): return redirect('/')
    conn = sqlite3.connect('gastos.db')
    lista = conn.execute('SELECT * FROM gastos ORDER BY fecha DESC').fetchall()
    total = sum(f[3] for f in lista)
    conn.close()
    
    tabla = '<table border="1" cellpadding="8"><tr><th>Fecha</th><th>Descripción</th><th>Monto</th></tr>'
    for f in lista:
        tabla += f'<tr><td>{f[1]}</td><td>{f[2]}</td><td>S/ {f[3]}</td></tr>'
    tabla += f'</table><h3>💰 Total: S/ {total}</h3>'
    
    return f'''
<h2>📊 Reporte de Gastos</h2>
{tabla}
<p><a href="/registrar">➕ Nuevo Gasto</a> | <a href="/salir">🚪 Cerrar Sesión</a></p>
'''

@app.route('/salir')
def salir():
    session.clear()
    return redirect('/')

with app.app_context():
    iniciar_bd()

if __name__ == '__main__':
    app.run(debug=True)
