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
        return response.data if response.data else []
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
        return []

pending_otp_requests = []

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

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการลูกหนี้ & บัญชีการเงิน</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #f8fafc; }
        .sidebar-item-active { background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(126, 34, 206, 0.2) 100%); border: 1px solid rgba(192, 132, 252, 0.4); color: #f3e8ff; }
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
            <div class="p-6 border-b border-purple-900/40 flex items-center justify-between">
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
                            <i class="fa-solid fa-users text-sm text-amber-400 w-5"></i><span>รายชื่อลูกหนี้ & หน้าประวัติ</span>
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
                    <p class="text-[11px] font-bold text-purple-400/80 uppercase px-3 mb-1">📄 3. รายงาน & ตั้งค่า</p>
                    <div class="space-y-1">
                        <button onclick="switchTab('annual_reports')" id="nav-annual_reports" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30">
                            <i class="fa-solid fa-chart-line text-sm text-teal-400 w-5"></i><span>รายงานผลประกอบการประจำปี</span>
                        </button>
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
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                    <div onclick="openBoxModal('old_arrears')" class="p-5 rounded-2xl bg-amber-500 text-white shadow-lg cursor-pointer hover:opacity-90 transition">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-amber-100 uppercase">📁 ยอดค้างเก่าคงเหลือ</span>
                            <i class="fa-solid fa-folder-open text-amber-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black">฿0.00</h3>
                        <p class="text-[10px] text-amber-100 mt-1 underline">คลิกดูประวัติ</p>
                    </div>

                    <div onclick="openBoxModal('principal')" class="p-5 rounded-2xl bg-rose-700 text-white shadow-lg cursor-pointer hover:opacity-90 transition">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-rose-200 uppercase">💼 เงินต้นคงค้าง</span>
                            <i class="fa-solid fa-briefcase text-rose-300 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black">฿{{ total_principal | format_num }}</h3>
                        <p class="text-[10px] text-rose-200 mt-1 underline">คลิกดูประวัติ</p>
                    </div>

                    <div onclick="openBoxModal('collected_today')" class="p-5 rounded-2xl bg-blue-600 text-white shadow-lg cursor-pointer hover:opacity-90 transition">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-blue-200 uppercase">💵 ยอดเก็บได้วันนี้</span>
                            <i class="fa-solid fa-hand-holding-dollar text-blue-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black">฿{{ collected_today | format_num }}</h3>
                        <p class="text-[10px] text-blue-200 mt-1 underline">คลิกดูประวัติ</p>
                    </div>

                    <div onclick="openBoxModal('profit')" class="p-5 rounded-2xl bg-emerald-600 text-white shadow-lg cursor-pointer hover:opacity-90 transition">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-emerald-200 uppercase">💰 กำไรสะสมรวม</span>
                            <i class="fa-solid fa-sack-dollar text-emerald-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black">฿{{ total_profit | format_num }}</h3>
                        <p class="text-[10px] text-emerald-200 mt-1 underline">คลิกดูประวัติ</p>
                    </div>
                </div>

                <!-- ตารางความเคลื่อนไหวล่างแดชบอร์ด -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-3xl border shadow-sm space-y-4">
                        <div class="flex items-center justify-between">
                            <h3 class="font-bold text-slate-800 text-sm">👥 รายชื่อลูกหนี้ที่ใช้งานอยู่ในระบบ</h3>
                            <button onclick="switchTab('debtors')" class="text-xs text-purple-600 font-bold hover:underline">ดูทั้งหมด</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-xl overflow-hidden">
                                <thead class="bg-slate-50 text-slate-500">
                                    <tr><th class="p-2.5">ชื่อ-เบอร์โทร</th><th class="p-2.5 text-right">เงินต้นกู้</th><th class="p-2.5 text-center">จัดการ</th></tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% set active_debtors = debtors | selectattr('status', 'equalto', 'ปกติ') | list %}
                                    {% for d in active_debtors[:5] %}
                                    <tr>
                                        <td class="p-2.5">
                                            <div class="font-bold text-slate-800">{{ d.name }}</div>
                                            <div class="text-[10px] text-slate-400 font-mono">{{ d.phone }}</div>
                                        </td>
                                        <td class="p-2.5 text-right font-mono font-bold text-rose-600">฿{{ d.principal | format_num }}</td>
                                        <td class="p-2.5 text-center">
                                            <button onclick="openDebtorDetailByPhone('{{ d.phone }}')" class="px-2.5 py-1 bg-purple-100 text-purple-800 rounded-lg font-bold">ดูประวัติ</button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="p-4 text-center text-slate-400">ยังไม่มีลูกหนี้ที่อนุมัติแล้ว</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="bg-white p-6 rounded-3xl border shadow-sm space-y-4">
                        <div class="flex items-center justify-between">
                            <h3 class="font-bold text-slate-800 text-sm">⌛ คำขอกู้ใหม่ที่รออนุมัติ</h3>
                            <span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-xs">{{ pending_count }} รายการ</span>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-xl overflow-hidden">
                                <thead class="bg-slate-50 text-slate-500">
                                    <tr><th class="p-2.5">ชื่อ-เบอร์โทร</th><th class="p-2.5 text-right">วงเงินที่ขอกู้</th><th class="p-2.5 text-center">จัดการ</th></tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% set pending_debtors = debtors | selectattr('status', 'equalto', 'รออนุมัติ') | list %}
                                    {% for d in pending_debtors %}
                                    <tr>
                                        <td class="p-2.5">
                                            <div class="font-bold text-slate-800">{{ d.name }}</div>
                                            <div class="text-[10px] text-slate-400 font-mono">{{ d.phone }}</div>
                                        </td>
                                        <td class="p-2.5 text-right font-mono font-bold text-purple-700">฿{{ d.principal | format_num }}</td>
                                        <td class="p-2.5 text-center">
                                            <button onclick="openDebtorDetailByPhone('{{ d.phone }}')" class="px-2.5 py-1 bg-amber-500 text-white rounded-lg font-bold">พิจารณาอนุมัติ</button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="p-4 text-center text-slate-400">ไม่มีคำขอกู้ที่รออนุมัติในขณะนี้</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: บัญชีธนาคาร & พื้นที่ส่วนตัว -->
            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">กสิกรไทย (KBANK)</h4>
                            <button onclick="toggleEditBank('kbank')" class="text-xs bg-emerald-700 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-kbank-display" class="text-3xl font-black">฿{{ bank_kbank | format_num }}</div>
                        <div id="bank-kbank-edit" class="hidden space-y-2">
                            <input type="number" id="bank-kbank-input" value="{{ bank_kbank }}" onkeydown="if(event.key==='Enter') saveBankBalance('kbank')" class="w-full px-3 py-2 bg-emerald-700 text-white rounded-xl font-bold">
                            <button onclick="saveBankBalance('kbank')" class="w-full py-1.5 bg-white text-emerald-800 rounded-lg text-xs font-bold">บันทึก</button>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-purple-700 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">ไทยพาณิชย์ (SCB)</h4>
                            <button onclick="toggleEditBank('scb')" class="text-xs bg-purple-800 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-scb-display" class="text-3xl font-black">฿{{ bank_scb | format_num }}</div>
                        <div id="bank-scb-edit" class="hidden space-y-2">
                            <input type="number" id="bank-scb-input" value="{{ bank_scb }}" onkeydown="if(event.key==='Enter') saveBankBalance('scb')" class="w-full px-3 py-2 bg-purple-800 text-white rounded-xl font-bold">
                            <button onclick="saveBankBalance('scb')" class="w-full py-1.5 bg-white text-purple-900 rounded-lg text-xs font-bold">บันทึก</button>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-slate-800 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">เงินสด (Cash)</h4>
                            <button onclick="toggleEditBank('cash')" class="text-xs bg-slate-700 px-2.5 py-1 rounded-lg">แก้ไขยอด</button>
                        </div>
                        <div id="bank-cash-display" class="text-3xl font-black">฿{{ bank_cash | format_num }}</div>
                        <div id="bank-cash-edit" class="hidden space-y-2">
                            <input type="number" id="bank-cash-input" value="{{ bank_cash }}" onkeydown="if(event.key==='Enter') saveBankBalance('cash')" class="w-full px-3 py-2 bg-slate-700 text-white rounded-xl font-bold">
                            <button onclick="saveBankBalance('cash')" class="w-full py-1.5 bg-white text-slate-900 rounded-lg text-xs font-bold">บันทึก</button>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-3xl border border-purple-200 p-6 md:p-8 shadow-xl space-y-6">
                    <div class="flex flex-wrap items-center justify-between border-b pb-4 gap-4">
                        <div>
                            <h3 class="text-xl font-black text-purple-900">พื้นที่ส่วนตัว: บริหารการเงินครัวเรือน & หนี้สินประจำ</h3>
                            <p class="text-xs text-slate-500 mt-1">จัดการรายรับรายจ่าย, หักค่างวดคำนวณเงินคงเหลือแท้จริง และสะสมทรัพย์สิน</p>
                        </div>
                        <div class="flex items-center gap-3 bg-purple-50 p-3 rounded-2xl border">
                            <div>
                                <span class="text-[10px] font-bold text-purple-700 block uppercase">รายรับเดือนนี้</span>
                                <span id="income-display" class="font-black text-purple-900 text-sm">฿{{ personal_finance.monthly_income | format_num }}</span>
                            </div>
                            <button onclick="toggleEditIncome()" class="px-2.5 py-1 bg-purple-600 text-white rounded-xl text-xs font-bold">แก้ไขรายรับ</button>
                        </div>
                    </div>

                    <div id="income-edit-box" class="hidden p-4 bg-purple-100 rounded-2xl flex items-center gap-3">
                        <input type="number" id="income-input" value="{{ personal_finance.monthly_income }}" onkeydown="if(event.key==='Enter') saveMonthlyIncome()" class="px-3 py-2 bg-white border rounded-xl text-sm font-black w-48">
                        <button onclick="saveMonthlyIncome()" class="px-4 py-2 bg-purple-600 text-white rounded-xl text-xs font-bold">บันทึกรายรับใหม่</button>
                    </div>

                    <!-- หลอดสรุปรายจ่าย vs รายรับคงเหลือจริง -->
                    <div class="p-6 bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-3xl space-y-4 shadow-xl">
                        <div class="flex flex-wrap items-center justify-between gap-4">
                            <div>
                                <span class="text-xs font-bold text-purple-300 uppercase tracking-wider">📊 หลอดสรุปการใช้จ่ายประจำเดือน (หักค่างวดและค่าใช้จ่ายแล้ว)</span>
                                <div class="text-2xl font-black text-white mt-1">
                                    ใช้จ่ายแล้ว: <span id="spent-val" class="text-rose-400">฿0.00</span> / <span class="text-slate-300">รายรับ ฿{{ personal_finance.monthly_income | format_num }}</span>
                                </div>
                            </div>
                            <div class="text-right bg-white/10 px-4 py-2 rounded-2xl border border-white/10">
                                <span class="text-[10px] font-bold text-emerald-300 block uppercase">💰 รายรับคงเหลือจริงเดือนนี้</span>
                                <span id="net-remaining-val" class="font-black text-emerald-400 text-xl">฿{{ personal_finance.monthly_income | format_num }}</span>
                            </div>
                        </div>

                        <!-- Progress Bar รายจ่าย -->
                        <div class="w-full bg-slate-800 rounded-full h-4 overflow-hidden p-0.5 border border-slate-700">
                            <div id="income-spent-bar" class="bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500 h-3 rounded-full transition-all duration-500" style="width: 0%;"></div>
                        </div>
                        <div class="flex justify-between text-[11px] font-semibold text-slate-400">
                            <span id="spent-percent-text">ใช้ไป 0% ของรายรับ</span>
                            <span id="remaining-percent-text">คงเหลือ 100%</span>
                        </div>
                    </div>

                    <!-- พอร์ตสะสมทรัพย์สิน -->
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-sm text-slate-800">🏆 พอร์ตสะสมทรัพย์สิน & การออมแยกประเภท (พิมพ์แล้วกด Enter เพื่อบันทึก)</h4>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-2">
                                <label class="text-xs font-bold text-emerald-800 uppercase block"><i class="fa-solid fa-money-bill-wave mr-1"></i> เงินสด / เงินฝาก (บาท)</label>
                                <input type="number" id="savings-cash-input" value="{{ personal_finance.savings_cash }}" onchange="saveSavingsPortfolio()" onkeydown="if(event.key==='Enter') { this.blur(); alert('บันทึกยอดเงินสดเรียบร้อย!'); }" class="w-full px-3 py-2 bg-white border border-emerald-300 rounded-xl font-mono font-bold text-emerald-900 text-lg">
                            </div>
                            <div class="p-4 rounded-2xl bg-amber-50 border border-amber-200 space-y-2">
                                <label class="text-xs font-bold text-amber-800 uppercase block"><i class="fa-solid fa-coins mr-1"></i> ทองคำสะสม (บาท)</label>
                                <input type="number" id="savings-gold-input" value="{{ personal_finance.savings_gold }}" onchange="saveSavingsPortfolio()" onkeydown="if(event.key==='Enter') { this.blur(); alert('บันทึกยอดทองคำเรียบร้อย!'); }" class="w-full px-3 py-2 bg-white border border-amber-300 rounded-xl font-mono font-bold text-amber-900 text-lg">
                            </div>
                            <div class="p-4 rounded-2xl bg-blue-50 border border-blue-200 space-y-2">
                                <label class="text-xs font-bold text-blue-800 uppercase block"><i class="fa-solid fa-chart-line mr-1"></i> หุ้น / กองทุน (บาท)</label>
                                <input type="number" id="savings-stocks-input" value="{{ personal_finance.savings_stocks }}" onchange="saveSavingsPortfolio()" onkeydown="if(event.key==='Enter') { this.blur(); alert('บันทึกยอดหุ้น/กองทุนเรียบร้อย!'); }" class="w-full px-3 py-2 bg-white border border-blue-300 rounded-xl font-mono font-bold text-blue-900 text-lg">
                            </div>
                        </div>
                    </div>

                    <!-- ค่าใช้จ่ายจิปาถะรายวัน -->
                    <div class="p-5 bg-slate-50 border rounded-3xl space-y-3">
                        <label class="text-xs font-bold text-slate-700 uppercase block">🛍️ ค่าใช้จ่ายจิปาถะ (บันทึกรายวัน - กด Enter เพื่อเพิ่มรายการ)</label>
                        <div class="flex gap-2">
                            <input type="text" id="misc-desc-input" placeholder="รายการ (เช่น ซื้อของใช้, ค่ากาแฟ)" onkeydown="if(event.key==='Enter') document.getElementById('misc-amt-input').focus();" class="flex-1 px-3.5 py-2.5 bg-white border rounded-xl text-xs font-semibold">
                            <input type="number" id="misc-amt-input" placeholder="จำนวนเงิน" onkeydown="if(event.key==='Enter') addDailyMisc();" class="w-32 px-3.5 py-2.5 bg-white border rounded-xl text-xs font-bold font-mono">
                            <button onclick="addDailyMisc()" class="px-4 py-2.5 bg-purple-600 text-white rounded-xl text-xs font-bold shadow">+ เพิ่มรายการ</button>
                        </div>
                        <div class="max-h-40 overflow-y-auto border rounded-xl bg-white">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-600 sticky top-0">
                                    <tr><th class="p-2.5">วันที่/เวลา</th><th class="p-2.5">รายการ</th><th class="p-2.5 text-right">จำนวน</th><th class="p-2.5 text-center">ลบ</th></tr>
                                </thead>
                                <tbody id="misc-table-body" class="divide-y">
                                    <tr><td colspan="4" class="p-3 text-center text-slate-400">ยังไม่มีรายการจิปาถะวันนี้</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- แผนภูมิวงกลม -->
                    <div class="p-6 bg-white border rounded-3xl shadow-sm space-y-4 max-w-lg mx-auto">
                        <h4 class="font-bold text-sm text-slate-800 text-center">📊 แผนภูมิวงกลมสรุปค่าใช้จ่ายประจำ</h4>
                        <div class="relative h-64 flex justify-center items-center">
                            <canvas id="expensePieChart"></canvas>
                        </div>
                    </div>

                    <!-- หนี้สินครัวเรือน -->
                    <div class="space-y-3">
                        <h4 class="font-bold text-sm text-slate-800">รายการหนี้ครัวเรือน (กดชำระ/ตัดยอดรายงวดได้)</h4>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-2xl overflow-hidden">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr><th class="p-3">รายการหนี้</th><th class="p-3 text-right">ยอดคงเหลือ (บาท)</th><th class="p-3">รายละเอียด</th><th class="p-3 text-center">ชำระงวด</th></tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% for debt in household_debts %}
                                    <tr id="debt-row-{{ debt.id }}">
                                        <td class="p-3 font-bold text-slate-900">{{ debt.name }}</td>
                                        <td class="p-3 text-right font-mono font-bold text-rose-600 text-sm" id="debt-amount-{{ debt.id }}">฿{{ debt.outstanding | format_num }}</td>
                                        <td class="p-3 text-slate-600">{{ debt.detail }}</td>
                                        <td class="p-3 text-center">
                                            <button onclick="openPayDebtModal('{{ debt.id }}', '{{ debt.name }}', {{ debt.outstanding }})" class="px-3 py-1.5 bg-rose-600 text-white rounded-xl font-bold text-xs shadow">จ่ายชำระ</button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- รายการค่าใช้จ่ายประจำต่อเดือน -->
                    <div class="space-y-3 pt-4">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-sm text-slate-800">รายการค่าใช้จ่ายประจำต่อเดือน (พิมพ์แล้วกด Enter เพื่อบันทึกทันที)</h4>
                            <button onclick="resetMonthlyExpenses()" class="px-3 py-1.5 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold">รีเซ็ตสถานะจ่ายทุกเดือน</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs border rounded-2xl overflow-hidden">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr><th class="p-3">รายการ</th><th class="p-3 text-right">จำนวนเงินจ่ายรอบนี้ (บาท)</th><th class="p-3">งวดคงเหลือ / หมายเหตุ</th><th class="p-3 text-center">สถานะจ่ายรอบนี้</th></tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% for exp in household_expenses %}
                                    <tr id="expense-tr-{{ exp.id }}">
                                        <td class="p-3 font-bold text-slate-800">{{ exp.name }}</td>
                                        <td class="p-3 text-right">
                                            {% if exp.is_variable %}
                                                <input type="number" id="exp-amt-{{ exp.id }}" value="{{ exp.amount }}" onchange="updateCalculations()" onkeydown="if(event.key==='Enter') { this.blur(); updateCalculations(); alert('บันทึกยอด {{ exp.name }} เรียบร้อย!'); }" class="w-28 px-2 py-1 bg-purple-50 border border-purple-300 rounded-lg font-mono font-bold text-purple-900 text-right">
                                            {% else %}
                                                <span class="font-mono font-bold text-blue-600" id="exp-amt-display-{{ exp.id }}">฿{{ exp.amount | format_num }}</span>
                                                <input type="hidden" id="exp-amt-{{ exp.id }}" value="{{ exp.amount }}">
                                            {% endif %}
                                        </td>
                                        <td class="p-3 text-slate-600 font-bold">
                                            {% if exp.has_installments %}
                                                <div class="flex items-center gap-1">
                                                    <span>เหลือ</span>
                                                    <input type="number" id="exp-inst-input-{{ exp.id }}" value="{{ exp.installments }}" onchange="updateInstallmentValue('{{ exp.id }}')" onkeydown="if(event.key==='Enter') { this.blur(); updateInstallmentValue('{{ exp.id }}'); alert('บันทึกงวดคงเหลือเรียบร้อย!'); }" class="w-16 px-2 py-0.5 bg-slate-50 border rounded font-mono font-bold text-slate-800 text-center">
                                                    <span>งวด</span>
                                                </div>
                                            {% else %}
                                                <span>{{ exp.note }}</span>
                                            {% endif %}
                                        </td>
                                        <td class="p-3 text-center">
                                            <button onclick="toggleExpenseStatus('{{ exp.id }}', this)" class="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold text-[11px] expense-status-btn" data-exp-id="{{ exp.id }}">{{ exp.status }}</button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: จัดการลูกหนี้ & หน้าประวัติ -->
            <div id="section-debtors" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-4 md:p-6 shadow-sm overflow-x-auto">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div class="flex items-center gap-2">
                            <button onclick="setFilterStatus('ทั้งหมด')" id="filter-all" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white">ทั้งหมด</button>
                            <button onclick="setFilterStatus('รออนุมัติ')" id="filter-pending" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-amber-50 text-amber-800 border">รออนุมัติ</button>
                            <button onclick="setFilterStatus('ปกติ')" id="filter-approved" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-600">อนุมัติแล้ว</button>
                        </div>
                        <input type="text" id="searchInput" oninput="filterDebtorsTable()" placeholder="🔍 ค้นหาสมาชิก..." class="px-4 py-2 bg-slate-50 border rounded-xl text-xs w-72">
                    </div>

                    <table class="w-full text-left text-sm min-w-[750px]">
                        <thead class="bg-slate-50 text-slate-500">
                            <tr><th class="p-3.5">ชื่อ-เบอร์โทร</th><th class="p-3.5">จำนวนบิลกู้</th><th class="p-3.5 text-right">ยอดเงินต้นรวม</th><th class="p-3.5 text-center">สถานะ</th><th class="p-3.5 text-center">จัดการหน้าประวัติ</th></tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y">
                            {% set unique_phones = [] %}
                            {% for d in debtors %}
                                {% if d.phone not in unique_phones %}
                                    {% set _ = unique_phones.append(d.phone) %}
                                    {% set client_bills = debtors | selectattr('phone', 'equalto', d.phone) | list %}
                                    {% set total_p = client_bills | sum(attribute='principal') %}
                                    {% set has_pending = client_bills | selectattr('status', 'equalto', 'รออนุมัติ') | list | length > 0 %}
                            <tr class="debtor-row" data-status="{% if has_pending %}รออนุมัติ{% else %}ปกติ{% endif %}" data-search="{{ d.name }} {{ d.phone }}">
                                <td class="p-3.5">
                                    <div class="font-bold text-purple-900 cursor-pointer hover:underline text-base" onclick="openDebtorDetailByPhone('{{ d.phone }}')">{{ d.name }}</div>
                                    <div class="text-xs text-slate-500 font-mono">{{ d.phone }}</div>
                                </td>
                                <td class="p-3.5 font-bold text-blue-700">{{ client_bills | length }} บิล</td>
                                <td class="p-3.5 text-right font-mono font-bold text-rose-600">฿{{ total_p | format_num }}</td>
                                <td class="p-3.5 text-center">
                                    <span class="px-2.5 py-1 rounded-full text-xs font-bold {% if has_pending %}bg-amber-100 text-amber-800{% else %}bg-emerald-100 text-emerald-800{% endif %}">
                                        {% if has_pending %}รออนุมัติบิลใหม่{% else %}ปกติ{% endif %}
                                    </span>
                                </td>
                                <td class="p-3.5 text-center">
                                    <button onclick="openDebtorDetailByPhone('{{ d.phone }}')" class="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow">
                                        <i class="fa-solid fa-address-book mr-1"></i> เปิดหน้าประวัติลูกค้า
                                    </button>
                                </td>
                            </tr>
                                {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab: OTP -->
            <div id="section-otp_requests" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800">🔑 คำขอรหัส OTP จากสมาชิกหน้าเว็บ</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs bg-white rounded-xl border">
                            <thead class="bg-slate-100 text-slate-600"><tr><th class="p-3">เบอร์โทร</th><th class="p-3">เวลา</th><th class="p-3 text-center">OTP</th><th class="p-3 text-right">จัดการ</th></tr></thead>
                            <tbody class="divide-y">
                                {% if otp_list %}
                                    {% for item in otp_list %}
                                    <tr>
                                        <td class="p-3 font-mono font-bold">{{ item.phone }}</td>
                                        <td class="p-3 text-slate-500">{{ item.time }}</td>
                                        <td class="p-3 text-center"><span class="px-3 py-1 bg-rose-100 text-rose-800 rounded font-mono font-black">{{ item.otp }}</span></td>
                                        <td class="p-3 text-right"><a href="/clear-otp?phone={{ item.phone }}" class="px-3 py-1.5 bg-slate-200 rounded font-bold">ลบ</a></td>
                                    </tr>
                                    {% endfor %}
                                {% else %}
                                    <tr><td colspan="4" class="p-4 text-center text-slate-400">ไม่มีคำขอ OTP ในขณะนี้</td></tr>
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="section-annual_reports" class="hidden space-y-6"><div class="bg-white rounded-2xl p-6 shadow-sm">รายงานประจำปี</div></div>
            <div id="section-settings" class="hidden space-y-6">
                <div class="bg-white rounded-2xl p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold border-b pb-3">⚙️ ตั้งค่า</h3>
                    <div class="flex gap-2">
                        <a href="/export-csv" class="py-2.5 px-4 bg-purple-600 text-white rounded-xl text-xs font-bold shadow">Export CSV</a>
                        <button onclick="if(confirm('รีเซ็ตข้อมูลทั้งหมด?')) { window.location.href='/clear-data'; }" class="py-2.5 px-4 bg-rose-600 text-white rounded-xl text-xs font-bold shadow">รีเซ็ตข้อมูล</button>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- Modal: หน้าประวัติลูกค้า (รวมทุกบิล, ชำระหนี้, และอัลบั้มสัญญา/ลายเซ็น) -->
    <div id="debtorModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-4xl w-full p-6 md:p-8 shadow-2xl border space-y-6 max-h-[95vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b pb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold text-lg"><i class="fa-solid fa-user-shield"></i></div>
                    <div>
                        <h3 class="text-lg font-black text-purple-900" id="modal_client_name">ชื่อลูกค้า</h3>
                        <p class="text-xs text-slate-500 font-mono" id="modal_client_phone">เบอร์โทร</p>
                    </div>
                </div>
                <button onclick="closeDebtorModal()" class="text-slate-400 hover:text-slate-600 font-bold text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div id="debtor_modal_content" class="space-y-6 text-xs text-slate-700"></div>

            <div class="border-t pt-4 flex items-center justify-between">
                <div id="modal_action_buttons" class="flex gap-2"></div>
                <button onclick="closeDebtorModal()" class="px-5 py-2.5 bg-slate-800 text-white rounded-xl font-bold text-xs">ปิดหน้าต่าง</button>
            </div>
        </div>
    </div>

    <!-- Modal: บันทึกการชำระหนี้รายบิล -->
    <div id="payDebtModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-60 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 class="text-lg font-black text-slate-900" id="pay_debt_title">บันทึกรับชำระหนี้</h3>
            <div class="space-y-3 text-xs">
                <input type="hidden" id="pay_debt_id">
                <div>
                    <label class="block font-semibold mb-1">ยอดเงินรับชำระ (บาท)</label>
                    <input type="number" id="pay_debt_amount" onkeydown="if(event.key==='Enter') submitPayDebt()" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold text-emerald-700" placeholder="0.00">
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="button" onclick="closePayDebtModal()" class="flex-1 py-2 bg-slate-200 rounded-xl font-bold">ยกเลิก</button>
                    <button type="button" onclick="submitPayDebt()" class="flex-1 py-2 bg-emerald-600 text-white rounded-xl font-bold shadow">บันทึกรับเงิน</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: แก้ไขวงเงินและดอกเบี้ย -->
    <div id="editDebtorModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-60 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 class="text-lg font-black text-slate-900 border-b pb-2">✏️ แก้ไขวงเงินและดอกเบี้ย</h3>
            <form action="/update-debtor-specs" method="POST" class="space-y-3 text-xs">
                <input type="hidden" name="debtor_id" id="edit_debtor_id">
                <div>
                    <label class="block font-semibold mb-1">เงินต้น / วงเงินกู้ (บาท)</label>
                    <input type="number" name="principal" id="edit_principal" required class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                </div>
                <div>
                    <label class="block font-semibold mb-1">ประเภทดอกเบี้ย</label>
                    <select name="interest_type" id="edit_interest_type" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                        <option value="ดอกลอย">ดอกลอย</option>
                        <option value="จบต้นดอก">จบต้นดอก</option>
                    </select>
                </div>
                <div>
                    <label class="block font-semibold mb-1">ดอกเบี้ยต่อวัน (บาท)</label>
                    <input type="number" step="any" name="interest_rate" id="edit_interest_rate" required class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="button" onclick="closeEditDebtorModal()" class="flex-1 py-2 bg-slate-200 rounded-xl font-bold">ยกเลิก</button>
                    <button type="submit" class="flex-1 py-2 bg-amber-600 text-white rounded-xl font-bold shadow">บันทึกการแก้ไข</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: ข้อมูลในกล่อง Dashboard -->
    <div id="boxModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 id="box_modal_title" class="text-lg font-black text-slate-900">รายละเอียด</h3>
            <div id="box_modal_content" class="space-y-3 text-xs"></div>
            <div class="text-right"><button onclick="closeBoxModal()" class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold text-xs">ปิด</button></div>
        </div>
    </div>

    <script>
        const debtorsData = {{ debtors | tojson }};
        let householdDebts = {{ household_debts | tojson }};
        let householdExpenses = {{ household_expenses | tojson }};
        let personalFinance = {{ personal_finance | tojson }};
        let dailyMiscExpenses = [];
        let expenseChart = null;

        function saveSavingsPortfolio() {
            personalFinance.savings_cash = parseFloat(document.getElementById('savings-cash-input').value) || 0;
            personalFinance.savings_gold = parseFloat(document.getElementById('savings-gold-input').value) || 0;
            personalFinance.savings_stocks = parseFloat(document.getElementById('savings-stocks-input').value) || 0;
        }

        function updateInstallmentValue(expId) {
            const exp = householdExpenses.find(e => e.id === expId);
            const input = document.getElementById('exp-inst-input-' + expId);
            if (exp && input) { exp.installments = parseInt(input.value) || 0; }
        }

        function addDailyMisc() {
            const descInput = document.getElementById('misc-desc-input');
            const amtInput = document.getElementById('misc-amt-input');
            const desc = descInput.value.trim();
            const amt = parseFloat(amtInput.value) || 0;
            if (!desc || amt <= 0) { alert('กรุณากรอกรายการและจำนวนเงินที่ถูกต้อง'); return; }
            const timeStr = new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
            dailyMiscExpenses.push({ id: Date.now(), time: timeStr, desc: desc, amt: amt });
            descInput.value = ''; amtInput.value = ''; descInput.focus();
            renderMiscTable(); updateCalculations();
        }

        function removeMiscItem(id) {
            dailyMiscExpenses = dailyMiscExpenses.filter(item => item.id !== id);
            renderMiscTable(); updateCalculations();
        }

        function renderMiscTable() {
            const tbody = document.getElementById('misc-table-body');
            if (dailyMiscExpenses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="p-3 text-center text-slate-400">ยังไม่มีรายการจิปาถะวันนี้</td></tr>';
                return;
            }
            let html = '';
            dailyMiscExpenses.forEach(item => {
                html += `<tr><td class="p-2 font-mono text-slate-500">${item.time}</td><td class="p-2 font-semibold text-slate-800">${item.desc}</td><td class="p-2 text-right font-mono font-bold text-rose-600">฿${item.amt.toLocaleString('en-US', {minimumFractionDigits: 2})}</td><td class="p-2 text-center"><button onclick="removeMiscItem(${item.id})" class="text-rose-500 hover:text-rose-700 font-bold"><i class="fa-solid fa-trash"></i></button></td></tr>`;
            });
            tbody.innerHTML = html;
        }

        function updateCalculations() {
            let paidExpensesSum = 0;
            householdExpenses.forEach(exp => {
                const btn = document.querySelector(`.expense-status-btn[data-exp-id="${exp.id}"]`);
                if (btn && btn.innerText === 'จ่ายแล้ว') {
                    const amtInput = document.getElementById('exp-amt-' + exp.id);
                    paidExpensesSum += amtInput ? (parseFloat(amtInput.value) || 0) : exp.amount;
                }
            });
            const miscTotal = dailyMiscExpenses.reduce((sum, item) => sum + item.amt, 0);
            const totalSpent = paidExpensesSum + miscTotal;
            const income = personalFinance.monthly_income || 1;
            const remaining = income - totalSpent;

            document.getElementById('spent-val').innerText = '฿' + totalSpent.toLocaleString('en-US', {minimumFractionDigits: 2});
            document.getElementById('net-remaining-val').innerText = '฿' + remaining.toLocaleString('en-US', {minimumFractionDigits: 2});

            let spentPercent = (totalSpent / income) * 100;
            let barWidth = spentPercent > 100 ? 100 : spentPercent;
            const bar = document.getElementById('income-spent-bar');
            bar.style.width = barWidth + '%';
            bar.className = spentPercent > 100 ? "bg-rose-600 h-3 rounded-full transition-all duration-500" : "bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500 h-3 rounded-full transition-all duration-500";
            document.getElementById('spent-percent-text').innerText = 'ใช้ไป ' + spentPercent.toFixed(1) + '% ของรายรับ';
            document.getElementById('remaining-percent-text').innerText = 'คงเหลือ ' + ((remaining / income) * 100).toFixed(1) + '%';
            updatePieChart(paidExpensesSum, miscTotal);
        }

        function updatePieChart(paidExpenses, misc) {
            const ctx = document.getElementById('expensePieChart').getContext('2d');
            if (expenseChart) expenseChart.destroy();
            expenseChart = new Chart(ctx, {
                type: 'pie',
                data: { labels: ['ค่างวด/หนี้/ค่าห้อง/ค่าเน็ต', 'ค่าใช้จ่ายจิปาถะ'], datasets: [{ data: [paidExpenses, misc], backgroundColor: ['#8b5cf6', '#f59e0b'] }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        window.addEventListener('load', updateCalculations);

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('-translate-x-full'); }
        function switchTab(tab) {
            ['dashboard', 'debtors', 'otp_requests', 'banking', 'annual_reports', 'settings'].forEach(s => {
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
                row.style.display = row.getAttribute('data-search').toLowerCase().includes(query) ? '' : 'none';
            });
        }
        function setFilterStatus(status) {
            document.querySelectorAll('.debtor-row').forEach(row => {
                row.style.display = (status === 'ทั้งหมด' || row.getAttribute('data-status') === status) ? '' : 'none';
            });
        }

        function toggleEditIncome() { document.getElementById('income-edit-box').classList.toggle('hidden'); }
        function saveMonthlyIncome() {
            const val = parseFloat(document.getElementById('income-input').value) || 0;
            personalFinance.monthly_income = val;
            document.getElementById('income-display').innerText = '฿' + val.toLocaleString('en-US', {minimumFractionDigits: 2});
            toggleEditIncome(); updateCalculations(); alert('บันทึกรายรับใหม่สำเร็จ!');
        }

        function openPayDebtModal(id, name, outstanding) {
            document.getElementById('pay_debt_id').value = id;
            document.getElementById('pay_debt_title').innerText = 'ชำระหนี้: ' + name + ' (คงเหลือ ฿' + outstanding.toLocaleString() + ')';
            document.getElementById('pay_debt_amount').value = '';
            document.getElementById('payDebtModal').classList.remove('hidden');
        }
        function closePayDebtModal() { document.getElementById('payDebtModal').classList.add('hidden'); }
        function submitPayDebt() {
            const id = document.getElementById('pay_debt_id').value;
            const payAmt = parseFloat(document.getElementById('pay_debt_amount').value) || 0;
            const debt = householdDebts.find(d => d.id === id);
            if (debt && payAmt > 0) {
                debt.outstanding = Math.max(0, debt.outstanding - payAmt);
                document.getElementById('debt-amount-' + id).innerText = '฿' + debt.outstanding.toLocaleString('en-US', {minimumFractionDigits: 2});
                closePayDebtModal(); alert('บันทึกการชำระหนี้เรียบร้อย!');
            }
        }

        function toggleExpenseStatus(expId, btn) {
            const exp = householdExpenses.find(e => e.id === expId);
            if (!exp) return;
            if (btn.innerText === 'รอจ่าย') {
                btn.innerText = 'จ่ายแล้ว';
                btn.className = "px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-lg font-bold text-[11px] expense-status-btn";
                if (exp.has_installments && exp.installments > 0) {
                    exp.installments = Math.max(0, exp.installments - 1);
                    const instInput = document.getElementById('exp-inst-input-' + expId);
                    if (instInput) instInput.value = exp.installments;
                }
            } else {
                btn.innerText = 'รอจ่าย';
                btn.className = "px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold text-[11px] expense-status-btn";
                if (exp.has_installments) {
                    exp.installments += 1;
                    const instInput = document.getElementById('exp-inst-input-' + expId);
                    if (instInput) instInput.value = exp.installments;
                }
            }
            updateCalculations();
        }

        function resetMonthlyExpenses() {
            document.querySelectorAll('.expense-status-btn').forEach(btn => {
                btn.innerText = 'รอจ่าย';
                btn.className = "px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold text-[11px] expense-status-btn";
            });
            updateCalculations(); alert('รีเซ็ตสถานะค่าใช้จ่ายประจำเดือนเรียบร้อย!');
        }

        function openBoxModal(boxType) {
            const titleMap = { 'old_arrears': '📁 รายละเอียด: ยอดค้างเก่าคงเหลือ', 'principal': '💼 รายละเอียด: เงินต้นคงค้างทั้งหมด', 'collected_today': '💵 รายละเอียด: ยอดเก็บได้วันนี้', 'profit': '💰 รายละเอียด: กำไรสะสมรวมทั้งหมด' };
            document.getElementById('box_modal_title').innerText = titleMap[boxType];
            const contentDiv = document.getElementById('box_modal_content');
            let html = '<div class="overflow-x-auto"><table class="w-full text-left text-xs border"><thead class="bg-slate-100"><tr><th class="p-2">ชื่อลูกหนี้</th><th class="p-2">เบอร์โทร</th><th class="p-2 text-right">ยอดเงิน</th><th class="p-2">สถานะ</th></tr></thead><tbody>';
            let count = 0;
            debtorsData.forEach(d => {
                if (boxType === 'principal' && d.status === 'ปกติ') {
                    count++;
                    html += `<tr><td class="p-2 font-bold">${d.name}</td><td class="p-2 font-mono">${d.phone}</td><td class="p-2 text-right font-mono font-bold text-rose-600">฿${parseFloat(d.principal).toLocaleString()}</td><td class="p-2">อนุมัติแล้ว</td></tr>`;
                }
            });
            if (count === 0) html += `<tr><td colspan="4" class="p-4 text-center text-slate-400">ยังไม่มีรายการ</td></tr>`;
            html += '</tbody></table></div>';
            contentDiv.innerHTML = html;
            document.getElementById('boxModal').classList.remove('hidden');
        }
        function closeBoxModal() { document.getElementById('boxModal').classList.add('hidden'); }

        // ฟังก์ชันเปิดหน้าประวัติลูกค้า (รวมทุกบิล, รับชำระ, และอัลบั้มสัญญา/ลายเซ็น)
        function openDebtorDetailByPhone(phone) {
            const clientBills = debtorsData.filter(d => d.phone === phone);
            if (clientBills.length === 0) return;
            const primary = clientBills[0];

            document.getElementById('modal_client_name').innerText = primary.name || 'ไม่ระบุชื่อ';
            document.getElementById('modal_client_phone').innerText = 'เบอร์โทร: ' + primary.phone + ' | บิลทั้งหมดในระบบ: ' + clientBills.length + ' บิล';

            let billsHtml = '';
            let galleryHtml = '';

            clientBills.forEach((b, index) => {
                let txs = b.transactions;
                if (typeof txs === 'string') { try { txs = JSON.parse(txs); } catch(e) { txs = []; } }
                
                let txHtml = '';
                if (txs && txs.length > 0) {
                    txs.forEach(t => {
                        txHtml += `<tr><td class="p-2 font-mono">${t.date || '-'}</td><td class="p-2">${t.type || '-'}</td><td class="p-2 text-right font-mono font-bold text-emerald-600">฿${parseFloat(t.raw_amount || 0).toLocaleString()}</td></tr>`;
                    });
                } else {
                    txHtml = `<tr><td colspan="3" class="p-3 text-center text-slate-400">ยังไม่มีประวัติธุรกรรม</td></tr>`;
                }

                billsHtml += `
                    <div class="p-4 bg-slate-50 border rounded-2xl space-y-3">
                        <div class="flex items-center justify-between border-b pb-2">
                            <div>
                                <span class="font-bold text-purple-900 text-sm">บิลที่ #${index + 1} (รหัส: ${b.id})</span>
                                <span class="ml-2 px-2 py-0.5 rounded text-[10px] font-bold ${b.status == 'รออนุมัติ' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">${b.status}</span>
                            </div>
                            <div class="flex gap-2">
                                ${b.status == 'รออนุมัติ' ? `<a href="/approve-debtor?debtor_id=${encodeURIComponent(b.id)}" class="px-3 py-1 bg-emerald-600 text-white rounded-lg font-bold text-xs">อนุมัติบิลนี้</a>` : ''}
                                <button onclick="openEditDebtor('${b.id}', ${b.principal || 0}, '${b.interest_type || 'ดอกลอย'}', ${b.interest_rate || 100})" class="px-3 py-1 bg-amber-600 text-white rounded-lg font-bold text-xs">แก้ไขวงเงิน/ดอกเบี้ย</button>
                                <button onclick="openPayDebtModalForItem('${b.id}', '${b.name}', ${b.principal || 0})" class="px-3 py-1 bg-purple-600 text-white rounded-lg font-bold text-xs"><i class="fa-solid fa-money-bill-wave mr-1"></i> รับชำระหนี้</button>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <div><b>เงินต้นกู้:</b> <span class="font-mono font-bold text-rose-700">฿${parseFloat(b.principal || 0).toLocaleString()}</span></div>
                                <div><b>ประเภทดอกเบี้ย:</b> ${b.interest_type || 'ดอกลอย'} (<span class="font-mono text-purple-700 font-bold">฿${b.interest_rate || 100}/วัน</span>)</div>
                                <div><b>ธนาคารรับเงิน:</b> ${b.bank || '-'} (<span class="font-mono">${b.acc || '-'}</span>)</div>
                                <div><b>วันที่ยื่นกู้:</b> ${b.date || '-'}</div>
                            </div>
                            <div>
                                <b>ประวัติธุรกรรม & การชำระหนี้:</b>
                                <div class="border rounded-xl bg-white max-h-28 overflow-y-auto mt-1">
                                    <table class="w-full text-left text-[11px]"><thead class="bg-slate-100"><tr><th class="p-1.5">เวลา</th><th class="p-1.5">รายการ</th><th class="p-1.5 text-right">จำนวน</th></tr></thead><tbody class="divide-y">${txHtml}</tbody></table>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // รวบรวมรูปลายเซ็น / บัตรประชาชนเข้าสู่อัลบั้มสัญญา
                if (b.signature_data) {
                    galleryHtml += `
                        <div class="p-3 bg-white border rounded-2xl shadow-sm space-y-1 text-center">
                            <span class="font-bold text-[11px] text-purple-900 block">ลายเซ็นสัญญา (บิล #${index + 1})</span>
                            <img src="${b.signature_data}" class="max-h-24 mx-auto border rounded bg-slate-50 p-1">
                        </div>
                    `;
                }
            });

            const contentDiv = document.getElementById('debtor_modal_content');
            contentDiv.innerHTML = `
                <div class="space-y-4">
                    <div class="p-4 bg-purple-50 rounded-2xl border flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <div><b>ชื่อ-นามสกุล:</b> ${primary.name}</div>
                            <div><b>เบอร์โทร:</b> <span class="font-mono font-bold">${primary.phone}</span></div>
                            <div><b>Facebook:</b> <a href="${primary.facebook || '#'}" target="_blank" class="text-blue-600 underline">${primary.facebook || 'ไม่มี'}</a></div>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-purple-700 block font-bold">📂 อัลบั้มสัญญา & ลายเซ็นดิจิทัลรวมทุกบิล</span>
                        </div>
                    </div>

                    <!-- อัลบั้มรูปสัญญา / ลายเซ็น -->
                    <div class="space-y-2">
                        <h4 class="font-bold text-xs text-slate-800 uppercase"><i class="fa-solid fa-images mr-1"></i> อัลบั้มสัญญาและลายเซ็นอิเล็กทรอนิกส์</h4>
                        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                            ${galleryHtml || '<p class="text-slate-400 text-xs col-span-full">ยังไม่มีรูปลายเซ็นในระบบ</p>'}
                        </div>
                    </div>

                    <!-- รายการบิลเงินกู้ทั้งหมด -->
                    <div class="space-y-3">
                        <h4 class="font-bold text-xs text-slate-800 uppercase"><i class="fa-solid fa-file-invoice-dollar mr-1"></i> ประวัติบิลเงินกู้ทั้งหมดของลูกค้าท่านนี้</h4>
                        <div class="space-y-3 max-h-96 overflow-y-auto pr-1">
                            ${billsHtml}
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('modal_action_buttons').innerHTML = ``;
            document.getElementById('debtorModal').classList.remove('hidden');
        }

        function closeDebtorModal() { document.getElementById('debtorModal').classList.add('hidden'); }

        function openPayDebtModalForItem(id, name, principal) {
            document.getElementById('pay_debt_id').value = id;
            document.getElementById('pay_debt_title').innerText = 'บันทึกรับชำระหนี้: ' + name + ' (บิลรหัส ' + id + ')';
            document.getElementById('pay_debt_amount').value = '';
            document.getElementById('payDebtModal').classList.remove('hidden');
        }

        function submitPayDebt() {
            const id = document.getElementById('pay_debt_id').value;
            const amt = parseFloat(document.getElementById('pay_debt_amount').value) || 0;
            if (amt <= 0) { alert('กรุณากรอกจำนวนเงินรับชำระที่ถูกต้อง'); return; }
            fetch('/submit-payment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ debtor_id: id, amount: amt })
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    alert('บันทึกรับชำระหนี้สำเร็จ!');
                    location.reload();
                } else {
                    alert('เกิดข้อผิดพลาดในการบันทึก');
                }
            });
        }

        function openEditDebtor(id, principal, interest_type, interest_rate) {
            document.getElementById('edit_debtor_id').value = id;
            document.getElementById('edit_principal').value = principal;
            document.getElementById('edit_interest_type').value = interest_type;
            document.getElementById('edit_interest_rate').value = interest_rate;
            document.getElementById('editDebtorModal').classList.remove('hidden');
        }
        function closeEditDebtorModal() { document.getElementById('editDebtorModal').classList.add('hidden'); }

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
    <title>BizFlow+ - เข้าสู่ระบบสมาชิก</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 border text-slate-800">
        <div class="text-center mb-6">
            <h1 class="text-xl font-black text-slate-900">เข้าสู่ระบบสมาชิก BizFlow+</h1>
            <p class="text-xs text-slate-500 mt-1">กรอกเบอร์โทรและขอรหัส OTP จากแอดมิน</p>
        </div>
        {% if error %}<div class="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-xl text-center font-bold">{{ error }}</div>{% endif %}
        {% if success_msg %}<div class="mb-4 p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl text-center font-semibold">{{ success_msg }}</div>{% endif %}
        <form action="/apply-login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">เบอร์โทรศัพท์มือถือ</label>
                <input type="text" name="phone" required placeholder="0891234567" value="{{ phone_val or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">รหัส OTP (4 หลัก)</label>
                <input type="text" name="otp_code" placeholder="xxxx" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono tracking-widest text-center text-lg font-bold">
            </div>
            <div class="flex gap-2 pt-2">
                <button type="submit" name="action" value="request_otp" formnovalidate class="flex-1 py-3 bg-slate-800 text-white rounded-xl font-bold text-xs shadow">ขอรหัส OTP</button>
                <button type="submit" name="action" value="verify_login" class="flex-1 py-3 bg-purple-600 text-white rounded-xl font-bold text-xs shadow">ยืนยัน OTP</button>
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
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } canvas { touch-action: none; } </style>
</head>
<body class="py-8 px-4 flex items-center justify-center">
    <div class="max-w-xl w-full bg-white rounded-3xl shadow-2xl p-6 md:p-8 border">
        <div class="text-center mb-6">
            <h1 class="text-xl font-black text-slate-900">แบบฟอร์มยื่นกู้ & ทำสัญญาออนไลน์</h1>
            {% if is_old_member %}
                <span class="inline-block mt-2 px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">✨ ตรวจพบสมาชิกเก่า (ระบบจดจำข้อมูลแล้ว ไม่ต้องแนบรูปบัตรซ้ำ)</span>
            {% else %}
                <span class="inline-block mt-2 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-bold">📝 สมาชิกใหม่ (กรุณาแนบรูปคู่บัตรประชาชน)</span>
            {% endif %}
        </div>
        <form action="/submit-application" method="POST" enctype="multipart/form-data" class="space-y-4" onsubmit="prepareSignature()">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ - นามสกุลจริง</label>
                <input type="text" name="name" required placeholder="สมชาย ใจดี" value="{{ default_name or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">เบอร์โทรศัพท์ (ยืนยันแล้ว)</label>
                <input type="text" name="phone" readonly value="{{ session.get('verified_phone', '') }}" class="w-full px-4 py-2.5 bg-purple-50 border rounded-xl text-sm font-bold text-purple-800 cursor-not-allowed">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ลิงก์ Facebook</label>
                <input type="url" name="facebook" required placeholder="https://www.facebook.com/..." value="{{ default_facebook or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ธนาคารรับเงิน</label>
                    <select name="bank" required class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold">
                        <option value="ธนาคารกสิกรไทย (KBANK)">กสิกรไทย (KBANK)</option>
                        <option value="ธนาคารไทยพาณิชย์ (SCB)">ไทยพาณิชย์ (SCB)</option>
                        <option value="ธนาคารกรุงเทพ (BBL)">กรุงเทพ (BBL)</option>
                        <option value="ธนาคารกรุงไทย (KTB)">กรุงไทย (KTB)</option>
                        <option value="ธนาคารทหารไทยธนชาต (TTB)">ทหารไทยธนชาต (TTB)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เลขที่บัญชี</label>
                    <input type="text" name="account" required placeholder="เลขบัญชี" value="{{ default_acc or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ขอกู้วงเงินเงินต้น (บาท)</label>
                <input type="number" name="amount" required placeholder="10000" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-lg">
            </div>

            {% if not is_old_member %}
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">แนบรูปถ่ายคู่บัตรประชาชน (เฉพาะสมาชิกใหม่)</label>
                <input type="file" name="id_card_image" accept="image/*" required class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-xs">
            </div>
            {% endif %}

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ลงลายมือชื่ออิเล็กทรอนิกส์</label>
                <div class="border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50 p-2 relative">
                    <canvas id="sig-canvas" width="500" height="120" class="w-full bg-white rounded-xl cursor-crosshair"></canvas>
                    <button type="button" onclick="clearSignature()" class="absolute bottom-3 right-3 px-3 py-1 bg-slate-200 text-xs font-semibold rounded-lg">ล้าง</button>
                </div>
                <input type="hidden" name="signature_data" id="signature_data">
            </div>
            <button type="submit" class="w-full py-3.5 bg-purple-600 text-white rounded-xl font-bold shadow-lg mt-2">ยื่นคำขอกู้เงินและส่งสัญญา</button>
        </form>
    </div>
    <script>
        const canvas = document.getElementById('sig-canvas');
        const ctx = canvas.getContext('2d');
        let painting = false;
        canvas.addEventListener('mousedown', () => painting = true);
        canvas.addEventListener('mouseup', () => { painting = false; ctx.beginPath(); });
        canvas.addEventListener('mousemove', (e) => {
            if (!painting) return;
            ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.strokeStyle = '#0f172a';
            const rect = canvas.getBoundingClientRect();
            ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top); ctx.stroke(); ctx.beginPath(); ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
        });
        function clearSignature() { ctx.clearRect(0, 0, canvas.width, canvas.height); }
        function prepareSignature() { document.getElementById('signature_data').value = canvas.toDataURL('image/png'); }
    </script>
</body>
</html>
"""

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - เข้าสู่ระบบแอดมิน</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 border text-slate-800">
        <div class="text-center mb-6">
            <h1 class="text-xl font-black text-slate-900">เข้าสู่ระบบหลังบ้าน BizFlow+</h1>
            <p class="text-xs text-slate-500 mt-1">กรุณากรอก Username และ Password</p>
        </div>
        {% if error %}<div class="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-xl text-center font-bold">{{ error }}</div>{% endif %}
        <form action="/admin-login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อผู้ใช้งาน (Username)</label>
                <input type="text" name="username" required class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสผ่าน (Password)</label>
                <input type="password" name="password" required class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold">
            </div>
            <button type="submit" class="w-full py-3 bg-purple-600 text-white rounded-xl font-bold text-xs shadow mt-2">เข้าสู่ระบบแอดมิน</button>
        </form>
    </div>
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
    try:
        res = supabase.table("debtors").select("*").eq('id', debtor_id).execute()
        if res.data:
            debtor = res.data[0]
            txs = debtor.get('transactions', [])
            if isinstance(txs, str):
                try: txs = json.loads(txs)
                except: txs = []
            txs.append({'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'รับชำระหนี้', 'raw_amount': amount})
            
            new_profit = float(debtor.get('accumulated_profit', 0)) + amount
            supabase.table("debtors").update({
                'transactions': json.dumps(txs),
                'accumulated_profit': new_profit,
                'collected_today': float(debtor.get('collected_today', 0)) + amount
            }).eq('id', debtor_id).execute()
            return {'success': True}
    except Exception as e:
        print(f"Payment Error: {e}")
    return {'success': False}

@app.route('/submit-application', methods=['POST'])
def submit_application():
    amount = float(request.form.get('amount') or 0)
    name = request.form.get('name')
    phone = request.form.get('phone')
    bank = request.form.get('bank', '')
    signature_data = request.form.get('signature_data', '')

    new_entry = {
        'id': f"#{random.randint(100000, 999999)}",
        'name': name,
        'phone': phone,
        'facebook': request.form.get('facebook'),
        'acc': request.form.get('account'),
        'bank': bank,
        'principal': amount,
        'payment_term': 'รายวัน',
        'status': 'รออนุมัติ',
        'interest_type': 'ดอกลอย',
        'interest_rate': 100,
        'accumulated_profit': 0,
        'collected_today': 0,
        'signature_data': signature_data,
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'transactions': json.dumps([{'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'ยื่นขอกู้เงินออนไลน์', 'raw_amount': amount}])
    }
    try:
        supabase.table("debtors").insert(new_entry).execute()
    except Exception as e:
        print(f"Insert Error: {e}")
    send_telegram_alert(f"🚨 <b>มีคำขอกู้เงินใหม่!</b>\n👤 ชื่อ: {name}\n📞 เบอร์: {phone}\n💰 ยอด: ฿{amount:,.2f}")
    session.pop('member_verified', None)
    return "<script>alert('ยื่นคำขอกู้เรียบร้อย!'); window.location.href='/apply';</script>"

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
