from flask import Flask, render_template_string, request, Response, redirect, url_for, session
import os
import csv
import io
import urllib.request
import urllib.parse
import json
import random
from datetime import datetime, date
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = 'bizflow_secure_secret_key'

SUPABASE_URL = "https://pdpeqsubrbmdjxgmtjpy.supabase.co"
SUPABASE_KEY = "sb_publishable_ZSKb3jQeqfP8oSIajLhFWA_sOBMd4-H"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_debtors_from_db():
    try:
        response = supabase.table("debtors").select("*").execute()
        data = response.data if response.data else []
        for d in data:
            if 'old_arrears' not in d:
                d['old_arrears'] = 0
        return data
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
        return []

pending_otp_requests = []

users_database = [
    {'id': 1, 'name': 'Nice (แอดมิน)', 'username': 'nice', 'password': '022540', 'role': 'Super Admin', 'status': 'ใช้งานอยู่', 'last_login': '30/10/2026 08:30'},
    {'id': 2, 'name': 'Nueng (แอดมิน)', 'username': 'nueng', 'password': '909090', 'role': 'Super Admin', 'status': 'ใช้งานอยู่', 'last_login': '30/10/2026 08:30'}
]

system_config = {
    'company_name': 'BizFlow+ Financial Services',
    'telegram_token': '9203750510:AAFJhUvWRf4mOSozUSkz0I0I9Jca-xImuTo',
    'telegram_chat_id': '1880260879'
}

bank_accounts = {
    'kbank': 0,
    'ktb': 0,
    'bay': 0,
    'kkp': 0,
    'gsb': 0,
    'wallet': 0,
    'cash': 0
}

personal_finance = {
    'monthly_income': 55000,
    'savings_cash': 0,
    'savings_gold': 0,
    'savings_stocks': 0
}

daily_misc_expenses = []

household_debts = [
    {'id': 'd1', 'name': 'Line BK', 'outstanding': 9200, 'detail': 'ดอกเบี้ย 20%, ปิดจบเดือนที่ 1'},
    {'id': 'd2', 'name': 'สินเชื่อ ttb', 'outstanding': 125441, 'detail': 'ดอกเบี้ย 19%, ปิดจบเดือนที่ 2-5'},
    {'id': 'd3', 'name': 'หนี้ทองคำ 4 บาท', 'outstanding': 240000, 'detail': 'ดอกเบี้ย 15%, ไถ่ถอนเดือนที่ 6-12'}
]

household_expenses = [
    {'id': 'e1', 'name': 'งดรถยนต์', 'amount': 13588, 'installments': 59, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e2', 'name': 'งดมอเตอร์ไซค์ 1', 'amount': 3396, 'installments': 10, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e3', 'name': 'งดมอเตอร์ไซค์ 2', 'amount': 2122, 'installments': 21, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e4', 'name': 'ประกันรถยนต์ 1', 'amount': 1540, 'installments': 10, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e5', 'name': 'ประกันรถยนต์ 2', 'amount': 1860, 'installments': 2, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e6', 'name': 'ค่าห้องพัก', 'amount': 0, 'installments': 0, 'note': 'ยอดผันแปรตามไฟ/น้ำ', 'status': 'รอจ่าย', 'is_variable': True, 'has_installments': False},
    {'id': 'e7', 'name': 'แชร์วง 5 หมื่น', 'amount': 3000, 'installments': 3, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e8', 'name': 'แชร์วง 9 หมื่น', 'amount': 5000, 'installments': 17, 'note': 'งวดคงเหลือ', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': True},
    {'id': 'e9', 'name': 'ประกันชีวิต', 'amount': 2100, 'installments': 0, 'note': 'จ่ายประจำเดือน', 'status': 'รอจ่าย', 'is_variable': False, 'has_installments': False},
    {'id': 'e10', 'name': 'ค่าเน็ต', 'amount': 0, 'installments': 0, 'note': 'ยอดผันแปรตามการใช้จริง', 'status': 'รอจ่าย', 'is_variable': True, 'has_installments': False}
]

@app.template_filter('format_num')
def format_num_filter(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return "0.00"

def send_telegram_alert(message):
    token = system_config.get('telegram_token')
    chat_id = system_config.get('telegram_chat_id')
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            return True
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

# โค้ด HTML Templates (ADMIN_TEMPLATE, LOGIN_MEMBER_TEMPLATE, APPLY_TEMPLATE, ADMIN_LOGIN_TEMPLATE) คงเดิมตามที่คุณใช้งานอยู่
# ----------------- Flask Routes -----------------

@app.route('/')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    today_str = datetime.now().strftime('%d/%m/%Y')
    debtors_database = get_debtors_from_db()
    
    total_principal = sum(float(d.get('principal', 0)) for d in debtors_database if d.get('status') == 'ปกติ')
    total_profit = sum(float(d.get('accumulated_profit', 0)) for d in debtors_database)
    
    collected_today = 0
    for d in debtors_database:
        txs = d.get('transactions', [])
        if isinstance(txs, str):
            try: txs = json.loads(txs)
            except: txs = []
        for tx in txs:
            if tx.get('date', '').startswith(today_str) and (tx.get('type') == 'รับชำระหนี้' or tx.get('type') == 'รับชำระยอดค้างเก่า'):
                collected_today += float(tx.get('raw_amount', 0))

    return render_template_string(ADMIN_TEMPLATE, 
                                 debtors=debtors_database,
                                 users=users_database,
                                 config=system_config,
                                 otp_list=pending_otp_requests,
                                 bank_kbank=bank_accounts['kbank'],
                                 bank_ktb=bank_accounts['ktb'],
                                 bank_bay=bank_accounts['bay'],
                                 bank_kkp=bank_accounts['kkp'],
                                 bank_gsb=bank_accounts['gsb'],
                                 bank_wallet=bank_accounts['wallet'],
                                 bank_cash=bank_accounts['cash'],
                                 today_date=today_str,
                                 total_principal=total_principal,
                                 total_profit=total_profit,
                                 collected_today=collected_today,
                                 household_debts=household_debts,
                                 household_expenses=household_expenses,
                                 personal_finance=personal_finance)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        if any(user['username'] == u and user['password'] == p for user in users_database):
            session['admin_logged_in'] = True
            session['admin_user'] = u
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Username หรือ Password ไม่ถูกต้อง!")
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

@app.route('/apply')
def apply_form():
    if not session.get('member_verified'):
        return render_template_string(LOGIN_MEMBER_TEMPLATE)
    
    phone = session.get('verified_phone', '')
    debtors_db = get_debtors_from_db()
    existing_client = next((d for d in debtors_db if d.get('phone') == phone), None)
    
    is_old_member = bool(existing_client)
    default_name = existing_client.get('name', '') if existing_client else ''
    default_facebook = existing_client.get('facebook', '') if existing_client else ''
    default_acc = existing_client.get('acc', '') if existing_client else ''

    return render_template_string(APPLY_TEMPLATE, 
                                 is_old_member=is_old_member,
                                 default_name=default_name,
                                 default_facebook=default_facebook,
                                 default_acc=default_acc)

@app.route('/apply-login', methods=['POST'])
def apply_login():
    phone = request.form.get('phone', '').strip()
    action = request.form.get('action')
    otp_input = request.form.get('otp_code', '').strip()
    if not phone:
        return render_template_string(LOGIN_MEMBER_TEMPLATE, error="กรุณากรอกเบอร์โทรศัพท์!")
    if action == 'request_otp':
        new_otp = str(random.randint(1000, 9999))
        pending_otp_requests.insert(0, {'phone': phone, 'otp': new_otp, 'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S')})
        send_telegram_alert(f"🔑 <b>OTP คำขอกู้</b>\n📞 เบอร์: {phone}\n🔢 OTP: <b>{new_otp}</b>")
        return render_template_string(LOGIN_MEMBER_TEMPLATE, phone_val=phone, success_msg="ส่งคำขอ OTP ไปยัง Telegram แอดมินแล้ว")
    elif action == 'verify_login':
        found = next((item for item in pending_otp_requests if item['phone'] == phone and item['otp'] == otp_input), None)
        if found:
            session['member_verified'] = True
            session['verified_phone'] = phone
            pending_otp_requests.remove(found)
            return redirect(url_for('apply_form'))
        return render_template_string(LOGIN_MEMBER_TEMPLATE, phone_val=phone, error="รหัส OTP ไม่ถูกต้อง!")
    return render_template_string(LOGIN_MEMBER_TEMPLATE)

@app.route('/clear-otp')
def clear_otp():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    phone = request.args.get('phone')
    global pending_otp_requests
    pending_otp_requests = [i for i in pending_otp_requests if i['phone'] != phone]
    return redirect(url_for('admin_dashboard'))

@app.route('/approve-debtor')
def approve_debtor():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    debtor_id = request.args.get('debtor_id')
    if debtor_id:
        try:
            supabase.table("debtors").update({'status': 'ปกติ'}).eq('id', debtor_id).execute()
        except Exception as e:
            print(f"Approve Error: {e}")
    return redirect(url_for('admin_dashboard'))

@app.route('/update-debtor-specs', methods=['POST'])
def update_debtor_specs():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    debtor_id = request.form.get('debtor_id')
    principal = float(request.form.get('principal') or 0)
    interest_type = request.form.get('interest_type')
    interest_rate = float(request.form.get('interest_rate') or 0)
    try:
        supabase.table("debtors").update({
            'principal': principal,
            'interest_type': interest_type,
            'interest_rate': interest_rate
        }).eq('id', debtor_id).execute()
    except Exception as e:
        print(f"Update Specs Error: {e}")
    return redirect(url_for('admin_dashboard'))

@app.route('/update-bank', methods=['POST'])
def update_bank():
    if not session.get('admin_logged_in'): return {'success': False}
    data = request.json
    b_name = data.get('bank')
    amount = float(data.get('amount') or 0)
    if b_name in bank_accounts:
        bank_accounts[b_name] = amount
        return {'success': True}
    return {'success': False}

@app.route('/submit-payment', methods=['POST'])
def submit_payment():
    if not session.get('admin_logged_in'): return {'success': False}
    data = request.json
    debtor_id = data.get('debtor_id')
    amount = float(data.get('amount') or 0)
    fine = float(data.get('fine') or 0)
    discount = float(data.get('discount') or 0)
    custom_date = data.get('date')

    if custom_date:
        try:
            date_obj = datetime.strptime(custom_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y') + ' ' + datetime.now().strftime('%H:%M')
        except:
            formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')
    else:
        formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')

    try:
        res = supabase.table("debtors").select("*").eq('id', debtor_id).execute()
        if res.data:
            debtor = res.data[0]
            txs = debtor.get('transactions', [])
            if isinstance(txs, str):
                try: txs = json.loads(txs)
                except: txs = []
            
            profit_earned = amount - discount
            txs.append({
                'date': formatted_date, 
                'type': 'รับชำระหนี้', 
                'raw_amount': amount, 
                'fine': fine, 
                'discount': discount, 
                'profit': profit_earned
            })
            
            new_profit = float(debtor.get('accumulated_profit', 0)) + profit_earned
            supabase.table("debtors").update({
                'transactions': json.dumps(txs),
                'accumulated_profit': new_profit
            }).eq('id', debtor_id).execute()
            return {'success': True}
    except Exception as e:
        print(f"Payment Error: {e}")
    return {'success': False}

@app.route('/submit-old-payment', methods=['POST'])
def submit_old_payment():
    if not session.get('admin_logged_in'): return {'success': False}
    data = request.json
    phone = data.get('phone')
    amount = float(data.get('amount') or 0)
    custom_date = data.get('date')

    if custom_date:
        try:
            date_obj = datetime.strptime(custom_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y') + ' ' + datetime.now().strftime('%H:%M')
        except:
            formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')
    else:
        formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')

    try:
        res = supabase.table("debtors").select("*").eq('phone', phone).execute()
        if res.data:
            for debtor in res.data:
                current_old = float(debtor.get('old_arrears', 0))
                new_old = max(0, current_old - amount)
                
                txs = debtor.get('transactions', [])
                if isinstance(txs, str):
                    try: txs = json.loads(txs)
                    except: txs = []
                
                txs.append({
                    'date': formatted_date,
                    'type': 'รับชำระยอดค้างเก่า',
                    'raw_amount': amount,
                    'profit': 0
                })

                supabase.table("debtors").update({
                    'old_arrears': new_old,
                    'transactions': json.dumps(txs)
                }).eq('id', debtor['id']).execute()
            return {'success': True}
    except Exception as e:
        print(f"Old Payment Error: {e}")
    return {'success': False}

@app.route('/update-old-arrears', methods=['POST'])
def update_old_arrears():
    if not session.get('admin_logged_in'): return {'success': False}
    data = request.json
    phone = data.get('phone')
    amount = float(data.get('amount') or 0)
    try:
        res = supabase.table("debtors").select("id").eq('phone', phone).execute()
        if res.data:
            for debtor in res.data:
                supabase.table("debtors").update({'old_arrears': amount}).eq('id', debtor['id']).execute()
            return {'success': True}
    except Exception as e:
        print(f"Update Old Arrears Error: {e}")
    return {'success': False}

@app.route('/submit-application', methods=['POST'])
def submit_application():
    amount = float(request.form.get('amount') or 0)
    name = request.form.get('name')
    phone = request.form.get('phone') or session.get('verified_phone', '')
    facebook = request.form.get('facebook')
    account = request.form.get('account')
    bank = request.form.get('bank', '')
    signature_data = request.form.get('signature_data', '')

    new_entry = {
        'id': f"#{random.randint(100000, 999999)}",
        'name': name,
        'phone': phone,
        'facebook': facebook,
        'acc': account,
        'bank': bank,
        'principal': amount,
        'payment_term': 'รายวัน',
        'status': 'รออนุมัติ',
        'interest_type': 'ดอกลอย',
        'interest_rate': 100,
        'accumulated_profit': 0,
        'old_arrears': 0,
        'signature_data': signature_data,
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'transactions': json.dumps([{
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 
            'type': 'ยื่นขอกู้เงินออนไลน์', 
            'raw_amount': amount
        }])
    }
    
    # บันทึกข้อมูลลงใน Supabase ตาราง debtors
    try:
        supabase.table("debtors").insert(new_entry).execute()
    except Exception as e:
        print(f"Supabase Insert Error: {e}")

    # ส่งแจ้งเตือนเข้า Telegram ทันที
    alert_msg = f"🚨 <b>มีคำขอกู้เงินใหม่เข้ามา!</b>\n👤 ชื่อ: {name}\n📞 เบอร์: {phone}\n💰 วงเงินกู้: ฿{amount:,.2f}\n🏦 ธนาคาร: {bank}"
    send_telegram_alert(alert_msg)

    session.pop('member_verified', None)
    return "<script>alert('ยื่นคำขอกู้เงินและส่งสัญญาเรียบร้อยแล้ว!'); window.location.href='/apply';</script>"

@app.route('/clear-data')
def clear_data():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    try:
        res = supabase.table("debtors").select("id").execute()
        for row in res.data: supabase.table("debtors").delete().eq('id', row['id']).execute()
    except Exception as e: print(e)
    pending_otp_requests.clear()
    return "<script>alert('ล้างข้อมูลสำเร็จ'); window.location.href='/';</script>"

@app.route('/export-csv')
def export_csv():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    debtors_database = get_debtors_from_db()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Principal', 'Status', 'Date'])
    for d in debtors_database: writer.writerow([d['id'], d['name'], d['phone'], d['principal'], d['status'], d['date']])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=debtors.csv"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
