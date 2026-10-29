from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import os
import io
import csv
import requests

app = Flask(__name__)

# ==========================================
# 1. DATABASE CONFIGURATION (Supabase)
# ==========================================
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxx.supabase.co:5432/postgres?sslmode=require'
)

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]
    DATABASE_URL += "?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_sublon_2026'

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 60,
    "pool_size": 2,
    "max_overflow": 5,
    "connect_args": {
        "sslmode": "require",
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
}

db = SQLAlchemy(app)

# 🔗 ใส่ Google Apps Script Web App URL ของคุณที่นี่ (สำหรับ Background Sync)
GOOGLE_SHEET_WEB_APP_URL = "https://script.google.com/macros/s/YOUR_GOOGLE_APPS_SCRIPT_URL/exec"

TH_TIMEZONE = timezone(timedelta(hours=7))

def get_thai_today():
    return datetime.now(TH_TIMEZONE).date()

VALID_USERS = {
    'nueng': '909090',
    'nice': '022540'
}

# ==========================================
# 2. DATABASE MODELS
# ==========================================
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, default='เงินกู้ยืม')
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    sales_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=get_thai_today)
    last_payment_date = db.Column(db.Date, nullable=True)
    closed_date = db.Column(db.Date, nullable=True)
    original_principal = db.Column(db.Float, nullable=False, default=0.0)
    principal = db.Column(db.Float, nullable=False)                     
    daily_interest = db.Column(db.Float, nullable=False, default=0.0)
    initial_daily_interest = db.Column(db.Float, nullable=False, default=0.0)
    paid_interest = db.Column(db.Float, default=0.0)      
    status = db.Column(db.String(50), default='ปกติ')
    installment_amount = db.Column(db.Float, default=0.0)
    schedule_type = db.Column(db.String(50), nullable=False, default='จ่ายทุกวัน') 
    due_day_of_month = db.Column(db.String(50), nullable=True)
    funding_source = db.Column(db.String(50), default='ออมสิน')
    start_next_day = db.Column(db.Boolean, default=False)
    is_locked_interest = db.Column(db.Boolean, default=False)
    locked_interest_amount = db.Column(db.Float, default=0.0)

with app.app_context():
    db.create_all()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def sync_to_google_sheet(tx):
    """ส่งข้อมูลไปเพิ่มใน Google Sheets อัตโนมัติเมื่อมีการบันทึก"""
    if not GOOGLE_SHEET_WEB_APP_URL or "YOUR_GOOGLE_APPS_SCRIPT_URL" in GOOGLE_SHEET_WEB_APP_URL:
        return
    try:
        payload = {
            "sheet": "transactions",
            "id": tx.id,
            "start_date": str(tx.start_date) if tx.start_date else "",
            "customer_name": tx.customer_name,
            "phone": tx.phone or "",
            "type": tx.type,
            "principal": tx.principal,
            "funding_source": tx.funding_source,
            "status": tx.status,
            "sales_name": tx.sales_name
        }
        requests.post(GOOGLE_SHEET_WEB_APP_URL, json=payload, timeout=3)
    except Exception as e:
        print("Google Sheet Sync Error:", e)

# ==========================================
# 4. TEMPLATES (LAYOUT)
# ==========================================
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{ title }} - ทรัพย์ล้น.com</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Prompt', sans-serif; background-color: #fcf6f0; }
        .sidebar { width: 260px; min-height: 100vh; background: #2c0b0e; border-right: 2px solid #d4af37; position: fixed; top: 0; left: 0; z-index: 1050; transition: transform 0.3s ease-in-out; overflow-y: auto; color: #f8f9fa; }
        .main-content { margin-left: 260px; padding: 25px; transition: margin 0.3s ease-in-out; }
        .nav-link { color: #f1d3b2; font-weight: 500; padding: 10px 15px; border-radius: 6px; margin-bottom: 4px; font-size: 0.95rem; white-space: nowrap; }
        .nav-link:hover, .nav-link.active { background-color: #d4af37; color: #2c0b0e; font-weight: 600; }
        .mobile-header { display: none; background: #2c0b0e; border-bottom: 2px solid #d4af37; color: #fff; padding: 12px 15px; position: sticky; top: 0; z-index: 1040; }
        .sidebar-backdrop { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); z-index: 1045; }
        .btn-warning { background-color: #d4af37; border-color: #d4af37; color: #2c0b0e; font-weight: 600; }
        .btn-warning:hover { background-color: #b38f27; border-color: #b38f27; color: #fff; }
        @media (max-width: 992px) {
            .sidebar { transform: translateX(-100%); }
            .sidebar.show { transform: translateX(0); }
            .main-content { margin-left: 0; padding: 12px; }
            .mobile-header { display: flex; justify-content: space-between; align-items: center; }
            .sidebar-backdrop.show { display: block; }
        }
    </style>
</head>
<body>
    <div class="mobile-header shadow-sm">
        <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-warning btn-sm" onclick="toggleSidebar()">☰ เมนู</button>
            <h5 class="text-warning fw-bold mb-0">🔱 ทรัพย์ล้น.com</h5>
        </div>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-warning text-dark">{{ session.get('admin') }}</span>
            <a href="/logout" class="btn btn-outline-danger btn-sm">ออก</a>
        </div>
    </div>

    <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="toggleSidebar()"></div>

    <div class="sidebar p-3 d-flex flex-column shadow" id="sidebarMenu">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h4 class="text-warning fw-bold d-none d-lg-block">🔱 ทรัพย์ล้น.com</h4>
            <h5 class="text-warning fw-bold d-lg-none">🔱 เมนูหลัก</h5>
            <button class="btn-close btn-close-white d-lg-none" onclick="toggleSidebar()"></button>
        </div>
        <div class="mb-3 px-2 d-none d-lg-block text-warning small border-bottom border-secondary pb-2">ผู้ใช้งาน: <b>{{ session.get('admin') }}</b></div>
        <ul class="nav nav-pills flex-column mb-auto">
            <li class="nav-item"><a href="/dashboard" class="nav-link {% if page == 'dashboard' %}active{% endif %}">📊 Dashboard</a></li>
            <li><a href="/receivables_dashboard" class="nav-link {% if page == 'receivables' %}active{% endif %}">🤝 แดชบอร์ดลูกหนี้ (ปล่อยกู้)</a></li>
            <li><a href="/all_transactions" class="nav-link {% if page == 'all' %}active{% endif %}">📋 รายการทั้งหมด</a></li>
        </ul>
        <hr class="border-secondary">
        <a href="/logout" class="btn btn-outline-danger btn-sm w-100 py-1 rounded-pill" style="font-size: 0.82rem;">ออกจากระบบ</a>
    </div>

    <div class="main-content">
        <h2 class="mb-4 text-danger fw-bold fs-4">{% block header %}{% endblock %}</h2>
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    function toggleSidebar() {
        document.getElementById('sidebarMenu').classList.toggle('show');
        document.getElementById('sidebarBackdrop').classList.toggle('show');
    }
    </script>
</body>
</html>
"""

# ==========================================
# 5. ROUTES & CONTROLLERS
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in VALID_USERS and VALID_USERS[username] == password:
            session['admin'] = username
            return redirect(url_for('receivables_dashboard'))
        else:
            error = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
    
    login_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8"><title>เข้าสู่ระบบ - ทรัพย์ล้น.com</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-dark d-flex align-items-center justify-content-center vh-100">
        <div class="card p-4 shadow" style="width: 350px; background: #2c0b0e; color: #d4af37; border: 2px solid #d4af37;">
            <h3 class="text-center mb-3 fw-bold">🔱 ทรัพย์ล้น.com</h3>
            {% if error %}<div class="alert alert-danger py-2 small">{{ error }}</div>{% endif %}
            <form method="POST">
                <div class="mb-3"><label class="form-label small">ชื่อผู้ใช้</label><input type="text" name="username" class="form-control" required></div>
                <div class="mb-3"><label class="form-label small">รหัสผ่าน</label><input type="password" name="password" class="form-control" required></div>
                <button type="submit" class="btn btn-warning w-100 fw-bold">เข้าสู่ระบบ</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_html, error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/')
def root_index():
    if 'admin' not in session: return redirect(url_for('login'))
    return redirect(url_for('receivables_dashboard'))

@app.route('/dashboard')
def index():
    if 'admin' not in session: return redirect(url_for('login'))
    all_txs = Transaction.query.filter(Transaction.principal > 0).all()
    
    dashboard_html = BASE_LAYOUT + """
    {% block header %}Dashboard Overview{% endblock %}
    {% block content %}
    <div class="card shadow-sm p-4">
        <h5 class="fw-bold mb-3">📋 รายการลูกหนี้ที่ต้องติดตาม</h5>
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr><th>ชื่อลูกค้า</th><th>ประเภท</th><th>เบอร์โทร</th><th>ยอดเงินต้นคงเหลือ</th><th>สถานะ</th></tr>
                </thead>
                <tbody>
                    {% for tx in all_txs %}
                    <tr>
                        <td class="fw-bold">{{ tx.customer_name }}</td>
                        <td><span class="badge bg-secondary">{{ tx.type }}</span></td>
                        <td>{{ tx.phone or '-' }}</td>
                        <td class="text-danger fw-bold">฿{{ "{:,.2f}".format(tx.principal) }}</td>
                        <td><span class="badge bg-warning text-dark">{{ tx.status }}</span></td>
                    </tr>
                    {% else %}
                    <tr><td colspan="5" class="text-center text-muted py-3">ไม่มีรายการค้างชำระ</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(dashboard_html, title="Dashboard", page="dashboard", all_txs=all_txs)

@app.route('/receivables_dashboard', methods=['GET', 'POST'])
def receivables_dashboard():
    if 'admin' not in session: return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            p_val = float(request.form.get('principal', 0))
            cust_name = request.form.get('customer_name')
            phone = request.form.get('phone')
            custom_start_date = request.form.get('start_date')
            parsed_date = datetime.strptime(custom_start_date, '%Y-%m-%d').date() if custom_start_date else get_thai_today()
            current_sales = session.get('admin', 'unknown')
            funding_source = request.form.get('funding_source', 'ออมสิน')
            schedule_type = request.form.get('schedule_type', 'จ่ายทุกวัน')

            new_tx = Transaction(
                type=request.form.get('type', 'เงินฉุกเฉิน (ลูกค้าใหม่)'),
                customer_name=cust_name,
                phone=phone,
                sales_name=current_sales,
                start_date=parsed_date, 
                original_principal=p_val,
                principal=p_val,
                daily_interest=p_val * 0.01,
                initial_daily_interest=p_val * 0.01,
                schedule_type=schedule_type,
                funding_source=funding_source,
                status='ปกติ'
            )
            db.session.add(new_tx)
            db.session.commit()
            
            # Sync ไปยัง Google Sheets
            sync_to_google_sheet(new_tx)
            
            return redirect(url_for('receivables_dashboard'))
        except Exception as e:
            db.session.rollback()
            print("Error adding transaction:", e)

    all_txs = Transaction.query.filter(Transaction.principal > 0).all()
    total_remaining = sum(tx.principal for tx in all_txs)

    receivables_html = BASE_LAYOUT + """
    {% block header %}แดชบอร์ดลูกหนี้ (ปล่อยกู้){% endblock %}
    {% block content %}
    <div class="row g-3 mb-4">
        <div class="col-md-3"><div class="card text-white bg-warning p-3 shadow-sm"><h6 class="text-dark fw-bold">ยอดค้างรวมทั้งหมด</h6><h3 class="text-dark fw-bold">฿{{ "{:,.2f}".format(total_remaining) }}</h3></div></div>
        <div class="col-md-3"><div class="card text-white bg-danger p-3 shadow-sm"><h6>เงินต้นคงค้าง</h6><h3 class="fw-bold">฿{{ "{:,.2f}".format(total_remaining) }}</h3></div></div>
    </div>

    <!-- ฟอร์มสำหรับอัปโหลดไฟล์ CSV สำรองข้อมูล (Restore Backup) -->
    <div class="card shadow-sm p-4 mb-4 border border-warning" style="background: #fffdf9;">
        <h5 class="fw-bold text-dark mb-3">📂 นำเข้าข้อมูลจากไฟล์ CSV (Restore Backup)</h5>
        <form action="/import_csv" method="POST" enctype="multipart/form-data">
            <div class="row g-3 align-items-center">
                <div class="col-md-8">
                    <input type="file" name="file" class="form-control form-control-sm" accept=".csv" required>
                    <div class="form-text small text-muted">รองรับไฟล์ sublon_backup_20261029_000000.csv</div>
                </div>
                <div class="col-md-4">
                    <button type="submit" class="btn btn-warning btn-sm fw-bold w-100 text-dark py-2">
                        📥 อัปโหลดและนำเข้าข้อมูล
                    </button>
                </div>
            </div>
        </form>
    </div>

    <!-- ฟอร์มเพิ่มรายการใหม่ -->
    <div class="card shadow-sm p-4 mb-4">
        <h5 class="fw-bold text-dark mb-3">➕ เพิ่มรายการใหม่ (ผู้ดูแล: {{ session.get('admin') }})</h5>
        <form method="POST">
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label small fw-bold">ประเภทรายการ</label>
                    <select name="type" class="form-select form-select-sm">
                        <option>เงินฉุกเฉิน (ลูกค้าใหม่)</option>
                        <option>ผ่อนทอง</option>
                        <option>ยอดค้างเก่า</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label small fw-bold">ชื่อลูกค้า</label>
                    <input type="text" name="customer_name" class="form-control form-control-sm" required placeholder="ระบุชื่อลูกค้า">
                </div>
                <div class="col-md-3">
                    <label class="form-label small fw-bold">เบอร์โทร</label>
                    <input type="text" name="phone" class="form-control form-control-sm" placeholder="08x-xxx-xxxx">
                </div>
                <div class="col-md-3">
                    <label class="form-label small fw-bold">วันที่เริ่ม</label>
                    <input type="date" name="start_date" class="form-control form-control-sm" value="{{ today }}">
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold">แหล่งทุน</label>
                    <select name="funding_source" class="form-select form-select-sm">
                        <option>ออมสิน</option>
                        <option>กรุงศรีอยุธยา</option>
                        <option>วอลเล็ท</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold">ประเภทกำหนดจ่าย</label>
                    <select name="schedule_type" class="form-select form-select-sm">
                        <option>จ่ายทุกวัน</option>
                        <option>กำหนดจ่ายประจำเดือน</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold">ยอดเงินต้น (บาท)</label>
                    <input type="number" step="any" name="principal" class="form-control form-control-sm fw-bold text-danger" required placeholder="0.00">
                </div>
                <div class="col-12 text-end">
                    <button type="submit" class="btn btn-success btn-sm fw-bold px-4">บันทึกข้อมูล</button>
                </div>
            </div>
        </form>
    </div>

    <!-- ตารางรายชื่อลูกหนี้ -->
    <div class="card shadow-sm p-4">
        <h5 class="fw-bold mb-3">📋 รายชื่อลูกหนี้ในระบบ</h5>
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr><th>วันที่เริ่ม</th><th>ชื่อลูกค้า</th><th>เบอร์โทร</th><th>ผู้ดูแล</th><th>แหล่งทุน</th><th>เงินต้นเดิม</th><th>ยอดคงเหลือ</th><th>สถานะ</th></tr>
                </thead>
                <tbody>
                    {% for tx in all_txs %}
                    <tr>
                        <td>{{ tx.start_date.strftime('%d/%m/%Y') if tx.start_date else '-' }}</td>
                        <td class="fw-bold">{{ tx.customer_name }}</td>
                        <td>{{ tx.phone or '-' }}</td>
                        <td><span class="badge bg-info text-dark">{{ tx.sales_name }}</span></td>
                        <td><span class="badge bg-warning text-dark">{{ tx.funding_source }}</span></td>
                        <td>{{ "{:,.2f}".format(tx.original_principal) }}</td>
                        <td class="text-danger fw-bold">฿{{ "{:,.2f}".format(tx.principal) }}</td>
                        <td><span class="badge bg-secondary">{{ tx.status }}</span></td>
                    </tr>
                    {% else %}
                    <tr><td colspan="8" class="text-center text-muted py-3">ยังไม่มีข้อมูลลูกหนี้</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(receivables_html, title="แดชบอร์ดลูกหนี้", page="receivables", total_remaining=total_remaining, all_txs=all_txs, today=get_thai_today().strftime('%Y-%m-%d'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'admin' not in session: 
        return redirect(url_for('login'))
    
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
            csv_input = csv.DictReader(stream)
            
            count_success = 0
            for row in csv_input:
                customer_name = row.get('CustomerName')
                if not customer_name or not str(customer_name).strip():
                    continue

                def safe_float(val, default=0.0):
                    try: return float(val) if val and str(val).strip() else default
                    except: return default

                def safe_date(val):
                    try:
                        val_str = str(val).strip()
                        if not val_str or '###' in val_str or val_str.lower() == 'nan':
                            return None
                        return datetime.strptime(val_str, '%Y-%m-%d').date()
                    except:
                        return None

                def safe_bool(val):
                    if not val: return False
                    return str(val).strip().upper() == 'TRUE'

                phone_val = row.get('Phone', '')
                if not phone_val or str(phone_val).strip().lower() == 'nan':
                    phone_val = None
                else:
                    phone_val = str(phone_val).strip()
                    if '.' in phone_val:
                        phone_val = phone_val.split('.')[0]

                p_val = safe_float(row.get('Principal'))
                orig_p = safe_float(row.get('OriginalPrincipal'), p_val)
                daily_int = safe_float(row.get('DailyInterest'))

                new_tx = Transaction(
                    type=row.get('Type', 'เงินกู้ยืม'),
                    customer_name=customer_name.strip(),
                    phone=phone_val,
                    sales_name=row.get('SalesName', session.get('admin', 'nueng')),
                    start_date=safe_date(row.get('StartDate')) or get_thai_today(),
                    closed_date=safe_date(row.get('ClosedDate')),
                    original_principal=orig_p,
                    principal=p_val,
                    daily_interest=daily_int,
                    initial_daily_interest=daily_int,
                    paid_interest=safe_float(row.get('PaidInterest')),
                    status=row.get('Status', 'ปกติ'),
                    installment_amount=safe_float(row.get('InstallmentAmount')),
                    schedule_type=row.get('ScheduleType', 'จ่ายทุกวัน'),
                    due_day_of_month=str(row.get('DueDayOfMonth', '')) if row.get('DueDayOfMonth') else None,
                    funding_source=row.get('FundingSource', 'ออมสิน'),
                    start_next_day=safe_bool(row.get('StartNextDay')),
                    is_locked_interest=safe_bool(row.get('IsLockedInterest')),
                    locked_interest_amount=safe_float(row.get('LockedInterestAmount'))
                )
                db.session.add(new_tx)
                count_success += 1
            
            db.session.commit()
            print(f"นำเข้าไฟล์ CSV สำเร็จ {count_success} รายการ")
        except Exception as e:
            db.session.rollback()
            print("Import CSV Error:", e)

    return redirect(url_for('receivables_dashboard'))

@app.route('/all_transactions')
def all_transactions():
    if 'admin' not in session: return redirect(url_for('login'))
    all_txs = Transaction.query.all()
    html = BASE_LAYOUT + """
    {% block header %}รายการทั้งหมดในระบบ{% endblock %}
    {% block content %}
    <div class="card shadow-sm p-4">
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark"><tr><th>ID</th><th>วันที่</th><th>ชื่อลูกค้า</th><th>ประเภท</th><th>ยอดเงินต้น</th><th>ผู้ดูแล</th><th>สถานะ</th></tr></thead>
                <tbody>
                    {% for tx in all_txs %}
                    <tr>
                        <td>{{ tx.id }}</td>
                        <td>{{ tx.start_date.strftime('%d/%m/%Y') if tx.start_date else '-' }}</td>
                        <td class="fw-bold">{{ tx.customer_name }}</td>
                        <td><span class="badge bg-secondary">{{ tx.type }}</span></td>
                        <td>฿{{ "{:,.2f}".format(tx.original_principal) }}</td>
                        <td>{{ tx.sales_name }}</td>
                        <td><span class="badge {% if tx.principal > 0 %}bg-warning text-dark{% else %}bg-secondary{% endif %}">{{ tx.status }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(html, title="รายการทั้งหมด", page="all", all_txs=all_txs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)