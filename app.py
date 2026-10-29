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
    'savings_cash': 15000,
    'savings_gold': 20000,
    'savings_stocks': 12000,
    'food_expense': 4500,
    'misc_expense': 2000
}

household_debts = [
    {'id': 'd1', 'name': 'Line BK', 'outstanding': 9200, 'detail': 'ดอกเบี้ย 20%, ปิดจบเดือนที่ 1'},
    {'id': 'd2', 'name': 'สินเชื่อ ttb', 'outstanding': 125441, 'detail': 'ดอกเบี้ย 19%, ปิดจบเดือนที่ 2-5'},
    {'id': 'd3', 'name': 'หนี้ทองคำ 4 บาท', 'outstanding': 240000, 'detail': 'ดอกเบี้ย 15%, ไถ่ถอนเดือนที่ 6-12'}
]

household_expenses = [
    {'id': 'e1', 'name': 'งดรถยนต์', 'amount': 13588, 'installments': 59, 'note': 'เหลือ 59 งวด', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e2', 'name': 'งดมอเตอร์ไซค์ 1', 'amount': 3396, 'installments': 10, 'note': 'เหลือ 10 งวด', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e3', 'name': 'งดมอเตอร์ไซค์ 2', 'amount': 2122, 'installments': 21, 'note': 'เหลือ 21 งวด', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e4', 'name': 'ประกันรถยนต์ 1', 'amount': 1540, 'installments': 0, 'note': 'ผ่อน 10 เดือน/ปี', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e5', 'name': 'ประกันรถยนต์ 2', 'amount': 1860, 'installments': 2, 'note': 'เหลืออีก 2 เดือนจบ', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e6', 'name': 'ค่าห้องพัก', 'amount': 7000, 'installments': 0, 'note': 'ยอดผันแปรตามหน่วยไฟ/น้ำ', 'status': 'รอจ่าย', 'is_variable': True},
    {'id': 'e7', 'name': 'แชร์วง 5 หมื่น', 'amount': 3000, 'installments': 3, 'note': 'เหลือ 3 งวด (จ่ายทุก 15)', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e8', 'name': 'แชร์วง 9 หมื่น', 'amount': 5000, 'installments': 17, 'note': 'เหลือ 17 งวด (จ่ายทุก 27)', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e9', 'name': 'ประกันชีวิต', 'amount': 2100, 'installments': 0, 'note': 'จ่ายประจำเดือน', 'status': 'รอจ่าย', 'is_variable': False},
    {'id': 'e10', 'name': 'ค่าเน็ต', 'amount': 1500, 'installments': 0, 'note': 'ยอดผันแปรตามการใช้งาน/ส่วนลด', 'status': 'รอจ่าย', 'is_variable': True}
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
                                            <button onclick="openDebtorDetail('{{ d.id }}')" class="px-2.5 py-1 bg-purple-100 text-purple-800 rounded-lg font-bold">ดูรายละเอียด</button>
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
                                            <button onclick="openDebtorDetail('{{ d.id }}')" class="px-2.5 py-1 bg-amber-500 text-white rounded-lg font-bold">พิจารณาอนุมัติ</button>
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
                            <input type="number" id="bank-kbank-input" value="{{ bank_kbank }}" class="w-full px-3 py-2 bg-emerald-700 text-white rounded-xl font-bold">
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
                            <input type="number" id="bank-scb-input" value="{{ bank_scb }}" class="w-full px-3 py-2 bg-purple-800 text-white rounded-xl font-bold">
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
                            <input type="number" id="bank-cash-input" value="{{ bank_cash }}" class="w-full px-3 py-2 bg-slate-700 text-white rounded-xl font-bold">
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
                        <input type="number" id="income-input" value="{{ personal_finance.monthly_income }}" class="px-3 py-2 bg-white border rounded-xl text-sm font-black w-48">
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

                    <!-- ช่องแยกกระเป๋าสะสมการออม (เงินสด / ทองคำ / หุ้น) -->
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-sm text-slate-800">🏆 พอร์ตสะสมทรัพย์สิน & การออมแยกประเภท</h4>
                            <button onclick="openSavingsModal()" class="px-3 py-1.5 bg-emerald-600 text-white rounded-xl text-xs font-bold shadow">+ บันทึกการออมเพิ่ม</button>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-1">
                                <span class="text-xs font-bold text-emerald-800 uppercase"><i class="fa-solid fa-money-bill-wave mr-1"></i> เงินสด / เงินฝาก</span>
                                <div class="text-xl font-black text-emerald-900" id="savings-cash-val">฿{{ personal_finance.savings_cash | format_num }}</div>
                            </div>
                            <div class="p-4 rounded-2xl bg-amber-50 border border-amber-200 space-y-1">
                                <span class="text-xs font-bold text-amber-800 uppercase"><i class="fa-solid fa-coins mr-1"></i> ทองคำสะสม</span>
                                <div class="text-xl font-black text-amber-900" id="savings-gold-val">฿{{ personal_finance.savings_gold | format_num }}</div>
                            </div>
                            <div class="p-4 rounded-2xl bg-blue-50 border border-blue-200 space-y-1">
                                <span class="text-xs font-bold text-blue-800 uppercase"><i class="fa-solid fa-chart-line mr-1"></i> หุ้น / กองทุน</span>
                                <div class="text-xl font-black text-blue-900" id="savings-stocks-val">฿{{ personal_finance.savings_stocks | format_num }}</div>
                            </div>
                        </div>
                    </div>

                    <!-- ค่าใช้จ่ายผันแปรประจำวัน: ค่ากิน & จิปาถะ -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-5 bg-slate-50 border rounded-3xl">
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-slate-700 uppercase">🍲 ค่ากินประจำเดือน (บาท)</label>
                            <input type="number" id="expense-food" value="{{ personal_finance.food_expense }}" onchange="updateCalculations()" class="w-full px-3 py-2 bg-white border rounded-xl text-sm font-bold text-slate-800">
                        </div>
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-slate-700 uppercase">🛍️ ค่าใช้จ่ายจิปาถะ (บาท)</label>
                            <input type="number" id="expense-misc" value="{{ personal_finance.misc_expense }}" onchange="updateCalculations()" class="w-full px-3 py-2 bg-white border rounded-xl text-sm font-bold text-slate-800">
                        </div>
                    </div>

                    <!-- แผนภูมิวงกลมสรุปค่าใช้จ่าย -->
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
                            <h4 class="font-bold text-sm text-slate-800">รายการค่าใช้จ่ายประจำต่อเดือน (กรอกยอดที่ชำระจริงของแต่ละเดือนได้)</h4>
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
                                                <input type="number" id="exp-amt-{{ exp.id }}" value="{{ exp.amount }}" onchange="updateCalculations()" class="w-28 px-2 py-1 bg-purple-50 border border-purple-300 rounded-lg font-mono font-bold text-purple-900 text-right">
                                            {% else %}
                                                <span class="font-mono font-bold text-blue-600" id="exp-amt-display-{{ exp.id }}">฿{{ exp.amount | format_num }}</span>
                                                <input type="hidden" id="exp-amt-{{ exp.id }}" value="{{ exp.amount }}">
                                            {% endif %}
                                        </td>
                                        <td class="p-3 text-slate-600 font-bold" id="exp-inst-{{ exp.id }}">
                                            {% if exp.installments > 0 %}เหลือ {{ exp.installments }} งวด{% else %}{{ exp.note }}{% endif %}
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

            <!-- Tab: จัดการลูกหนี้ & คำขอกู้ -->
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
                            <tr><th class="p-3.5">ชื่อ-เบอร์โทร</th><th class="p-3.5">ดอกเบี้ย</th><th class="p-3.5">เงินต้นกู้</th><th class="p-3.5">รูปแบบ</th><th class="p-3.5">สถานะ</th><th class="p-3.5 text-center">จัดการ</th></tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y">
                            {% for d in debtors %}
                            <tr class="debtor-row" data-status="{{ d.status }}" data-search="{{ d.name }} {{ d.phone }}">
                                <td class="p-3.5">
                                    <div class="font-bold text-purple-900 cursor-pointer hover:underline text-base" onclick="openDebtorDetail('{{ d.id }}')">{{ d.name }}</div>
                                    <div class="text-xs text-slate-500 font-mono">{{ d.phone }}</div>
                                </td>
                                <td class="p-3.5"><span class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-bold">{{ d.interest_type or 'ดอกลอย' }}</span></td>
                                <td class="p-3.5 font-mono font-bold">฿{{ d.principal | format_num }}</td>
                                <td class="p-3.5 text-xs font-semibold">{{ d.payment_term }}</td>
                                <td class="p-3.5"><span class="px-2.5 py-1 rounded-full text-xs font-bold {% if d.status == 'รออนุมัติ' %}bg-amber-100 text-amber-800{% else %}bg-emerald-100 text-emerald-800{% endif %}">{{ d.status }}</span></td>
                                <td class="p-3.5 text-center">
                                    <button onclick="openDebtorDetail('{{ d.id }}')" class="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow">
                                        <i class="fa-solid fa-address-card mr-1"></i> ดูประวัติ & จัดการ
                                    </button>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="6" class="p-6 text-center text-slate-400">ยังไม่มีข้อมูลลูกหนี้</td></tr>
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

            <div id="section-transactions" class="hidden space-y-6"><div class="bg-white rounded-2xl p-6 shadow-sm">บันทึกการชำระหนี้</div></div>
            <div id="section-contracts" class="hidden space-y-6"><div class="bg-white rounded-2xl p-6 shadow-sm">จัดการสัญญา</div></div>
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

    <!-- Modal: ประวัติและจัดการลูกหนี้รายบุคคล -->
    <div id="debtorModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-3xl w-full p-6 md:p-8 shadow-2xl border space-y-6 max-h-[95vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b pb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold text-lg"><i class="fa-solid fa-user"></i></div>
                    <div>
                        <h3 class="text-lg font-black text-purple-900" id="modal_debtor_fullname">ชื่อ</h3>
                        <p class="text-xs text-slate-500 font-mono" id="modal_debtor_phone">เบอร์</p>
                    </div>
                </div>
                <button onclick="closeDebtorModal()" class="text-slate-400 hover:text-slate-600 font-bold text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div id="debtor_modal_content" class="space-y-5 text-xs text-slate-700"></div>

            <div class="border-t pt-4 flex flex-wrap items-center justify-between gap-3">
                <div class="flex gap-2" id="modal_action_buttons"></div>
                <button onclick="closeDebtorModal()" class="px-5 py-2.5 bg-slate-800 text-white rounded-xl font-bold text-xs">ปิดหน้าต่าง</button>
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

    <!-- Modal: ชำระหนี้แต่ละงวด -->
    <div id="payDebtModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 class="text-lg font-black text-slate-900" id="pay_debt_title">ชำระหนี้งวดนี้</h3>
            <div class="space-y-3 text-xs">
                <input type="hidden" id="pay_debt_id">
                <div>
                    <label class="block font-semibold mb-1">ยอดชำระตัดต้น (บาท)</label>
                    <input type="number" id="pay_debt_amount" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold text-rose-700">
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="button" onclick="closePayDebtModal()" class="flex-1 py-2 bg-slate-200 rounded-xl font-bold">ยกเลิก</button>
                    <button type="button" onclick="submitPayDebt()" class="flex-1 py-2 bg-emerald-600 text-white rounded-xl font-bold shadow">ยืนยัน</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: เพิ่มเงินออมสะสมแยกประเภท -->
    <div id="savingsModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 class="text-lg font-black text-slate-900">เพิ่มการออม / สะสมทรัพย์สิน</h3>
            <div class="space-y-3 text-xs">
                <div>
                    <label class="block font-semibold mb-1">เลือกประเภททรัพย์สินที่ออม</label>
                    <select id="savings_type_select" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold">
                        <option value="cash">เงินสด / เงินฝาก</option>
                        <option value="gold">ทองคำ</option>
                        <option value="stocks">หุ้น / กองทุน</option>
                    </select>
                </div>
                <div>
                    <label class="block font-semibold mb-1">จำนวนเงินออมเพิ่ม (บาท)</label>
                    <input type="number" id="add_savings_input" class="w-full px-3 py-2 bg-slate-50 border rounded-xl text-sm font-bold text-emerald-700">
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="button" onclick="closeSavingsModal()" class="flex-1 py-2 bg-slate-200 rounded-xl font-bold">ยกเลิก</button>
                    <button type="button" onclick="submitAddSavings()" class="flex-1 py-2 bg-emerald-600 text-white rounded-xl font-bold shadow">บันทึก</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: ที่มาของยอดเงินในกล่อง -->
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

        let expenseChart = null;

        function updateCalculations() {
            // คำนวณยอดเงินที่จ่ายจริงในรอบเดือนนี้เฉพาะรายการที่ขึ้นสถานะ 'จ่ายแล้ว'
            let paidExpensesSum = 0;
            householdExpenses.forEach(exp => {
                const btn = document.querySelector(`.expense-status-btn[data-exp-id="${exp.id}"]`);
                if (btn && btn.innerText === 'จ่ายแล้ว') {
                    const amtInput = document.getElementById('exp-amt-' + exp.id);
                    const val = amtInput ? (parseFloat(amtInput.value) || 0) : exp.amount;
                    paidExpensesSum += val;
                }
            });

            // รวมค่ากิน และค่าใช้จ่ายจิปาถะ
            const food = parseFloat(document.getElementById('expense-food').value) || 0;
            const misc = parseFloat(document.getElementById('expense-misc').value) || 0;
            personalFinance.food_expense = food;
            personalFinance.misc_expense = misc;

            const totalSpent = paidExpensesSum + food + misc;
            const income = personalFinance.monthly_income || 1;
            const remaining = income - totalSpent;

            // อัปเดตการแสดงผลของหลอด Progress Bar รายได้
            document.getElementById('spent-val').innerText = '฿' + totalSpent.toLocaleString('en-US', {minimumFractionDigits: 2});
            document.getElementById('net-remaining-val').innerText = '฿' + remaining.toLocaleString('en-US', {minimumFractionDigits: 2});

            let spentPercent = (totalSpent / income) * 100;
            let barWidth = spentPercent > 100 ? 100 : spentPercent;
            
            const bar = document.getElementById('income-spent-bar');
            bar.style.width = barWidth + '%';
            if (spentPercent > 100) {
                bar.className = "bg-rose-600 h-3 rounded-full transition-all duration-500";
            } else {
                bar.className = "bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500 h-3 rounded-full transition-all duration-500";
            }

            document.getElementById('spent-percent-text').innerText = 'ใช้ไป ' + spentPercent.toFixed(1) + '% ของรายรับ';
            document.getElementById('remaining-percent-text').innerText = 'คงเหลือ ' + ((remaining / income) * 100).toFixed(1) + '%';

            // อัปเดตกราฟวงกลม
            updatePieChart(paidExpensesSum, food, misc);
        }

        function updatePieChart(paidExpenses, food, misc) {
            const ctx = document.getElementById('expensePieChart').getContext('2d');
            if (expenseChart) expenseChart.destroy();
            expenseChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['ค่างวด/หนี้/ค่าห้อง/ค่าเน็ต', 'ค่ากินประจำวัน', 'ค่าใช้จ่ายจิปาถะ'],
                    datasets: [{
                        data: [paidExpenses, food, misc],
                        backgroundColor: ['#8b5cf6', '#10b981', '#f59e0b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        window.addEventListener('load', updateCalculations);

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

        function toggleEditIncome() { document.getElementById('income-edit-box').classList.toggle('hidden'); }
        function saveMonthlyIncome() {
            const val = parseFloat(document.getElementById('income-input').value) || 0;
            personalFinance.monthly_income = val;
            document.getElementById('income-display').innerText = '฿' + val.toLocaleString('en-US', {minimumFractionDigits: 2});
            toggleEditIncome();
            updateCalculations();
            alert('บันทึกรายรับใหม่สำเร็จ!');
        }

        function openSavingsModal() { document.getElementById('savingsModal').classList.remove('hidden'); }
        function closeSavingsModal() { document.getElementById('savingsModal').classList.add('hidden'); }
        function submitAddSavings() {
            const type = document.getElementById('savings_type_select').value;
            const amt = parseFloat(document.getElementById('add_savings_input').value) || 0;
            if (amt <= 0) return;

            if (type === 'cash') {
                personalFinance.savings_cash += amt;
                document.getElementById('savings-cash-val').innerText = '฿' + personalFinance.savings_cash.toLocaleString('en-US', {minimumFractionDigits: 2});
            } else if (type === 'gold') {
                personalFinance.savings_gold += amt;
                document.getElementById('savings-gold-val').innerText = '฿' + personalFinance.savings_gold.toLocaleString('en-US', {minimumFractionDigits: 2});
            } else if (type === 'stocks') {
                personalFinance.savings_stocks += amt;
                document.getElementById('savings-stocks-val').innerText = '฿' + personalFinance.savings_stocks.toLocaleString('en-US', {minimumFractionDigits: 2});
            }
            closeSavingsModal();
            alert('บันทึกการออมเพิ่มสำเร็จ!');
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
                closePayDebtModal();
                alert('บันทึกการชำระหนี้เรียบร้อย!');
            }
        }

        function toggleExpenseStatus(expId, btn) {
            const exp = householdExpenses.find(e => e.id === expId);
            if (!exp) return;

            if (btn.innerText === 'รอจ่าย') {
                btn.innerText = 'จ่ายแล้ว';
                btn.className = "px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-lg font-bold text-[11px] expense-status-btn";
                // หักงวดคงเหลือลง 1 งวดถ้ามีรายการ
                if (exp.installments > 0) {
                    exp.installments = Math.max(0, exp.installments - 1);
                    document.getElementById('exp-inst-' + expId).innerText = 'เหลือ ' + exp.installments + ' งวด';
                }
            } else {
                btn.innerText = 'รอจ่าย';
                btn.className = "px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold text-[11px] expense-status-btn";
                if (exp.installments >= 0 && exp.note.includes('งวด')) {
                    exp.installments += 1;
                    document.getElementById('exp-inst-' + expId).innerText = 'เหลือ ' + exp.installments + ' งวด';
                }
            }
            updateCalculations();
        }

        function resetMonthlyExpenses() {
            document.querySelectorAll('.expense-status-btn').forEach(btn => {
                btn.innerText = 'รอจ่าย';
                btn.className = "px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold text-[11px] expense-status-btn";
            });
            updateCalculations();
            alert('รีเซ็ตสถานะค่าใช้จ่ายประจำเดือนเรียบร้อย!');
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

        function openDebtorDetail(debtorId) {
            const debtor = debtorsData.find(d => d.id === debtorId);
            if (!debtor) return;
            document.getElementById('modal_debtor_fullname').innerText = debtor.name || 'ไม่ระบุชื่อ';
            document.getElementById('modal_debtor_phone').innerText = 'เบอร์โทร: ' + (debtor.phone || '-') + ' | รหัส: ' + (debtor.id || '-');
            
            let daysPassed = 1;
            if (debtor.date) {
                try {
                    const datePart = debtor.date.split(' ')[0];
                    const parts = datePart.split('/');
                    if (parts.length === 3) {
                        const startDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
                        const today = new Date();
                        const diffTime = today - startDate;
                        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                        daysPassed = diffDays > 0 ? diffDays : 1;
                    }
                } catch(e) { daysPassed = 1; }
            }

            const dailyRate = parseFloat(debtor.interest_rate || 100);
            const totalInterest = daysPassed * dailyRate;

            const contentDiv = document.getElementById('debtor_modal_content');
            let txHtml = '';
            let txs = debtor.transactions;
            if (typeof txs === 'string') { try { txs = JSON.parse(txs); } catch(e) { txs = []; } }
            if (txs && txs.length > 0) {
                txs.forEach(t => {
                    txHtml += `<tr><td class="p-2 font-mono">${t.date || '-'}</td><td class="p-2">${t.type || '-'}</td><td class="p-2 text-right font-mono font-bold text-emerald-600">฿${parseFloat(t.raw_amount || 0).toLocaleString()}</td></tr>`;
                });
            } else {
                txHtml = `<tr><td colspan="3" class="p-4 text-center text-slate-400">ยังไม่มีประวัติธุรกรรม</td></tr>`;
            }

            contentDiv.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="p-4 bg-purple-50 rounded-2xl border space-y-1">
                        <div><b>ชื่อ:</b> ${debtor.name || '-'}</div>
                        <div><b>โทร:</b> <span class="font-mono">${debtor.phone || '-'}</span></div>
                        <div><b>Facebook:</b> <a href="${debtor.facebook || '#'}" target="_blank" class="text-blue-600 underline">${debtor.facebook || 'ไม่มี'}</a></div>
                        <div><b>ธนาคาร:</b> ${debtor.bank || '-'} (<span class="font-mono">${debtor.acc || '-'}</span>)</div>
                    </div>
                    <div class="p-4 bg-slate-50 rounded-2xl border space-y-1">
                        <div><b>เงินต้น:</b> <span class="font-mono font-bold text-rose-700">฿${parseFloat(debtor.principal || 0).toLocaleString()}</span></div>
                        <div><b>ประเภทดอกเบี้ย:</b> <span class="px-2 py-0.5 bg-purple-100 text-purple-800 rounded font-bold">${debtor.interest_type || 'ดอกลอย'}</span></div>
                        <div><b>อัตราดอกเบี้ย:</b> <span class="font-mono text-purple-700 font-bold">฿${dailyRate.toLocaleString()} / วัน</span></div>
                        <div><b>ระยะเวลาที่กู้:</b> <span class="font-mono font-bold text-blue-700">${daysPassed} วัน</span></div>
                        <div class="pt-1 border-t mt-1"><b>🧮 ดอกเบี้ยสะสมอัตโนมัติ:</b> <span class="font-mono font-black text-emerald-700 text-sm">฿${totalInterest.toLocaleString()}</span></div>
                        <div><b>สถานะ:</b> <span class="px-2 py-0.5 rounded font-bold ${debtor.status == 'รออนุมัติ' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">${debtor.status || 'รออนุมัติ'}</span></div>
                    </div>
                </div>
                <div class="space-y-2">
                    <h4 class="font-bold text-xs text-slate-800 uppercase">ประวัติธุรกรรม</h4>
                    <div class="border rounded-2xl overflow-hidden max-h-40 overflow-y-auto bg-white">
                        <table class="w-full text-left text-xs"><thead class="bg-slate-100"><tr><th class="p-2">เวลา</th><th class="p-2">รายการ</th><th class="p-2 text-right">จำนวนเงิน</th></tr></thead><tbody class="divide-y">${txHtml}</tbody></table>
                    </div>
                </div>
            `;

            let cleanId = encodeURIComponent(debtor.id);
            let actionHtml = '';
            if (debtor.status === 'รออนุมัติ') {
                actionHtml += `<a href="/approve-debtor?debtor_id=${cleanId}" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow flex items-center"><i class="fa-solid fa-check mr-1.5"></i> อนุมัติคำขอกู้เงิน</a>`;
            }
            actionHtml += `<button onclick="openEditDebtor('${debtor.id}', ${debtor.principal || 0}, '${debtor.interest_type || 'ดอกลอย'}', ${dailyRate})" class="px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-xs shadow"><i class="fa-solid fa-pen-to-square mr-1.5"></i> แก้ไขวงเงิน/ดอกเบี้ย</button>`;
            
            document.getElementById('modal_action_buttons').innerHTML = actionHtml;
            document.getElementById('debtorModal').classList.remove('hidden');
        }
        function closeDebtorModal() { document.getElementById('debtorModal').classList.add('hidden'); }

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
        </div>
        <form action="/submit-application" method="POST" enctype="multipart/form-data" class="space-y-4" onsubmit="prepareSignature()">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ - นามสกุลจริง</label>
                <input type="text" name="name" required placeholder="สมชาย ใจดี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">เบอร์โทรศัพท์ (ยืนยันแล้ว)</label>
                <input type="text" name="phone" readonly value="{{ session.get('verified_phone', '') }}" class="w-full px-4 py-2.5 bg-purple-50 border rounded-xl text-sm font-bold text-purple-800 cursor-not-allowed">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ลิงก์ Facebook</label>
                <input type="url" name="facebook" required placeholder="https://www.facebook.com/..." class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
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
                    <input type="text" name="account" required placeholder="เลขบัญชี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ขอกู้วงเงินเงินต้น (บาท)</label>
                <input type="number" name="amount" required placeholder="10000" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-lg">
            </div>
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
    return render_template_string(APPLY_TEMPLATE)

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

@app.route('/submit-application', methods=['POST'])
def submit_application():
    amount = float(request.form.get('amount') or 0)
    name = request.form.get('name')
    phone = request.form.get('phone')
    bank = request.form.get('bank', '')
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
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'transactions': json.dumps([{'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'ยื่นขอกู้เงินออนไลน์', 'raw_amount': amount}])
    }
    try:
        supabase.table("debtors").insert(new_entry).execute()
    except Exception as e:
        print(f"Insert Error: {e}")
    send_telegram_alert(f"🚨 <b>มีคำขอกู้เงินใหม่!</b>\n👤 ชื่อ: {name}\n💰 ยอด: ฿{amount:,.2f}")
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
