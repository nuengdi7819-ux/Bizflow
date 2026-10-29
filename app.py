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

# ตั้งค่าการเชื่อมต่อ Supabase
SUPABASE_URL = "https://pdpeqsubrbmdjxgmtjpy.supabase.co"
SUPABASE_KEY = "sb_publishable_ZSKb3jQeqfP8oSIajLhFWA_sOBMd4-H"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ฟังก์ชันช่วยดึงข้อมูลลูกหนี้จาก Supabase (ถ้ามีตาราง debtors)
def get_debtors_from_db():
    try:
        response = supabase.table("debtors").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
        return []

# ระบบเก็บข้อมูลการขอ OTP ชั่วคราวของสมาชิก
pending_otp_requests = []

# ฐานข้อมูลผู้ใช้งานระบบหลังบ้าน
users_database = [
    {'id': 1, 'name': 'Nice (แอดมิน)', 'username': 'nice', 'password': '022540', 'role': 'Super Admin', 'status': 'ใช้งานอยู่', 'last_login': '30/10/2026 08:30'},
    {'id': 2, 'name': 'Nueng (แอดมิน)', 'username': 'nueng', 'password': '909090', 'role': 'Super Admin', 'status': 'ใช้งานอยู่', 'last_login': '30/10/2026 08:30'}
]

activity_logs = [
    {'time': '30/10/2026 08:30', 'user': 'System', 'action': 'เริ่มต้นระบบหลังบ้าน', 'ip': '127.0.0.1'}
]

system_config = {
    'company_name': 'BizFlow+ Financial Services',
    'telegram_token': '9203750510:AAFJhUvWRf4mOSozUSkz0I0I9Jca-xImuTo',
    'telegram_chat_id': '1880260879'
}

bank_accounts = {
    'kbank': 0,
    'scb': 0,
    'cash': 0
}

# ข้อมูลหนี้ประจำและค่าใช้จ่ายครัวเรือน
household_debts = [
    {'name': 'Line BK', 'outstanding': 9200, 'detail': 'ดอกเบี้ย 20%, ปิดจบเดือนที่ 1'},
    {'name': 'สินเชื่อ ttb', 'outstanding': 125441, 'detail': 'ดอกเบี้ย 19%, ปิดจบเดือนที่ 2-5'},
    {'name': 'หนี้ทองคำ 4 บาท', 'outstanding': 240000, 'detail': 'ดอกเบี้ย 15%, ไถ่ถอนเดือนที่ 6-12'}
]

household_expenses = [
    {'name': 'งดรถยนต์', 'amount': 13588, 'note': 'เหลือ 59 งวด'},
    {'name': 'งดมอเตอร์ไซค์ 1', 'amount': 3396, 'note': 'เหลือ 10 งวด'},
    {'name': 'งดมอเตอร์ไซค์ 2', 'amount': 2122, 'note': 'เหลือ 21 งวด'},
    {'name': 'ประกันรถยนต์ 1', 'amount': 1540, 'note': 'ผ่อน 10 เดือน/ปี'},
    {'name': 'ประกันรถยนต์ 2', 'amount': 1860, 'note': 'เหลืออีก 2 เดือนจบ'},
    {'name': 'ค่าห้อง', 'amount': 7000, 'note': 'จ่ายประจำ'},
    {'name': 'แชร์วง 5 หมื่น', 'amount': 3000, 'note': 'เหลือ 3 งวด (จ่ายทุก 15)'},
    {'name': 'แชร์วง 9 หมื่น', 'amount': 5000, 'note': 'เหลือ 17 งวด (จ่ายทุก 27)'},
    {'name': 'ประกันชีวิต', 'amount': 2100, 'note': 'จ่ายประจำเดือน'},
    {'name': 'ค่าเน็ต', 'amount': 1500, 'note': 'จ่ายประจำเดือน'}
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

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - เข้าสู่ระบบหลังบ้าน (Admin Login)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 border border-purple-100 text-slate-800">
        <div class="text-center mb-6">
            <div class="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center font-black text-2xl mx-auto mb-3 shadow-lg">B</div>
            <h1 class="text-xl font-black text-slate-900">BizFlow+ ระบบหลังบ้าน</h1>
            <p class="text-xs text-slate-500 mt-1">กรุณาเข้าสู่ระบบด้วย Username และ Password ของแอดมิน</p>
        </div>
        {% if error %}
        <div class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl text-center font-bold">{{ error }}</div>
        {% endif %}
        <form action="/admin-login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">Username</label>
                <input type="text" name="username" required placeholder="ชื่อผู้ใช้งานแอดมิน" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">Password</label>
                <input type="password" name="password" required placeholder="รหัสผ่าน" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
            </div>
            <button type="submit" class="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow-lg mt-2">เข้าสู่ระบบหลังบ้าน</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการลูกหนี้ & บัญชีการเงิน</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #f8fafc; }
        .sidebar-item-active {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(126, 34, 206, 0.2) 100%);
            border: 1px solid rgba(192, 132, 252, 0.4);
            color: #f3e8ff;
        }
        .sidebar-bg { background: linear-gradient(180deg, #18092e 0%, #0d061a 50%, #110726 100%); }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col md:flex-row">

    <div class="md:hidden bg-[#18092e] text-white p-4 flex items-center justify-between shadow-md sticky top-0 z-40">
        <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-xl bg-purple-600 flex items-center justify-center font-black">B</div>
            <span class="font-bold text-lg">BizFlow <span class="text-xs bg-purple-500 px-1.5 py-0.5 rounded">PLUS</span></span>
        </div>
        <button onclick="toggleSidebar()" class="text-purple-300 hover:text-white text-xl p-2"><i class="fa-solid fa-bars"></i></button>
    </div>

    <aside id="sidebar" class="w-72 sidebar-bg text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl h-screen fixed md:static inset-y-0 left-0 z-50 transform -translate-x-full md:translate-x-0 transition-transform duration-300 border-r border-purple-900/35 overflow-y-auto">
        <div>
            <div class="p-6 pb-6 border-b border-purple-900/40 flex items-center justify-between">
                <div class="flex items-center space-x-3.5">
                    <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 to-violet-400 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg">B</div>
                    <div>
                        <span class="text-2xl font-black text-white">BizFlow <span class="bg-purple-400 text-slate-950 text-xs px-2 py-0.5 rounded font-bold">PLUS</span></span>
                        <p class="text-xs text-purple-300/70">ระบบจัดการลูกหนี้ & บัญชี</p>
                    </div>
                </div>
                <button onclick="toggleSidebar()" class="md:hidden text-purple-300 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <nav class="p-4 space-y-4">
                <div>
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">📊 1. ภาพรวม & การเงิน</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('dashboard')" id="nav-dashboard" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs sidebar-item-active">
                            <i class="fa-solid fa-chart-pie text-sm text-purple-400 w-5"></i><span>แดชบอร์ดหลัก</span>
                        </button>
                        <button onclick="switchTab('banking')" id="nav-banking" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-building-columns text-sm text-sky-400 w-5"></i><span>บัญชีธนาคาร & พื้นที่ส่วนตัว</span>
                        </button>
                    </div>
                </div>

                <div>
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">👥 2. จัดการลูกหนี้ & คำขอกู้</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('debtors')" id="nav-debtors" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-users text-sm text-amber-400 w-5"></i><span>รายชื่อลูกหนี้ & คำขอกู้</span>
                        </button>
                        <button onclick="switchTab('otp_requests')" id="nav-otp_requests" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-key text-sm text-rose-400 w-5"></i><span>🔑 อนุมัติรหัส OTP ลูกค้า</span>
                        </button>
                        <a href="/apply" target="_blank" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-emerald-300 hover:bg-emerald-950/40 border border-emerald-500/30 mt-1">
                            <i class="fa-solid fa-globe text-sm text-emerald-400 w-5"></i><span>🔗 หน้าบ้านสมาชิก (/apply)</span>
                        </a>
                    </div>
                </div>

                <div>
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">💰 3. การชำระเงิน & ธุรกรรม</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('transactions')" id="nav-transactions" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-receipt text-sm text-emerald-400 w-5"></i><span>บันทึกการชำระหนี้ / สลิป</span>
                        </button>
                    </div>
                </div>

                <div>
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">📄 4. สัญญา & รายงาน</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('contracts')" id="nav-contracts" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-file-contract text-sm text-indigo-400 w-5"></i><span>จัดการสัญญาเงินกู้ดิจิทัล</span>
                        </button>
                        <button onclick="switchTab('annual_reports')" id="nav-annual_reports" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-chart-line text-sm text-teal-400 w-5"></i><span>รายงานผลประกอบการประจำปี</span>
                        </button>
                    </div>
                </div>

                <div>
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">⚙️ 5. ตั้งค่า & ระบบหลังบ้าน</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('settings')" id="nav-settings" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-sliders text-sm text-pink-400 w-5"></i><span>ตั้งค่าระบบหลังบ้าน</span>
                        </button>
                    </div>
                </div>
            </nav>
        </div>
        <div class="p-4 border-t border-purple-900/40 space-y-3">
            <div class="text-xs text-purple-300/80 flex items-center justify-between">
                <span>แอดมิน: <b class="text-white">{{ session.get('admin_user', 'Admin') }}</b></span>
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>
            <a href="/admin-logout" class="w-full py-2 bg-rose-600/80 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow flex items-center justify-center space-x-1.5 transition">
                <i class="fa-solid fa-right-from-bracket"></i><span>ออกจากระบบหลังบ้าน</span>
            </a>
        </div>
    </aside>

    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50 w-full">
        <header class="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 md:px-8 py-4 flex items-center justify-between shadow-sm">
            <h2 id="page-title" class="text-lg md:text-xl font-bold text-slate-800">แดชบอร์ดหลัก</h2>
            <div class="flex items-center space-x-4">
                <div class="relative cursor-pointer p-2 hover:bg-purple-50 rounded-xl transition" onclick="switchTab('debtors')" title="คลิกดูรายการคำขอกู้ใหม่">
                    <i class="fa-solid fa-bell text-2xl text-purple-600 hover:text-purple-800"></i>
                    {% set pending_count = debtors | selectattr('status', 'equalto', 'รออนุมัติ') | list | length %}
                    <span id="bell-badge" class="absolute top-0 right-0 bg-rose-600 text-white font-black text-[11px] px-1.5 py-0.5 rounded-full shadow-md {% if pending_count == 0 %}hidden{% endif %}">
                        {{ pending_count }}
                    </span>
                </div>
                <a href="/apply" target="_blank" class="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium text-xs md:text-sm shadow-md flex items-center space-x-1.5">
                    <i class="fa-solid fa-external-link-alt"></i><span>เปิดหน้าบ้านสมาชิก</span>
                </a>
            </div>
        </header>

        <div class="p-4 md:p-8 space-y-6">

            <!-- Section: แดชบอร์ดหลัก -->
            <div id="section-dashboard" class="space-y-6">
                <div class="bg-gradient-to-r from-purple-700 to-indigo-800 text-white p-6 rounded-3xl shadow-xl flex flex-wrap items-center justify-between gap-4">
                    <div>
                        <h3 class="text-xl font-black">จัดการระบบลูกหนี้ & เงินกู้ด่วน</h3>
                        <p class="text-xs text-purple-200 mt-1">แอดมินสามารถเพิ่มรายการสมาชิก/ปล่อยกู้ย้อนหลัง หรือฝากทำรายการได้ทันที</p>
                    </div>
                    <button onclick="openAddMemberModal()" class="px-5 py-3 bg-white text-purple-900 rounded-2xl font-black text-xs shadow-lg hover:bg-purple-50 transition flex items-center space-x-2">
                        <i class="fa-solid fa-user-plus text-base text-purple-600"></i><span>+ เพิ่มรายการสมาชิก (แอดมินทำเอง)</span>
                    </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                    <div onclick="openBoxModal('old_arrears')" class="p-5 rounded-2xl bg-amber-500 text-white shadow-lg cursor-pointer hover:opacity-90 transition transform hover:-translate-y-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-amber-100 uppercase tracking-wider">📁 ยอดค้างเก่าคงเหลือ</span>
                            <i class="fa-solid fa-folder-open text-amber-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">฿0.00</h3>
                        <p class="text-[10px] text-amber-100 mt-1 underline">คลิกดูประวัติ/ที่มาที่ไป</p>
                    </div>

                    <div onclick="openBoxModal('principal')" class="p-5 rounded-2xl bg-rose-700 text-white shadow-lg cursor-pointer hover:opacity-90 transition transform hover:-translate-y-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-rose-200 uppercase tracking-wider">💼 เงินต้นคงค้าง</span>
                            <i class="fa-solid fa-briefcase text-rose-300 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">฿{{ total_principal | format_num }}</h3>
                        <p class="text-[10px] text-rose-200 mt-1 underline">คลิกดูประวัติ/ที่มาที่ไป</p>
                    </div>

                    <div onclick="openBoxModal('collected_today')" class="p-5 rounded-2xl bg-blue-600 text-white shadow-lg cursor-pointer hover:opacity-90 transition transform hover:-translate-y-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-blue-200 uppercase tracking-wider">💵 ยอดเก็บได้วันนี้</span>
                            <i class="fa-solid fa-hand-holding-dollar text-blue-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">฿{{ collected_today | format_num }}</h3>
                        <p class="text-[10px] text-blue-200 mt-1 underline">คลิกดูประวัติ/ที่มาที่ไป</p>
                    </div>

                    <div onclick="openBoxModal('profit')" class="p-5 rounded-2xl bg-emerald-600 text-white shadow-lg cursor-pointer hover:opacity-90 transition transform hover:-translate-y-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-emerald-200 uppercase tracking-wider">💰 กำไรสะสม (รวม)</span>
                            <i class="fa-solid fa-sack-dollar text-emerald-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">฿{{ total_profit | format_num }}</h3>
                        <p class="text-[10px] text-emerald-200 mt-1 underline">คลิกดูประวัติ/ที่มาที่ไป</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                        <h4 class="font-bold text-slate-800 text-base flex items-center">
                            <i class="fa-solid fa-calendar-day text-purple-600 mr-2"></i> รายการที่มีการทำธุรกรรมวันนี้ ({{ today_date }})
                        </h4>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr>
                                        <th class="p-2.5">ชื่อ-นามสกุล</th>
                                        <th class="p-2.5">ประเภท</th>
                                        <th class="p-2.5 text-right">ยอดเงิน</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% if today_transactions %}
                                        {% for tx in today_transactions %}
                                        <tr>
                                            <td class="p-2.5 font-bold text-purple-900 cursor-pointer hover:underline" onclick="openDebtorDetailByName('{{ tx.name }}')">{{ tx.name }}</td>
                                            <td class="p-2.5 text-slate-600">{{ tx.type }}</td>
                                            <td class="p-2.5 text-right font-mono font-bold text-emerald-600">฿{{ tx.amount | format_num }}</td>
                                        </tr>
                                        {% endfor %}
                                    {% else %}
                                        <tr><td colspan="3" class="p-4 text-center text-slate-400">ยังไม่มีธุรกรรมในวันนี้</td></tr>
                                    {% endif %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                        <h4 class="font-bold text-slate-800 text-base flex items-center">
                            <i class="fa-solid fa-clock-rotate-left text-amber-500 mr-2"></i> รายการที่มีกำหนดชำระคืนวันนี้ ({{ today_date }})
                        </h4>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr>
                                        <th class="p-2.5">ชื่อ-นามสกุล</th>
                                        <th class="p-2.5">วงเงินกู้</th>
                                        <th class="p-2.5 text-right">สถานะ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% if due_today_list %}
                                        {% for d in due_today_list %}
                                        <tr>
                                            <td class="p-2.5 font-bold text-purple-900 cursor-pointer hover:underline" onclick="openDebtorDetail('{{ d.id }}')">{{ d.name }}</td>
                                            <td class="p-2.5 font-mono">฿{{ d.principal | format_num }}</td>
                                            <td class="p-2.5 text-right"><span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold">ถึงกำหนดคืน</span></td>
                                        </tr>
                                        {% endfor %}
                                    {% else %}
                                        <tr><td colspan="3" class="p-4 text-center text-slate-400">ไม่มีรายการครบกำหนดชำระคืนในวันนี้</td></tr>
                                    {% endif %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: บัญชีธนาคาร & พื้นที่ส่วนตัวบริหารการเงินครัวเรือน -->
            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                            <button onclick="toggleEditBank('kbank')" class="text-emerald-200 hover:text-white text-xs bg-emerald-700/60 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-kbank-display" class="text-3xl font-black tracking-tight py-2">฿{{ bank_kbank | format_num }}</div>
                        <div id="bank-kbank-edit" class="hidden space-y-2">
                            <input type="number" id="bank-kbank-input" value="{{ bank_kbank }}" class="w-full px-3 py-2 bg-emerald-700 border border-emerald-500 rounded-xl text-xl font-black text-white">
                            <button onclick="saveBankBalance('kbank')" class="w-full py-1.5 bg-white text-emerald-800 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-purple-700 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">ธนาคารไทยพาณิชย์ (SCB)</h4>
                            <button onclick="toggleEditBank('scb')" class="text-purple-200 hover:text-white text-xs bg-purple-800/60 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-scb-display" class="text-3xl font-black tracking-tight py-2">฿{{ bank_scb | format_num }}</div>
                        <div id="bank-scb-edit" class="hidden space-y-2">
                            <input type="number" id="bank-scb-input" value="{{ bank_scb }}" class="w-full px-3 py-2 bg-purple-800 border border-purple-600 rounded-xl text-xl font-black text-white">
                            <button onclick="saveBankBalance('scb')" class="w-full py-1.5 bg-white text-purple-900 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-slate-800 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">เงินสด (Cash)</h4>
                            <button onclick="toggleEditBank('cash')" class="text-slate-300 hover:text-white text-xs bg-slate-700 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-cash-display" class="text-3xl font-black tracking-tight py-2">฿{{ bank_cash | format_num }}</div>
                        <div id="bank-cash-edit" class="hidden space-y-2">
                            <input type="number" id="bank-cash-input" value="{{ bank_cash }}" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-xl text-xl font-black text-white">
                            <button onclick="saveBankBalance('cash')" class="w-full py-1.5 bg-white text-slate-900 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-3xl border border-purple-200 p-6 md:p-8 shadow-xl space-y-6">
                    <div class="flex flex-wrap items-center justify-between border-b pb-4 gap-4">
                        <div>
                            <h3 class="text-xl font-black text-purple-900 flex items-center">
                                <i class="fa-solid fa-house-chimney-user mr-2.5 text-purple-600"></i> พื้นที่ส่วนตัว: บริหารการเงินครัวเรือน & หนี้สินประจำ
                            </h3>
                            <p class="text-xs text-slate-500 mt-1">ดึงเงินจากกระเป๋าต่างๆ มาจัดสรรสัดส่วนค่ากิน, เงินออม และหนี้สินประจำเดือน</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="px-3 py-1.5 bg-purple-100 text-purple-800 rounded-xl font-bold text-xs">รายได้รวม: ฿55,000 / เดือน</span>
                            <span class="px-3 py-1.5 bg-emerald-100 text-emerald-800 rounded-xl font-bold text-xs">รวมจ่ายคงที่: ฿41,106</span>
                        </div>
                    </div>

                    <div class="space-y-3">
                        <h4 class="font-bold text-sm text-slate-800 flex items-center">
                            <i class="fa-solid fa-triangle-exclamation text-rose-500 mr-2"></i> รายการหนี้ที่ต้องเร่งปลด (ยอดคงเหลือ & สัดส่วน)
                        </h4>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-2xl overflow-hidden">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr>
                                        <th class="p-3">รายการหนี้</th>
                                        <th class="p-3 text-right">ยอดคงเหลือ (บาท)</th>
                                        <th class="p-3">รายละเอียด / แผนการปิดจบ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% for debt in household_debts %}
                                    <tr>
                                        <td class="p-3 font-bold text-slate-900">{{ debt.name }}</td>
                                        <td class="p-3 text-right font-mono font-bold text-rose-600 text-sm">฿{{ debt.outstanding | format_num }}</td>
                                        <td class="p-3 text-slate-600">{{ debt.detail }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="space-y-3 pt-4">
                        <h4 class="font-bold text-sm text-slate-800 flex items-center">
                            <i class="fa-solid fa-file-invoice-dollar text-blue-600 mr-2"></i> รายการค่าใช้จ่ายประจำ (Fixed Expenses) ต่อเดือน
                        </h4>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-2xl overflow-hidden">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr>
                                        <th class="p-3">รายการค่าใช้จ่าย</th>
                                        <th class="p-3 text-right">จำนวนเงิน (บาท)</th>
                                        <th class="p-3">รายละเอียดสถานะ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% for exp in household_expenses %}
                                    <tr>
                                        <td class="p-3 font-bold text-slate-900">{{ exp.name }}</td>
                                        <td class="p-3 text-right font-mono font-bold text-blue-600 text-sm">฿{{ exp.amount | format_num }}</td>
                                        <td class="p-3 text-slate-600">{{ exp.note }}</td>
                                    </tr>
                                    {% endfor %}
                                    <tr class="bg-purple-50 font-bold">
                                        <td class="p-3 text-purple-900">รวมค่าใช้จ่ายคงที่ทั้งหมด</td>
                                        <td class="p-3 text-right font-mono text-purple-900 text-sm">฿41,106.00</td>
                                        <td class="p-3 text-purple-700">หักออกจากรายได้เพื่อบริหารเงินออม & ค่ากิน</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: จัดการลูกหนี้ & คำขอกู้ -->
            <div id="section-debtors" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-4 md:p-6 shadow-sm overflow-x-auto">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div class="flex items-center gap-2">
                            <button onclick="setFilterStatus('ทั้งหมด')" id="filter-all" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white">ทั้งหมด</button>
                            <button onclick="setFilterStatus('รออนุมัติ')" id="filter-pending" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-amber-50 text-amber-800 border border-amber-300">รออนุมัติ</button>
                            <button onclick="setFilterStatus('ปกติ')" id="filter-approved" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-600">อนุมัติแล้ว</button>
                        </div>
                        <input type="text" id="searchInput" oninput="filterDebtorsTable()" placeholder="🔍 ค้นหาสมาชิกด้วยชื่อ หรือเบอร์โทร..." class="px-4 py-2 bg-slate-50 border rounded-xl text-xs w-72">
                    </div>

                    <table class="w-full text-left text-sm min-w-[750px]">
                        <thead class="bg-slate-50 text-slate-500">
                            <tr>
                                <th class="p-3.5">ชื่อ-เบอร์โทร (คลิกดูประวัติ)</th>
                                <th class="p-3.5">ประเภทดอกเบี้ย</th>
                                <th class="p-3.5">เงินต้นกู้</th>
                                <th class="p-3.5">รูปแบบการชำระ</th>
                                <th class="p-3.5">สถานะ</th>
                                <th class="p-3.5 text-center">จัดการ / รายละเอียด</th>
                            </tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y divide-slate-100">
                            {% for d in debtors %}
                            <tr class="debtor-row" data-status="{{ d.status }}" data-search="{{ d.name }} {{ d.phone }}">
                                <td class="p-3.5">
                                    <div class="font-bold text-purple-900 cursor-pointer hover:underline text-base" onclick="openDebtorDetail('{{ d.id }}')">
                                        <i class="fa-solid fa-user-circle mr-1 text-purple-600"></i>{{ d.name }}
                                    </div>
                                    <div class="text-xs text-slate-500 font-mono">{{ d.phone }}</div>
                                </td>
                                <td class="p-3.5">
                                    <span class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-bold">{{ d.interest_type or 'ยังไม่กำหนด' }}</span>
                                    {% if d.interest_type == 'ดอกลอย' %}
                                    <div class="text-[10px] text-slate-500 mt-0.5">ดร. ฿{{ d.interest_rate | format_num }}/วัน</div>
                                    {% endif %}
                                </td>
                                <td class="p-3.5 font-mono font-bold">฿{{ d.principal | format_num }}</td>
                                <td class="p-3.5 text-xs font-semibold">{{ d.payment_term }}</td>
                                <td class="p-3.5">
                                    <span class="px-2.5 py-1 rounded-full text-xs font-bold {% if d.status == 'รออนุมัติ' %}bg-amber-100 text-amber-800{% else %}bg-emerald-100 text-emerald-800{% endif %}">
                                        {{ d.status }}
                                    </span>
                                </td>
                                <td class="p-3.5 text-center">
                                    <button onclick="openDebtorDetail('{{ d.id }}')" class="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow">
                                        <i class="fa-solid fa-address-card mr-1"></i> ดูประวัติ & จัดการ
                                    </button>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="6" class="p-6 text-center text-slate-400">ยังไม่มีข้อมูลลูกหนี้ในระบบ</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab: อนุมัติรหัส OTP ลูกค้า (เรียงเบอร์ล่าสุดขึ้นบนสุด) -->
            <div id="section-otp_requests" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-key text-rose-500 mr-2"></i> คำขอรหัส OTP จากสมาชิกหน้าเว็บ (เรียงลำดับล่าสุดขึ้นบน)
                    </h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs bg-white rounded-xl border">
                            <thead class="bg-slate-100 text-slate-600">
                                <tr>
                                    <th class="p-3">เบอร์โทรศัพท์มือถือ</th>
                                    <th class="p-3">เวลาที่ขอ OTP</th>
                                    <th class="p-3 text-center">รหัส OTP ชั่วคราว</th>
                                    <th class="p-3 text-right">จัดการ</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y">
                                {% if otp_list %}
                                    {% for item in otp_list %}
                                    <tr>
                                        <td class="p-3 font-mono font-bold text-purple-800 text-sm"><i class="fa-solid fa-phone mr-1"></i>{{ item.phone }}</td>
                                        <td class="p-3 text-slate-500">{{ item.time }}</td>
                                        <td class="p-3 text-center"><span class="px-3 py-1.5 bg-rose-100 text-rose-800 rounded-xl font-mono font-black text-base">{{ item.otp }}</span></td>
                                        <td class="p-3 text-right"><a href="/clear-otp?phone={{ item.phone }}" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg font-bold">ลบ OTP</a></td>
                                    </tr>
                                    {% endfor %}
                                {% else %}
                                    <tr><td colspan="4" class="p-6 text-center text-slate-400">ยังไม่มีเบอร์โทรขอรหัส OTP ในขณะนี้</td></tr>
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">บันทึกการชำระหนี้ / ตัดยอดสะสม</h3>
                </div>
            </div>

            <div id="section-contracts" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-file-contract text-indigo-600 mr-2"></i> จัดการสัญญาเงินกู้ดิจิทัล
                    </h3>
                </div>
            </div>

            <div id="section-annual_reports" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-chart-line text-teal-600 mr-2"></i> รายงานสรุปผลประกอบการประจำปี
                    </h3>
                </div>
            </div>

            <div id="section-settings" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
                    <h3 class="text-lg font-bold text-slate-800 border-b pb-3">⚙️ ตั้งค่าระบบหลังบ้านขั้นสูง</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="p-4 bg-slate-50 border rounded-2xl space-y-3">
                            <h4 class="text-xs font-bold text-purple-900 uppercase">1. ผู้ดูแลระบบ (Admin Accounts)</h4>
                            <table class="w-full text-left text-xs bg-white rounded-xl border mb-3">
                                <thead class="bg-slate-100 text-slate-600"><tr><th class="p-2.5">ชื่อ / Username</th><th class="p-2.5">บทบาท</th></tr></thead>
                                <tbody>
                                    {% for u in users %}
                                    <tr class="border-t"><td class="p-2.5 font-bold">{{ u.name }}</td><td class="p-2.5 text-purple-700 font-semibold">{{ u.role }}</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        <div class="p-4 bg-purple-50/50 border border-purple-200 rounded-2xl space-y-3">
                            <h4 class="text-xs font-bold text-purple-900 uppercase">2. จัดการฐานข้อมูล</h4>
                            <div class="flex gap-2 pt-1">
                                <a href="/export-csv" class="flex-1 py-2.5 bg-purple-600 text-white rounded-xl text-xs font-bold shadow text-center flex items-center justify-center space-x-1"><i class="fa-solid fa-download"></i><span>Export CSV</span></a>
                                <button onclick="if(confirm('ต้องการรีเซ็ตข้อมูลทั้งหมดจริงหรือไม่?')) { window.location.href='/clear-data'; }" class="py-2.5 px-4 bg-rose-600 text-white rounded-xl text-xs font-bold shadow">รีเซ็ตข้อมูล</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- Modal: ดูประวัติและที่มาของยอดเงินในกล่อง -->
    <div id="boxModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-purple-100 space-y-4 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b pb-3">
                <h3 id="box_modal_title" class="text-lg font-black text-slate-900">รายละเอียดที่มาของยอดเงิน</h3>
                <button onclick="closeBoxModal()" class="text-slate-400 hover:text-slate-600 font-bold text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="box_modal_content" class="space-y-3 text-xs text-slate-700"></div>
            <div class="text-right pt-2">
                <button onclick="closeBoxModal()" class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold text-xs">ปิดหน้าต่าง</button>
            </div>
        </div>
    </div>

    <!-- Modal: ประวัติและรายละเอียดลูกหนี้รายบุคคล -->
    <div id="debtorModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-3xl w-full p-6 md:p-8 shadow-2xl border border-purple-100 space-y-6 max-h-[95vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b pb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold text-lg"><i class="fa-solid fa-user"></i></div>
                    <div>
                        <h3 class="text-lg font-black text-purple-900" id="modal_debtor_fullname">ชื่อ-นามสกุล</h3>
                        <p class="text-xs text-slate-500 font-mono" id="modal_debtor_phone">เบอร์โทรศัพท์</p>
                    </div>
                </div>
                <button onclick="closeDebtorModal()" class="text-slate-400 hover:text-slate-600 font-bold text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div id="debtor_modal_content" class="space-y-5 text-xs text-slate-700"></div>

            <div class="border-t pt-4 flex flex-wrap items-center justify-between gap-3">
                <div class="flex gap-2">
                    <button onclick="alert('ฟังก์ชันบันทึกรับชำระหนี้')" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow"><i class="fa-solid fa-hand-holding-dollar mr-1"></i> บันทึกรับชำระ</button>
                    <button onclick="alert('ฟังก์ชันแก้ไขวงเงิน/ดอกเบี้ย')" class="px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-xs shadow"><i class="fa-solid fa-pen-to-square mr-1"></i> แก้ไขข้อมูลสัญญา</button>
                </div>
                <button onclick="closeDebtorModal()" class="px-5 py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-xs">ปิดหน้าต่าง</button>
            </div>
        </div>
    </div>

    <!-- Modal: แอดมินเพิ่มสมาชิก -->
    <div id="addMemberModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-purple-100 space-y-4 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b pb-3">
                <h3 class="text-lg font-black text-slate-900">เพิ่มรายการสมาชิก / ปล่อยกู้ (โดยแอดมิน)</h3>
                <button onclick="closeAddMemberModal()" class="text-slate-400 hover:text-slate-600 font-bold text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form action="/admin-add-debtor" method="POST" class="space-y-3 text-xs">
                <div>
                    <label class="block font-semibold text-slate-700 mb-1">ชื่อ - นามสกุลจริง</label>
                    <input type="text" name="name" required placeholder="เช่น สมชาย ใจดี" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm">
                </div>
                <div>
                    <label class="block font-semibold text-slate-700 mb-1">เบอร์โทรศัพท์</label>
                    <input type="text" name="phone" required placeholder="เช่น 0891234567" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-mono">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block font-semibold text-slate-700 mb-1">วงเงินต้น (บาท)</label>
                        <input type="number" name="principal" required placeholder="10000" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 mb-1">รูปแบบการชำระ</label>
                        <select name="payment_term" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
                            <option value="รายวัน">รายวัน</option>
                            <option value="กำหนดวันคืน">กำหนดวันคืน</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block font-semibold text-slate-700 mb-1">กำหนดวันครบกำหนดชำระคืน</label>
                    <input type="date" name="due_date" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block font-semibold text-slate-700 mb-1">ประเภทดอกเบี้ย</label>
                        <select name="interest_type" id="admin_interest_type" onchange="toggleAdminInterestFields()" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
                            <option value="ดอกลอย">ดอกลอย</option>
                            <option value="จบต้นดอก">จบต้นดอก</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 mb-1" id="admin_rate_label">ดอกเบี้ยต่อวัน (บาท)</label>
                        <input type="number" step="any" name="interest_input" required placeholder="100" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                    </div>
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="button" onclick="closeAddMemberModal()" class="flex-1 py-2.5 bg-slate-200 text-slate-700 rounded-xl font-bold">ยกเลิก</button>
                    <button type="submit" class="flex-1 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow">บันทึกเพิ่มสมาชิก</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        const debtorsData = {{ debtors | tojson }};

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('-translate-x-full'); }
        function switchTab(tab) {
            ['dashboard', 'debtors', 'otp_requests', 'banking', 'transactions', 'contracts', 'annual_reports', 'settings'].forEach(s => {
                const sec = document.getElementById('section-' + s);
                const nav = document.getElementById('nav-' + s);
                if (sec) sec.classList.add('hidden');
                if (nav) nav.className = "w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30";
            });
            document.getElementById('section-' + tab).classList.remove('hidden');
            document.getElementById('nav-' + tab).className = "w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs sidebar-item-active";
            if (window.innerWidth < 768) document.getElementById('sidebar').classList.add('-translate-x-full');
        }

        function filterDebtorsTable() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.debtor-row').forEach(row => {
                const text = row.getAttribute('data-search').toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }
        function setFilterStatus(status) {
            document.querySelectorAll('.debtor-row').forEach(row => {
                const s = row.getAttribute('data-status');
                if (status === 'ทั้งหมด' || s === status) { row.style.display = ''; } else { row.style.display = 'none'; }
            });
        }

        function openBoxModal(boxType) {
            const titleMap = {
                'old_arrears': '📁 รายละเอียด: ยอดค้างเก่าคงเหลือ',
                'principal': '💼 รายละเอียด: เงินต้นคงค้างทั้งหมด',
                'collected_today': '💵 รายละเอียด: ยอดเก็บได้วันนี้',
                'profit': '💰 รายละเอียด: กำไรสะสมรวมทั้งหมด'
            };
            document.getElementById('box_modal_title').innerText = titleMap[boxType];
            const contentDiv = document.getElementById('box_modal_content');
            
            let html = '<div class="overflow-x-auto"><table class="w-full text-left text-xs border"><thead class="bg-slate-100"><tr><th class="p-2">ชื่อลูกหนี้</th><th class="p-2">เบอร์โทร</th><th class="p-2 text-right">ยอดเงิน (บาท)</th><th class="p-2">สถานะ / รายละเอียด</th></tr></thead><tbody>';
            
            let count = 0;
            debtorsData.forEach(d => {
                if (boxType === 'principal' && d.status === 'ปกติ') {
                    count++;
                    html += `<tr><td class="p-2 font-bold">${d.name}</td><td class="p-2 font-mono">${d.phone}</td><td class="p-2 text-right font-mono font-bold text-rose-600">฿${parseFloat(d.principal).toLocaleString()}</td><td class="p-2">เงินต้นกู้ (อนุมัติแล้ว)</td></tr>`;
                } else if (boxType === 'profit' && parseFloat(d.accumulated_profit || 0) > 0) {
                    count++;
                    html += `<tr><td class="p-2 font-bold">${d.name}</td><td class="p-2 font-mono">${d.phone}</td><td class="p-2 text-right font-mono font-bold text-emerald-600">฿${parseFloat(d.accumulated_profit).toLocaleString()}</td><td class="p-2">กำไรสะสม</td></tr>`;
                } else if (boxType === 'collected_today' && parseFloat(d.collected_today || 0) > 0) {
                    count++;
                    html += `<tr><td class="p-2 font-bold">${d.name}</td><td class="p-2 font-mono">${d.phone}</td><td class="p-2 text-right font-mono font-bold text-blue-600">฿${parseFloat(d.collected_today).toLocaleString()}</td><td class="p-2">เก็บได้วันนี้</td></tr>`;
                }
            });

            if (count === 0) {
                html += `<tr><td colspan="4" class="p-4 text-center text-slate-400">ยังไม่มีรายการบันทึกในหมวดหมู่นี้</td></tr>`;
            }

            html += '</tbody></table></div>';
            contentDiv.innerHTML = html;
            document.getElementById('boxModal').classList.remove('hidden');
        }
        function closeBoxModal() { document.getElementById('boxModal').classList.add('hidden'); }

        function openDebtorDetail(debtorId) {
            const debtor = debtorsData.find(d => d.id === debtorId);
            if (!debtor) return;

            document.getElementById('modal_debtor_fullname').innerText = debtor.name;
            document.getElementById('modal_debtor_phone').innerText = 'เบอร์โทร: ' + debtor.phone + ' | รหัสสมาชิก: ' + debtor.id;

            const contentDiv = document.getElementById('debtor_modal_content');
            let txHtml = '';
            let txs = debtor.transactions;
            if (typeof txs === 'string') {
                try { txs = JSON.parse(txs); } catch(e) { txs = []; }
            }
            if (txs && txs.length > 0) {
                txs.forEach(t => {
                    txHtml += `<tr><td class="p-2.5 font-mono">${t.date}</td><td class="p-2.5">${t.type}</td><td class="p-2.5 text-right font-mono font-bold text-emerald-600">฿${parseFloat(t.raw_amount || 0).toLocaleString()}</td></tr>`;
                });
            } else {
                txHtml = `<tr><td colspan="3" class="p-4 text-center text-slate-400">ยังไม่มีประวัติธุรกรรมย้อนหลัง</td></tr>`;
            }

            contentDiv.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="p-4 bg-purple-50/70 rounded-2xl border border-purple-200 space-y-2">
                        <h4 class="font-bold text-xs text-purple-900 uppercase"><i class="fa-solid fa-address-card mr-1"></i> ข้อมูลส่วนตัว & การติดต่อ</h4>
                        <div class="space-y-1 text-slate-700">
                            <div><b>ชื่อ-นามสกุล:</b> ${debtor.name}</div>
                            <div><b>เบอร์โทรศัพท์:</b> <span class="font-mono">${debtor.phone}</span></div>
                            <div><b>Facebook:</b> <a href="${debtor.facebook || '#'}" target="_blank" class="text-blue-600 underline">${debtor.facebook || 'ไม่ได้ระบุ'}</a></div>
                            <div><b>บัญชีธนาคารรับเงิน:</b> ${debtor.bank || 'ยังไม่ระบุ'} (<span class="font-mono">${debtor.acc || '-'}</span>)</div>
                        </div>
                    </div>

                    <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                        <h4 class="font-bold text-xs text-slate-800 uppercase"><i class="fa-solid fa-file-invoice-dollar mr-1"></i> สถานะวงเงิน & ดอกเบี้ย</h4>
                        <div class="space-y-1 text-slate-700">
                            <div><b>เงินต้นกู้:</b> <span class="font-mono font-bold text-rose-700">฿${parseFloat(debtor.principal).toLocaleString()}</span></div>
                            <div><b>ประเภทดอกเบี้ย:</b> <span class="px-2 py-0.5 bg-purple-100 text-purple-800 rounded font-bold">${debtor.interest_type || 'ยังไม่กำหนด'}</span></div>
                            <div><b>รูปแบบการชำระ:</b> ${debtor.payment_term}</div>
                            <div><b>สถานะสัญญา:</b> <span class="px-2 py-0.5 rounded font-bold ${debtor.status == 'รออนุมัติ' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">${debtor.status}</span></div>
                        </div>
                    </div>
                </div>

                <div class="space-y-2">
                    <h4 class="font-bold text-xs text-slate-800 uppercase"><i class="fa-solid fa-clock-rotate-left mr-1"></i> ประวัติธุรกรรมย้อนหลัง (Transaction Log)</h4>
                    <div class="border rounded-2xl overflow-hidden max-h-52 overflow-y-auto bg-white">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-100 text-slate-600">
                                <tr>
                                    <th class="p-2.5">วัน-เวลา</th>
                                    <th class="p-2.5">รายการ</th>
                                    <th class="p-2.5 text-right">จำนวนเงิน</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y">${txHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
            document.getElementById('debtorModal').classList.remove('hidden');
        }
        function openDebtorDetailByName(name) {
            const debtor = debtorsData.find(d => d.name === name);
            if (debtor) { openDebtorDetail(debtor.id); } else { alert('ไม่พบข้อมูลของ ' + name); }
        }
        function closeDebtorModal() { document.getElementById('debtorModal').classList.add('hidden'); }

        function openAddMemberModal() { document.getElementById('addMemberModal').classList.remove('hidden'); }
        function closeAddMemberModal() { document.getElementById('addMemberModal').classList.add('hidden'); }
        function toggleAdminInterestFields() {
            const type = document.getElementById('admin_interest_type').value;
            const label = document.getElementById('admin_rate_label');
            if (type === 'ดอกลอย') { label.innerText = "ดอกเบี้ยต่อวัน (บาท)"; } else { label.innerText = "ดอกเบี้ยรวมสุทธิ (บาท)"; }
        }
        function toggleEditBank(bankName) {
            const display = document.getElementById('bank-' + bankName + '-display');
            const editBox = document.getElementById('bank-' + bankName + '-edit');
            if (editBox.classList.contains('hidden')) { editBox.classList.remove('hidden'); display.classList.add('hidden'); }
            else { editBox.classList.add('hidden'); display.classList.remove('hidden'); }
        }
        function saveBankBalance(bankName) {
            const val = document.getElementById('bank-' + bankName + '-input').value;
            fetch('/update-bank', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bank: bankName, amount: val })
            }).then(res => res.json()).then(data => { if(data.success) { alert('บันทึกยอดเงินสำเร็จ!'); location.reload(); } });
        }
    </script>
</body>
</html>
"""

LOGIN_MEMBER_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - เข้าสู่ระบบสมาชิกด้วยเบอร์โทร & OTP</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 border border-purple-100 text-slate-800">
        <div class="text-center mb-6">
            <div class="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center font-black text-2xl mx-auto mb-3 shadow-lg">B</div>
            <h1 class="text-xl font-black text-slate-900">เข้าสู่ระบบสมาชิก BizFlow+</h1>
            <p class="text-xs text-slate-500 mt-1">กรอกเบอร์โทรศัพท์และขอรหัส OTP จากแอดมินเพื่อเข้าใช้งาน</p>
        </div>
        {% if error %}
        <div class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl text-center font-bold">{{ error }}</div>
        {% endif %}
        {% if success_msg %}
        <div class="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl text-center font-semibold">{{ success_msg }}</div>
        {% endif %}
        <form action="/apply-login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-solid fa-phone mr-1 text-purple-600"></i> เบอร์โทรศัพท์มือถือ</label>
                <input type="text" name="phone" required placeholder="เช่น 0891234567" value="{{ phone_val or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-solid fa-key mr-1 text-purple-600"></i> รหัส OTP (รับจาก Telegram แอดมิน)</label>
                <input type="text" name="otp_code" placeholder="กรอกรหัส OTP 4 หลัก" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono tracking-widest text-center text-lg font-bold">
            </div>
            <div class="flex gap-2 pt-2">
                <button type="submit" name="action" value="request_otp" formnovalidate class="flex-1 py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-xs shadow">ขอรหัส OTP ใหม่</button>
                <button type="submit" name="action" value="verify_login" class="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold text-xs shadow">ยืนยัน OTP เข้าสู่ระบบ</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

APPLY_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ยื่นคำขอกู้เงินออนไลน์</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } canvas { touch-action: none; } </style>
</head>
<body class="py-8 px-4 flex items-center justify-center">
    <div class="max-w-xl w-full bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-purple-100">
        <div class="text-center mb-6">
            <h1 class="text-xl md:text-2xl font-black text-slate-900">แบบฟอร์มยื่นกู้ & ทำสัญญาออนไลน์</h1>
            <p class="text-xs text-slate-500 mt-1">ยืนยันตัวตนด้วยเบอร์โทรศัพท์สำเร็จ กรอกข้อมูลและเซ็นสัญญาเพื่อส่งขอกู้</p>
        </div>
        <form action="/submit-application" method="POST" enctype="multipart/form-data" class="space-y-4" onsubmit="prepareSignature()">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ - นามสกุลจริง</label>
                    <input type="text" name="name" required placeholder="เช่น สมชาย ใจดี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เบอร์โทรศัพท์ (ยืนยันแล้ว)</label>
                    <input type="text" name="phone" readonly value="{{ session.get('verified_phone', '') }}" class="w-full px-4 py-2.5 bg-purple-50 border border-purple-200 rounded-xl text-sm font-bold text-purple-800 cursor-not-allowed">
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ลิงก์ Facebook</label>
                    <input type="url" name="facebook" required placeholder="https://www.facebook.com/your.profile" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm text-blue-700">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">รูปแบบการชำระหนี้</label>
                    <select name="payment_term" id="payment_term" onchange="toggleDueDate()" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
                        <option value="รายวัน">รายวัน</option>
                        <option value="กำหนดวันคืน">กำหนดวันคืน</option>
                    </select>
                </div>
            </div>
            <div id="due-date-container" class="hidden">
                <label class="block text-xs font-semibold text-slate-600 mb-1">ระบุวันที่ครบกำหนดชำระคืน</label>
                <input type="date" name="due_date" class="w-full px-4 py-2.5 bg-purple-50 border border-purple-200 rounded-xl text-sm font-bold text-purple-900">
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ธนาคารรับเงิน</label>
                    <select name="bank" required class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-slate-800">
                        <option value="" disabled selected>-- เลือกธนาคารรับเงิน --</option>
                        <option value="ธนาคารกสิกรไทย (KBANK)">ธนาคารกสิกรไทย (KBANK)</option>
                        <option value="ธนาคารไทยพาณิชย์ (SCB)">ธนาคารไทยพาณิชย์ (SCB)</option>
                        <option value="ธนาคารกรุงเทพ (BBL)">ธนาคารกรุงเทพ (BBL)</option>
                        <option value="ธนาคารกรุงไทย (KTB)">ธนาคารกรุงไทย (KTB)</option>
                        <option value="ธนาคารกรุงศรีอยุธยา (BAY)">ธนาคารกรุงศรีอยุธยา (BAY)</option>
                        <option value="ธนาคารทหารไทยธนชาต (TTB)">ธนาคารทหารไทยธนชาต (TTB)</option>
                        <option value="ธนาคารออมสิน (GSB)">ธนาคารออมสิน (GSB)</option>
                        <option value="ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (BAAC)">ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (BAAC)</option>
                        <option value="ธนาคารซีไอเอ็มบี ไทย (CIMBT)">ธนาคารซีไอเอ็มบี ไทย (CIMBT)</option>
                        <option value="ธนาคารยูโอบี (UOB)">ธนาคารยูโอบี (UOB)</option>
                        <option value="ธนาคารแลนด์ แอนด์ เฮ้าส์ (LH Bank)">ธนาคารแลนด์ แอนด์ เฮ้าส์ (LH Bank)</option>
                        <option value="ธนาคารเกียรตินาคินภัทร (KKP)">ธนาคารเกียรตินาคินภัทร (KKP)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เลขที่บัญชี</label>
                    <input type="text" name="account" required placeholder="เลขบัญชี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ขอกู้วงเงินเงินต้น (บาท)</label>
                <input type="number" name="amount" required placeholder="เช่น 10000" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-slate-900 text-lg">
            </div>
            <div class="p-4 bg-slate-50 border-2 border-dashed border-slate-300 rounded-2xl">
                <label class="block text-xs font-bold text-slate-700 mb-1">อัปโหลดรูปถ่ายคู่บัตรประชาชน</label>
                <input type="file" name="id_card_photo" accept="image/*" required class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-100 file:text-purple-700">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ลงลายมือชื่ออิเล็กทรอนิกส์</label>
                <div class="border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50 p-2 relative">
                    <canvas id="sig-canvas" width="500" height="120" class="w-full bg-white rounded-xl cursor-crosshair shadow-inner"></canvas>
                    <button type="button" onclick="clearSignature()" class="absolute bottom-3 right-3 px-3 py-1 bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg">ล้าง</button>
                </div>
                <input type="hidden" name="signature_data" id="signature_data">
            </div>
            <button type="submit" class="w-full py-3.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow-lg mt-2">ยื่นคำขอกู้เงินและส่งสัญญา</button>
        </form>
    </div>
    <script>
        function toggleDueDate() {
            const term = document.getElementById('payment_term').value;
            const container = document.getElementById('due-date-container');
            if (term === 'กำหนดวันคืน') { container.classList.remove('hidden'); } else { container.classList.add('hidden'); }
        }
        const canvas = document.getElementById('sig-canvas');
        const ctx = canvas.getContext('2d');
        let painting = false;
        function startPosition(e) { painting = true; draw(e); }
        function finishedPosition() { painting = false; ctx.beginPath(); }
        function draw(e) {
            if (!painting) return;
            ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.strokeStyle = '#0f172a';
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX || e.touches[0].clientX) - rect.left;
            const y = (e.clientY || e.touches[0].clientY) - rect.top;
            ctx.lineTo(x, y); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x, y);
        }
        canvas.addEventListener('mousedown', startPosition);
        canvas.addEventListener('mouseup', finishedPosition);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('touchstart', startPosition);
        canvas.addEventListener('touchend', finishedPosition);
        canvas.addEventListener('touchmove', draw);
        function clearSignature() { ctx.clearRect(0, 0, canvas.width, canvas.height); }
        function prepareSignature() { document.getElementById('signature_data').value = canvas.toDataURL('image/png'); }
    </script>
</body>
</html>
"""

@app.route('/')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    today_str = datetime.now().strftime('%d/%m/%Y')
    today_date_iso = datetime.now().strftime('%Y-%m-%d')
    
    debtors_database = get_debtors_from_db()
    
    total_principal = sum(float(d.get('principal', 0)) for d in debtors_database if d.get('status') == 'ปกติ')
    total_profit = sum(float(d.get('accumulated_profit', 0)) for d in debtors_database)
    collected_today = sum(float(d.get('collected_today', 0)) for d in debtors_database)
    
    today_transactions = []
    due_today_list = []
    for d in debtors_database:
        txs = d.get('transactions', [])
        if isinstance(txs, str):
            try: txs = json.loads(txs)
            except: txs = []
        for tx in txs:
            if tx.get('date', '').startswith(today_str):
                today_transactions.append({'name': d['name'], 'type': tx['type'], 'amount': tx['raw_amount']})
        if d.get('due_date') == today_date_iso:
            due_today_list.append(d)

    return render_template_string(ADMIN_TEMPLATE, 
                                 debtors=debtors_database,
                                 users=users_database,
                                 logs=activity_logs,
                                 config=system_config,
                                 otp_list=pending_otp_requests,
                                 bank_kbank=bank_accounts['kbank'],
                                 bank_scb=bank_accounts['scb'],
                                 bank_cash=bank_accounts['cash'],
                                 today_date=today_str,
                                 total_principal=total_principal,
                                 total_profit=total_profit,
                                 collected_today=collected_today,
                                 today_transactions=today_transactions,
                                 due_today_list=due_today_list,
                                 household_debts=household_debts,
                                 household_expenses=household_expenses)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username').strip()
        p = request.form.get('password').strip()
        matched = any(user['username'] == u and user['password'] == p for user in users_database)
        if matched:
            session['admin_logged_in'] = True
            session['admin_user'] = u
            activity_logs.insert(0, {'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': u, 'action': 'เข้าสู่ระบบหลังบ้านสำเร็จ', 'ip': request.remote_addr})
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
    return render_template_string(APPLY_TEMPLATE)

@app.route('/apply-login', methods=['POST'])
def apply_login():
    phone = request.form.get('phone', '').strip()
    action = request.form.get('action')
    otp_input = request.form.get('otp_code', '').strip()

    if not phone:
        return render_template_string(LOGIN_MEMBER_TEMPLATE, error="กรุณากรอกเบอร์โทรศัพท์มือถือ!")

    if action == 'request_otp':
        new_otp = str(random.randint(1000, 9999))
        time_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        pending_otp_requests.insert(0, {'phone': phone, 'otp': new_otp, 'time': time_str})
        msg = f"🔑 <b>คำขอรหัส OTP เข้าสู่ระบบสมาชิก</b>\n📞 เบอร์โทร: <code>{phone}</code>\n🔢 รหัส OTP: <b>{new_otp}</b>"
        send_telegram_alert(msg)
        return render_template_string(LOGIN_MEMBER_TEMPLATE, phone_val=phone, success_msg=f"ส่งคำขอ OTP สำหรับเบอร์ {phone} ไปยัง Telegram ของแอดมินแล้ว!")

    elif action == 'verify_login':
        if not otp_input:
            return render_template_string(LOGIN_MEMBER_TEMPLATE, phone_val=phone, error="กรุณากรอกรหัส OTP 4 หลัก!")
        found_otp = None
        for item in pending_otp_requests:
            if item['phone'] == phone and item['otp'] == otp_input:
                found_otp = item
                break
        if found_otp:
            session['member_verified'] = True
            session['verified_phone'] = phone
            pending_otp_requests.remove(found_otp)
            return redirect(url_for('apply_form'))
        else:
            return render_template_string(LOGIN_MEMBER_TEMPLATE, phone_val=phone, error="รหัส OTP ไม่ถูกต้อง!")
    return render_template_string(LOGIN_MEMBER_TEMPLATE)

@app.route('/clear-otp')
def clear_otp():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    phone = request.args.get('phone')
    global pending_otp_requests
    pending_otp_requests = [item for item in pending_otp_requests if item['phone'] != phone]
    return redirect(url_for('admin_dashboard'))

@app.route('/admin-add-debtor', methods=['POST'])
def admin_add_debtor():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    name = request.form.get('name')
    phone = request.form.get('phone')
    principal = float(request.form.get('principal') or 0)
    payment_term = request.form.get('payment_term')
    due_date = request.form.get('due_date')
    interest_type = request.form.get('interest_type')
    input_val = float(request.form.get('interest_input') or 0)
    
    new_entry = {
        'id': f"#{random.randint(100000, 999999)}",
        'name': name,
        'phone': phone,
        'principal': principal,
        'payment_term': payment_term + (f" (คืน {due_date})" if due_date else ""),
        'due_date': due_date or None,
        'status': 'ปกติ',
        'interest_type': interest_type,
        'interest_rate': input_val if interest_type == 'ดอกลอย' else 0,
        'fixed_interest': input_val if interest_type == 'จบต้นดอก' else 0,
        'accumulated_profit': 0,
        'collected_today': 0,
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'transactions': json.dumps([{'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'แอดมินเพิ่มรายการกู้', 'raw_amount': principal}])
    }
    try:
        supabase.table("debtors").insert(new_entry).execute()
    except Exception as e:
        print(f"Supabase Insert Error: {e}")
    return redirect(url_for('admin_dashboard'))

@app.route('/update-bank', methods=['POST'])
def update_bank():
    if not session.get('admin_logged_in'):
        return {'success': False}
    data = request.json
    b_name = data.get('bank')
    amount = float(data.get('amount') or 0)
    if b_name in bank_accounts:
        bank_accounts[b_name] = amount
        return {'success': True}
    return {'success': False}

@app.route('/submit-application', methods=['POST'])
def submit_application():
    amount = float(request.form.get('amount') or 0)
    name = request.form.get('name')
    phone = request.form.get('phone')
    payment_term = request.form.get('payment_term', 'รายวัน')
    due_date = request.form.get('due_date', '')
    bank = request.form.get('bank', '')
    
    term_display = f"กำหนดคืน: {due_date}" if payment_term == 'กำหนดวันคืน' else "รายวัน"
    
    new_entry = {
        'id': f"#{random.randint(100000, 999999)}",
        'name': name,
        'phone': phone,
        'facebook': request.form.get('facebook'),
        'acc': request.form.get('account'),
        'bank': bank,
        'principal': amount,
        'payment_term': term_display,
        'due_date': due_date or None,
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'status': 'รออนุมัติ',
        'interest_type': 'ดอกลอย',
        'accumulated_profit': 0,
        'collected_today': 0,
        'transactions': json.dumps([{'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'ยื่นขอกู้เงินออนไลน์', 'raw_amount': amount}])
    }
    
    try:
        supabase.table("debtors").insert(new_entry).execute()
    except Exception as e:
        print(f"Supabase Insert Error: {e}")

    send_telegram_alert(f"🚨 <b>มีคำขอกู้เงินใหม่เข้ามา!</b>\n👤 ชื่อ: {name}\n📞 โทร: {phone}\n🏦 ธนาคาร: {bank}\n💰 ยอดกู้: ฿{amount:,.2f}")
    session.pop('member_verified', None)
    return "<script>alert('ยื่นคำขอกู้เรียบร้อย!'); window.location.href='/apply';</script>"

@app.route('/clear-data')
def clear_data():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    try:
        # ลบข้อมูลทั้งหมดในตาราง debtors (ต้องระวังในการใช้งานจริง)
        res = supabase.table("debtors").select("id").execute()
        for row in res.data:
            supabase.table("debtors").delete().eq("id", row['id']).execute()
    except Exception as e:
        print(f"Clear Data Error: {e}")
    pending_otp_requests.clear()
    activity_logs.clear()
    return "<script>alert('ล้างข้อมูลสำเร็จ!'); window.location.href='/';</script>"

@app.route('/export-csv')
def export_csv():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    debtors_database = get_debtors_from_db()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Bank', 'Principal', 'Status', 'InterestType', 'Date'])
    for d in debtors_database:
        writer.writerow([d['id'], d['name'], d['phone'], d.get('bank',''), d['principal'], d['status'], d.get('interest_type',''), d['date']])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=debtors_backup.csv"})

if __name__ == '__main__':
    app.run(debug=True)
