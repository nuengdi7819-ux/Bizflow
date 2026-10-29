from flask import Flask, render_template_string, request, Response, redirect, url_for, session
import os
import csv
import io
import urllib.request
import urllib.parse
import json
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bizflow_secure_secret_key'

# ฐานข้อมูลลูกหนี้
debtors_database = []

# ระบบเก็บข้อมูลการขอ OTP ชั่วคราวของสมาชิก (เบอร์โทร -> OTP ล่าสุด)
pending_otp_sessions = {}

# ฐานข้อมูลผู้ใช้งานระบบหลังบ้าน (แอดมิน)
users_database = [
    {'id': 1, 'name': 'Owner (คุณสมชาย)', 'username': 'owner', 'role': 'Owner / Super Admin', 'status': 'ใช้งานอยู่', 'last_login': '30/10/2026 08:30'}
]

activity_logs = [
    {'time': '30/10/2026 08:30', 'user': 'Owner', 'action': 'เข้าสู่ระบบหลังบ้าน', 'ip': '127.0.0.1'}
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

@app.template_filter('format_num')
def format_num_filter(value):
    try:
        return f"{float(value):,.0f}"
    except:
        return "0"

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
                            <i class="fa-solid fa-building-columns text-sm text-sky-400 w-5"></i><span>บัญชีธนาคาร & เงินสด</span>
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
        <div class="p-4 border-t border-purple-900/40 text-xs text-purple-300/60 flex items-center justify-between">
            <span>ผู้ดูแลระบบ: Owner</span>
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>
    </aside>

    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50 w-full">
        <header class="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 md:px-8 py-4 flex items-center justify-between shadow-sm">
            <h2 id="page-title" class="text-lg md:text-xl font-bold text-slate-800">แดชบอร์ดหลัก</h2>
            <div class="flex items-center space-x-4">
                <div class="relative cursor-pointer" onclick="switchTab('debtors')">
                    <i class="fa-solid fa-bell text-xl text-purple-600 hover:text-purple-800"></i>
                    <span id="bell-badge" class="absolute -top-1 -right-1 bg-rose-600 text-white font-bold text-[10px] w-4 h-4 rounded-full flex items-center justify-center hidden">0</span>
                </div>
                <a href="/apply" target="_blank" class="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium text-xs md:text-sm shadow-md flex items-center space-x-1.5">
                    <i class="fa-solid fa-external-link-alt"></i><span>เปิดหน้าบ้านสมาชิก</span>
                </a>
            </div>
        </header>

        <div class="p-4 md:p-8">

            <div id="section-dashboard" class="space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                    <div class="p-5 rounded-2xl bg-amber-500 text-white shadow-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-amber-100 uppercase tracking-wider">📁 ยอดค้างเก่าคงเหลือ</span>
                            <i class="fa-solid fa-folder-open text-amber-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">0.00 บ.</h3>
                    </div>
                    <div class="p-5 rounded-2xl bg-rose-700 text-white shadow-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-rose-200 uppercase tracking-wider">💼 เงินต้นคงค้าง</span>
                            <i class="fa-solid fa-briefcase text-rose-300 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">0.00 บ.</h3>
                    </div>
                    <div class="p-5 rounded-2xl bg-blue-600 text-white shadow-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-blue-200 uppercase tracking-wider">🔱 เงินลงทุนใหม่ (เดือนนี้)</span>
                            <i class="fa-solid fa-chart-line text-blue-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">0.00 บ.</h3>
                    </div>
                    <div class="p-5 rounded-2xl bg-emerald-600 text-white shadow-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-emerald-200 uppercase tracking-wider">💰 กำไรสะสม (เดือนนี้)</span>
                            <i class="fa-solid fa-sack-dollar text-emerald-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">0.00 บ.</h3>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สรุปรายรับ - รายจ่าย</h4>
                        <div class="h-64"><canvas id="financeChart"></canvas></div>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สัดส่วนบัญชีเงินฝาก</h4>
                        <div class="h-64 flex items-center justify-center"><canvas id="accountChart"></canvas></div>
                    </div>
                </div>
            </div>

            <!-- Tab: จัดการคำขอกู้ -->
            <div id="section-debtors" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-4 md:p-6 shadow-sm overflow-x-auto">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div class="flex items-center gap-2">
                            <button onclick="setFilterStatus('ทั้งหมด')" id="filter-all" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white">ทั้งหมด</button>
                            <button onclick="setFilterStatus('รออนุมัติ')" id="filter-pending" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-amber-50 text-amber-800 border border-amber-300">รออนุมัติ</button>
                            <button onclick="setFilterStatus('ปกติ')" id="filter-approved" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-600">อนุมัติแล้ว</button>
                        </div>
                        <input type="text" id="searchInput" oninput="renderDebtorsTable()" placeholder="ค้นหาด้วยชื่อ หรือ เบอร์โทร..." class="px-4 py-2 bg-slate-50 border rounded-xl text-xs w-64">
                    </div>

                    <table class="w-full text-left text-sm min-w-[700px]">
                        <thead class="bg-slate-50 text-slate-500">
                            <tr>
                                <th class="p-3.5">ชื่อ-เบอร์โทร (คลิกดูประวัติ)</th>
                                <th class="p-3.5">วันที่ทำธุรกรรม</th>
                                <th class="p-3.5">เงินต้นกู้</th>
                                <th class="p-3.5">ประเภทชำระ</th>
                                <th class="p-3.5">สถานะ</th>
                                <th class="p-3.5 text-center">จัดการคำขอ / ดู Ledger</th>
                            </tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <!-- Tab: อนุมัติรหัส OTP ลูกค้า -->
            <div id="section-otp_requests" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-key text-rose-500 mr-2"></i> คำขอรหัส OTP จากสมาชิกหน้าเว็บ
                    </h3>
                    <p class="text-xs text-slate-500">เมื่อลูกค้ากรอกเบอร์โทรขอเข้าสู่ระบบ แอดมินจะเห็นรหัส OTP ชั่วคราวที่ถูกสุ่มขึ้นมาใหม่ตรงนี้ ให้นำรหัสนี้แจ้งลูกค้า</p>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs bg-white rounded-xl border">
                            <thead class="bg-slate-100 text-slate-600">
                                <tr>
                                    <th class="p-3">เบอร์โทรศัพท์มือถือ</th>
                                    <th class="p-3">เวลาที่ขอ OTP</th>
                                    <th class="p-3 text-center">รหัส OTP ชั่วคราว (สุ่มใหม่)</th>
                                    <th class="p-3 text-right">จัดการ</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y">
                                {% if otp_list %}
                                    {% for phone, data in otp_list.items() %}
                                    <tr>
                                        <td class="p-3 font-mono font-bold text-purple-800 text-sm"><i class="fa-solid fa-phone mr-1"></i>{{ phone }}</td>
                                        <td class="p-3 text-slate-500">{{ data.time }}</td>
                                        <td class="p-3 text-center">
                                            <span class="px-3 py-1.5 bg-rose-100 text-rose-800 rounded-xl font-mono font-black text-base tracking-widest shadow-inner">{{ data.otp }}</span>
                                        </td>
                                        <td class="p-3 text-right">
                                            <a href="/clear-otp?phone={{ phone }}" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg font-bold">รีเซ็ต/ลบ OTP</a>
                                        </td>
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

            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white shadow-lg space-y-3">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                            <button onclick="toggleEditBank('kbank')" class="text-emerald-200 hover:text-white text-xs bg-emerald-700/60 px-2.5 py-1 rounded-lg"><i class="fa-solid fa-pen mr-1"></i>แก้ไขยอด</button>
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
                            <button onclick="toggleEditBank('scb')" class="text-purple-200 hover:text-white text-xs bg-purple-800/60 px-2.5 py-1 rounded-lg"><i class="fa-solid fa-pen mr-1"></i>แก้ไขยอด</button>
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
                            <button onclick="toggleEditBank('cash')" class="text-slate-300 hover:text-white text-xs bg-slate-700 px-2.5 py-1 rounded-lg"><i class="fa-solid fa-pen mr-1"></i>แก้ไขยอด</button>
                        </div>
                        <div id="bank-cash-display" class="text-3xl font-black tracking-tight py-2">฿{{ bank_cash | format_num }}</div>
                        <div id="bank-cash-edit" class="hidden space-y-2">
                            <input type="number" id="bank-cash-input" value="{{ bank_cash }}" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-xl text-xl font-black text-white">
                            <button onclick="saveBankBalance('cash')" class="w-full py-1.5 bg-white text-slate-900 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">บันทึกการชำระหนี้ / สลิปโอนเงิน</h3>
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
                            <h4 class="text-xs font-bold text-purple-900 uppercase"><i class="fa-solid fa-users-gear mr-1"></i> 1. จัดการผู้ใช้งาน & เพิ่มแอดมิน</h4>
                            <div class="overflow-x-auto">
                                <table class="w-full text-left text-xs bg-white rounded-xl border mb-3">
                                    <thead class="bg-slate-100 text-slate-600">
                                        <tr>
                                            <th class="p-2.5">ชื่อ-นามสกุล / Username</th>
                                            <th class="p-2.5">บทบาท</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for u in users %}
                                        <tr class="border-t">
                                            <td class="p-2.5 font-bold">{{ u.name }} <br><span class="text-purple-600 font-mono text-[10px]">(@{{ u.username }})</span></td>
                                            <td class="p-2.5 text-purple-700 font-semibold">{{ u.role }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>

                            <form action="/add-admin" method="POST" class="space-y-2 pt-2 border-t">
                                <span class="text-xs font-bold text-slate-700 block">➕ เพิ่มบัญชีแอดมินใหม่</span>
                                <div class="grid grid-cols-2 gap-2">
                                    <input type="text" name="admin_name" required placeholder="ชื่อแอดมิน" class="px-3 py-1.5 bg-white border rounded-lg text-xs">
                                    <input type="text" name="admin_user" required placeholder="Username" class="px-3 py-1.5 bg-white border rounded-lg text-xs">
                                </div>
                                <div class="grid grid-cols-2 gap-2">
                                    <input type="password" name="admin_pass" required placeholder="Password" class="px-3 py-1.5 bg-white border rounded-lg text-xs">
                                    <button type="submit" class="py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold shadow">บันทึกแอดมิน</button>
                                </div>
                            </form>
                        </div>

                        <div class="p-4 bg-purple-50/50 border border-purple-200 rounded-2xl space-y-3">
                            <h4 class="text-xs font-bold text-purple-900 uppercase"><i class="fa-solid fa-database mr-1"></i> 2. จัดการฐานข้อมูล & เตรียมใช้งานจริง</h4>
                            <p class="text-xs text-slate-500">สำรองข้อมูลเป็น CSV หรือล้างข้อมูลจำลองเพื่อเริ่มต้นใช้งานจริง</p>
                            
                            <div class="flex gap-2 pt-1">
                                <a href="/export-csv" class="flex-1 py-2.5 bg-purple-600 text-white rounded-xl text-xs font-bold shadow hover:bg-purple-700 text-center flex items-center justify-center space-x-1">
                                    <i class="fa-solid fa-download"></i><span>Export CSV</span>
                                </a>
                                <button onclick="if(confirm('ต้องการรีเซ็ตข้อมูลทั้งหมดจริงหรือไม่?')) { window.location.href='/clear-data'; }" class="py-2.5 px-4 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow">
                                    <i class="fa-solid fa-trash-can mr-1"></i> รีเซ็ตข้อมูล
                                </button>
                            </div>

                            <form action="/import-csv" method="POST" enctype="multipart/form-data" class="pt-2 border-t border-purple-200 space-y-2">
                                <label class="block text-xs font-semibold text-slate-700">อัปโหลดไฟล์ CSV เพื่อกู้คืนข้อมูล</label>
                                <input type="file" name="csv_file" accept=".csv" required class="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-purple-200 file:text-purple-800">
                                <button type="submit" class="w-full py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow hover:bg-slate-900">
                                    <i class="fa-solid fa-upload mr-1"></i> นำเข้าข้อมูล (Import CSV)
                                </button>
                            </form>
                        </div>

                        <div class="p-4 bg-slate-50 border rounded-2xl space-y-3 md:col-span-2">
                            <h4 class="text-xs font-bold text-purple-900 uppercase"><i class="fa-brands fa-telegram text-sky-600 mr-1"></i> 3. ช่องทางแจ้งเตือน Telegram Bot & ความปลอดภัย</h4>
                            <form action="/update-telegram" method="POST" class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs items-end">
                                <div>
                                    <label class="block font-semibold text-slate-700 mb-1">Telegram Bot Token</label>
                                    <input type="text" name="tg_token" value="{{ config.telegram_token }}" class="w-full px-3 py-2 bg-white border rounded-xl font-mono">
                                </div>
                                <div>
                                    <label class="block font-semibold text-slate-700 mb-1">Telegram Chat ID</label>
                                    <input type="text" name="tg_chat_id" value="{{ config.telegram_chat_id }}" placeholder="เช่น 1880260879" class="w-full px-3 py-2 bg-white border rounded-xl font-mono">
                                </div>
                                <div class="flex gap-2">
                                    <button type="submit" class="flex-1 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow">บันทึกค่า</button>
                                    <button type="button" onclick="testTelegram()" class="py-2 px-3 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold shadow"><i class="fa-solid fa-paper-plane"></i> ทดสอบ</button>
                                </div>
                            </form>
                        </div>

                    </div>

                    <div class="p-4 bg-slate-50 border rounded-2xl space-y-3">
                        <h4 class="text-xs font-bold text-slate-700 uppercase"><i class="fa-solid fa-shield-halved text-emerald-600 mr-1"></i> 4. ประวัติการใช้งานระบบ (Activity Logs)</h4>
                        <div class="bg-white rounded-xl border overflow-x-auto max-h-48">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-600">
                                    <tr>
                                        <th class="p-2.5">เวลา</th>
                                        <th class="p-2.5">ผู้ใช้งาน</th>
                                        <th class="p-2.5">กิจกรรม / รายการ</th>
                                        <th class="p-2.5">IP Address</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y">
                                    {% for log in logs %}
                                    <tr>
                                        <td class="p-2.5 text-slate-500 font-mono">{{ log.time }}</td>
                                        <td class="p-2.5 font-bold text-purple-800">{{ log.user }}</td>
                                        <td class="p-2.5 text-slate-800">{{ log.action }}</td>
                                        <td class="p-2.5 text-slate-400 font-mono">{{ log.ip }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                </div>
            </div>

        </div>
    </main>

    <div id="userDetailModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-4xl w-full p-6 md:p-8 shadow-2xl max-h-[92vh] overflow-y-auto space-y-6">
            <div class="flex items-center justify-between pb-4 border-b">
                <span id="detail-user-id" class="px-2.5 py-1 bg-purple-100 text-purple-800 rounded-lg text-xs font-mono font-bold">#000000</span>
                <button onclick="closeUserDetailModal()" class="px-3 py-1.5 bg-slate-100 rounded-xl text-xs font-bold">✕ ปิด</button>
            </div>
            <div id="approve-btn-container" class="grid grid-cols-2 gap-4 pt-2"></div>
        </div>
    </div>

    <script>
        let debtorsList = {{ debtors | tojson }};
        let currentFilterStatus = 'ทั้งหมด';

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

        function toggleEditBank(bankName) {
            const display = document.getElementById('bank-' + bankName + '-display');
            const editBox = document.getElementById('bank-' + bankName + '-edit');
            if (editBox.classList.contains('hidden')) {
                editBox.classList.remove('hidden');
                display.classList.add('hidden');
            } else {
                editBox.classList.add('hidden');
                display.classList.remove('hidden');
            }
        }

        function saveBankBalance(bankName) {
            const val = document.getElementById('bank-' + bankName + '-input').value;
            fetch('/update-bank', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bank: bankName, amount: val })
            }).then(res => res.json()).then(data => {
                if(data.success) { alert('บันทึกยอดเงินสำเร็จ!'); location.reload(); }
            });
        }

        function testTelegram() {
            fetch('/test-telegram', { method: 'POST' }).then(res => res.json()).then(data => {
                if(data.success) { alert('ส่งข้อความทดสอบเข้า Telegram สำเร็จ!'); }
                else { alert('ส่งไม่สำเร็จ กรุณาตรวจสอบ Token และ Chat ID'); }
            });
        }

        function renderDebtorsTable() {
            const tbody = document.getElementById('debtor-table-body');
            tbody.innerHTML = '';
            if (debtorsList.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-slate-400">ยังไม่มีข้อมูลลูกหนี้ในระบบ (รอการยื่นกู้ผ่านหน้าบ้านสมาชิก)</td></tr>`;
                return;
            }
        }

        window.onload = function() { renderDebtorsTable(); }
    </script>
</body>
</html>
"""

# หน้า Login สมาชิกแบบกรอกเบอร์โทร + ขอ OTP จากแอดมิน
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
        <div class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl text-center font-bold">
            {{ error }}
        </div>
        {% endif %}

        {% if success_msg %}
        <div class="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl text-center font-semibold">
            {{ success_msg }}
        </div>
        {% endif %}

        <form action="/apply-login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-solid fa-phone mr-1 text-purple-600"></i> เบอร์โทรศัพท์มือถือ</label>
                <input type="text" name="phone" required placeholder="เช่น 0891234567" value="{{ phone_val or '' }}" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-solid fa-key mr-1 text-purple-600"></i> รหัส OTP (สอดคล้องกับที่ขอจากแอดมิน)</label>
                <input type="text" name="otp_code" required placeholder="กรอกรหัส OTP 4 หลัก" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono tracking-widest text-center text-lg font-bold">
            </div>

            <div class="flex gap-2 pt-2">
                <button type="submit" name="action" value="request_otp" class="flex-1 py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-xs shadow">
                    ขอรหัส OTP ใหม่
                </button>
                <button type="submit" name="action" value="verify_login" class="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold text-xs shadow">
                    ยืนยัน OTP เข้าสู่ระบบ
                </button>
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
                    <select name="payment_term" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
                        <option value="รายวัน">รายวัน</option>
                        <option value="รายวันเว้นอาทิตย์">รายวันเว้นอาทิตย์</option>
                        <option value="ราย 15 วัน">ราย 15 วัน</option>
                    </select>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ธนาคารรับเงิน</label>
                    <input type="text" name="bank" required placeholder="เช่น กสิกรไทย" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
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

            <button type="submit" class="w-full py-3.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow-lg mt-2">
                ยื่นคำขอกู้เงินและส่งสัญญา
            </button>
        </form>
    </div>

    <script>
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

# เก็บคำขอ OTP ที่รอแอดมินแจ้ง
active_otp_requests = {}

@app.route('/')
def admin_dashboard():
    return render_template_string(ADMIN_TEMPLATE, 
                                 debtors=debtors_database,
                                 users=users_database,
                                 logs=activity_logs,
                                 config=system_config,
                                 otp_list=active_otp_requests,
                                 bank_kbank=bank_accounts['kbank'],
                                 bank_scb=bank_accounts['scb'],
                                 bank_cash=bank_accounts['cash'])

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
        # สุ่มรหัส OTP ใหม่ 4 หลัก (ไม่ซ้ำเดิม)
        new_otp = str(random.randint(1000, 9999))
        active_otp_requests[phone] = {
            'otp': new_otp,
            'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # ส่งแจ้งเตือนเข้า Telegram ให้แอดมินทราบทันทีว่ามีเบอร์นี้ขอ OTP
        send_telegram_alert(f"🔑 <b>มีคำขอรหัส OTP ใหม่!</b>\n📞 เบอร์โทร: <code>{phone}</code>\n🔢 รหัส OTP: <b>{new_otp}</b>\n\n(แจ้งรหัสนี้ให้ลูกค้าเพื่อเข้าสู่ระบบ)")
        
        return render_template_string(LOGIN_MEMBER_TEMPLATE, 
                                     phone_val=phone,
                                     success_msg=f"ส่งคำขอ OTP สำหรับเบอร์ {phone} สำเร็จ! กรุณาติดต่อขอรหัสจากแอดมิน")

    elif action == 'verify_login':
        if phone in active_otp_requests and active_otp_requests[phone]['otp'] == otp_input:
            session['member_verified'] = True
            session['verified_phone'] = phone
            # ลบ OTP ออกหลังใช้งานเพื่อความปลอดภัย (ใช้ครั้งเดียวทิ้ง)
            del active_otp_requests[phone]
            return redirect(url_for('apply_form'))
        else:
            return render_template_string(LOGIN_MEMBER_TEMPLATE, 
                                         phone_val=phone,
                                         error="รหัส OTP ไม่ถูกต้อง หรือยังไม่ได้กดขอรหัสจากแอดมิน!")

    return render_template_string(LOGIN_MEMBER_TEMPLATE)

@app.route('/clear-otp')
def clear_otp():
    phone = request.args.get('phone')
    if phone in active_otp_requests:
        del active_otp_requests[phone]
    return redirect(url_for('admin_dashboard'))

@app.route('/update-bank', methods=['POST'])
def update_bank():
    data = request.json
    b_name = data.get('bank')
    amount = float(data.get('amount') or 0)
    if b_name in bank_accounts:
        bank_accounts[b_name] = amount
        activity_logs.insert(0, {'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': 'Owner', 'action': f'อัปเดตยอดเงิน {b_name.upper()} เป็น ฿{amount:,.0f}', 'ip': '127.0.0.1'})
        return {'success': True}
    return {'success': False}

@app.route('/update-telegram', methods=['POST'])
def update_telegram():
    system_config['telegram_token'] = request.form.get('tg_token')
    system_config['telegram_chat_id'] = request.form.get('tg_chat_id')
    activity_logs.insert(0, {'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': 'Owner', 'action': 'อัปเดตตั้งค่า Telegram Bot', 'ip': '127.0.0.1'})
    return "<script>alert('บันทึก Telegram สำเร็จ!'); window.location.href='/';</script>"

@app.route('/test-telegram', methods=['POST'])
def test_telegram():
    success = send_telegram_alert("🔔 <b>BizFlow+ Test Alert</b>\nระบบแจ้งเตือนผ่าน Telegram ทำงานปกติแล้วครับ!")
    return {'success': success}

@app.route('/add-admin', methods=['POST'])
def add_admin():
    name = request.form.get('admin_name')
    username = request.form.get('admin_user')
    users_database.append({
        'id': len(users_database) + 1,
        'name': name,
        'username': username,
        'role': 'Staff / Operator',
        'status': 'ใช้งานอยู่',
        'last_login': '-'
    })
    activity_logs.insert(0, {'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': 'Owner', 'action': f'เพิ่มแอดมินใหม่: {name} (@{username})', 'ip': '127.0.0.1'})
    return "<script>alert('เพิ่มแอดมินสำเร็จ!'); window.location.href='/';</script>"

@app.route('/submit-application', methods=['POST'])
def submit_application():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    amount = float(request.form.get('amount') or 0)
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    new_entry = {
        'id': f"#{len(debtors_database)+541540}",
        'name': name,
        'phone': phone,
        'facebook': request.form.get('facebook'),
        'acc': request.form.get('account'),
        'bank': request.form.get('bank'),
        'principal': amount,
        'payment_term': request.form.get('payment_term', 'รายวัน'),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'ip': client_ip,
        'status': 'รออนุมัติ',
        'idCardPhoto': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
        'signature': 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=400',
        'credit_limit': amount * 1.2,
        'outstanding_balance': amount,
        'available_credit': amount * 0.2,
        'transactions': [{'tx_id': f"TXN-2026-00{len(debtors_database)+1}", 'date': datetime.now().strftime('%d/%m/%Y %H:%M'), 'type': 'เบิกเงินกู้ใหม่', 'amount': f"+฿{amount:,.0f}", 'status': 'รอตรวจสอบ'}],
        'internal_notes': 'ยื่นกู้ผ่านหน้าเว็บสมาชิกด้วย OTP'
    }
    debtors_database.insert(0, new_entry)
    
    msg = f"🚨 <b>มีคำขอกู้เงินใหม่เข้ามา!</b>\n👤 ชื่อ: {name}\n📞 โทร: {phone}\n💰 ยอดกู้: ฿{amount:,.0f}\n📅 รูปแบบ: {new_entry['payment_term']}"
    send_telegram_alert(msg)

    activity_logs.insert(0, {'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': f'สมาชิก ({phone})', 'action': f'ลูกค้ายื่นกู้ใหม่: {name} (฿{amount:,.0f})', 'ip': client_ip})
    
    # ล้างสถานะ Verified เพื่อความปลอดภัยหลังส่งกู้เสร็จ
    session.pop('member_verified', None)
    
    return "<script>alert('ยื่นคำขอกู้เรียบร้อย!'); window.location.href='/apply';</script>"

@app.route('/clear-data')
def clear_data():
    debtors_database.clear()
    activity_logs.clear()
    activity_logs.append({'time': datetime.now().strftime('%d/%m/%Y %H:%M'), 'user': 'Owner', 'action': 'รีเซ็ตข้อมูลทั้งหมดในระบบ', 'ip': '127.0.0.1'})
    return "<script>alert('ล้างข้อมูลสำเร็จ พร้อมใช้งานจริงแล้ว!'); window.location.href='/';</script>"

@app.route('/export-csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Facebook', 'Bank', 'Account', 'Principal', 'PaymentTerm', 'Status', 'Date'])
    for d in debtors_database:
        writer.writerow([d['id'], d['name'], d['phone'], d['facebook'], d['bank'], d['acc'], d['principal'], d['payment_term'], d['status'], d['date']])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=debtors_backup.csv"})

@app.route('/import-csv', methods=['POST'])
def import_csv():
    if 'csv_file' not in request.files:
        return "<script>alert('ไม่พบไฟล์ CSV'); window.location.href='/';</script>"
    file = request.files['csv_file']
    try:
        stream = io.TextIOWrapper(file.stream, encoding="utf-8")
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            if len(row) >= 10:
                debtors_database.append({
                    'id': row[0], 'name': row[1], 'phone': row[2], 'facebook': row[3],
                    'bank': row[4], 'acc': row[5], 'principal': float(row[6] or 0),
                    'payment_term': row[7], 'status': row[8], 'date': row[9],
                    'ip': '127.0.0.1', 'idCardPhoto': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
                    'signature': 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=400',
                    'credit_limit': float(row[6] or 0) * 1.2, 'outstanding_balance': float(row[6] or 0),
                    'available_credit': 0, 'transactions': [], 'internal_notes': 'นำเข้าจาก CSV'
                })
        return "<script>alert('นำเข้าข้อมูลสำเร็จ!'); window.location.href='/';</script>"
    except Exception as e:
        return f"<script>alert('เกิดข้อผิดพลาด: {str(e)}'); window.location.href='/';</script>"

if __name__ == '__main__':
    app.run(debug=True)
