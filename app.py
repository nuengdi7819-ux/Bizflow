from flask import Flask, render_template_string, request, Response, redirect, url_for, session, jsonify
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
            if 'principal' not in d:
                d['principal'] = 0
            if 'profit' not in d:
                d['profit'] = 0
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

@app.route('/request-otp', methods=['POST'])
def request_otp():
    phone = request.form.get('phone') or (request.json.get('phone') if request.is_json else None)
    name = request.form.get('name') or (request.json.get('name') if request.is_json else 'ลูกค้าหน้าบ้าน')
    
    if not phone:
        return jsonify({'success': False, 'message': 'กรุณาระบุเบอร์โทรศัพท์'}), 400

    otp_code = str(random.randint(100000, 999999))
    req_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    otp_item = {
        'id': len(pending_otp_requests) + 1,
        'name': name,
        'phone': phone,
        'otp': otp_code,
        'time': req_time,
        'status': 'รออนุมัติ'
    }
    pending_otp_requests.insert(0, otp_item)

    msg = (
        f"<b>🔑 มีคำขอรหัส OTP ใหม่!</b>\n"
        f"<b>ชื่อ:</b> {name}\n"
        f"<b>เบอร์โทร:</b> {phone}\n"
        f"<b>รหัส OTP:</b> <code>{otp_code}</code>\n"
        f"<b>เวลา:</b> {req_time}"
    )
    send_telegram_alert(msg)

    return jsonify({
        'success': True, 
        'message': 'ส่งคำขอ OTP เรียบร้อยแล้ว ระบบได้แจ้งเตือนแอดมินทาง Telegram แล้ว',
        'otp_ref': otp_code
    })

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการลูกหนี้ & บัญชีการเงิน</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #0f172a; color: #f8fafc; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col">
    <div class="p-6 max-w-7xl mx-auto w-full space-y-6">
        <header class="flex justify-between items-center border-b border-slate-800 pb-4">
            <h1 class="text-2xl font-black text-purple-400">BizFlow+ Admin Dashboard</h1>
            <a href="/apply" target="_blank" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-bold">เปิดหน้าบ้านสมาชิก (/apply)</a>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div onclick="alert('แสดงประวัติยอดค้างเก่าทั้งหมด')" class="p-5 rounded-2xl bg-amber-600 text-white cursor-pointer hover:opacity-90">
                <h3 class="text-xs uppercase font-bold">ยอดค้างเก่าคงเหลือ</h3>
                <p class="text-2xl font-black mt-2">฿{{ total_old_arrears | format_num }}</p>
                <span class="text-[10px] underline mt-1 block">คลิกดูประวัติ</span>
            </div>
            <div onclick="alert('แสดงประวัติเงินต้นคงค้างทั้งหมด')" class="p-5 rounded-2xl bg-rose-700 text-white cursor-pointer hover:opacity-90">
                <h3 class="text-xs uppercase font-bold">เงินต้นคงค้าง</h3>
                <p class="text-2xl font-black mt-2">฿{{ total_principal | format_num }}</p>
                <span class="text-[10px] underline mt-1 block">คลิกดูประวัติ</span>
            </div>
            <div onclick="alert('แสดงประวัติยอดเก็บได้วันนี้')" class="p-5 rounded-2xl bg-blue-600 text-white cursor-pointer hover:opacity-90">
                <h3 class="text-xs uppercase font-bold">ยอดเก็บได้วันนี้</h3>
                <p class="text-2xl font-black mt-2">฿{{ collected_today | format_num }}</p>
                <span class="text-[10px] underline mt-1 block">คลิกดูประวัติ</span>
            </div>
            <div onclick="alert('แสดงประวัติกำไรสะสมรวม')" class="p-5 rounded-2xl bg-emerald-600 text-white cursor-pointer hover:opacity-90">
                <h3 class="text-xs uppercase font-bold">กำไรสะสมรวม</h3>
                <p class="text-2xl font-black mt-2">฿{{ total_profit | format_num }}</p>
                <span class="text-[10px] underline mt-1 block">คลิกดูประวัติ</span>
            </div>
        </div>

        <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <h2 class="text-lg font-bold text-purple-300 mb-4">🔑 รายการขอรหัส OTP จากลูกค้า (รออนุมัติ)</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-800 text-slate-300">
                        <tr><th class="p-3">ชื่อ</th><th class="p-3">เบอร์โทร</th><th class="p-3">OTP</th><th class="p-3">เวลา</th><th class="p-3">สถานะ</th></tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        {% for otp in pending_otp_requests %}
                        <tr>
                            <td class="p-3">{{ otp.name }}</td>
                            <td class="p-3 font-mono">{{ otp.phone }}</td>
                            <td class="p-3 font-mono text-amber-400 font-bold">{{ otp.otp }}</td>
                            <td class="p-3">{{ otp.time }}</td>
                            <td class="p-3"><span class="px-2 py-1 bg-amber-500/20 text-amber-300 rounded">{{ otp.status }}</span></td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5" class="p-4 text-center text-slate-500">ยังไม่มีคำขอ OTP ในขณะนี้</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def admin_dashboard():
    debtors = get_debtors_from_db()
    total_old_arrears = sum(float(d.get('old_arrears', 0)) for d in debtors)
    total_principal = sum(float(d.get('principal', 0)) for d in debtors if d.get('status', 'ปกติ') == 'ปกติ')
    total_profit = sum(float(d.get('profit', 0)) for d in debtors)
    collected_today = 0
    
    return render_template_string(
        ADMIN_TEMPLATE,
        debtors=debtors,
        total_old_arrears=total_old_arrears,
        total_principal=total_principal,
        total_profit=total_profit,
        collected_today=collected_today,
        pending_otp_requests=pending_otp_requests,
        bank_accounts=bank_accounts,
        personal_finance=personal_finance
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
