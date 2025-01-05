from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Inisialisasi Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/manajemen_user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(600), nullable=False)

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

# Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username dan Password wajib diisi.', 'error')
        else:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboard'))
            flash('Username atau Password salah.', 'error')
    return render_template('login.html')


# Halaman Registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))  # Jika sudah login, arahkan ke dashboard

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username atau email sudah digunakan.', 'error')
        else:
            new_user = User(
                username=username,
                role=role,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Halaman Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Harap login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('dashboard.html', users=users)

# Tambah Pengguna
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        flash('Harap login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username atau email sudah digunakan.', 'error')
        else:
            new_user = User(
                username=username,
                role=role,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Pengguna berhasil ditambahkan!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_user.html')

# Edit Pengguna
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        flash('Harap login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        user.email = request.form['email']
        password = request.form['password']

        if password:
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        flash('Pengguna berhasil diperbarui!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_user.html', user=user)

# Hapus Pengguna
@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Harap login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Pengguna berhasil dihapus!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:  # Pastikan pengguna sudah login
        session.clear()  # Hapus semua data sesi
        flash('Logout berhasil.', 'info')  # Pesan notifikasi
    else:
        flash('Anda belum login.', 'warning')  # Pesan jika belum login
    return redirect(url_for('login'))  # Arahkan ke halaman login

# Jalankan Aplikasi
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
