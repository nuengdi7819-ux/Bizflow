from flask import Flask, render_template_string, request, Response
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)

# ฐานข้อมูลจำลองลูกหนี้
debtors_database = [
    {
        'id': '#541542',
        'username': '0929237819',
        'name': 'หนึ่งฤดี นาน้อย',
        'phone': '0929237819',
        'facebook': 'https://facebook.com/nuengruedi',
        'acc': '0113514345',
        'bank': 'กสิกรไทย',
        'principal': 1000000,
        'interest_type': 'ดอกคงที่',
        'payment_term': 'รายวัน',
        'daily_interest_rate': 0,
        'fixed_interest': 2000,
        'installment_amount': 0,
        'start_date': '2026-10-29',
        'date': '29/10/2026 21:15',
        'ip': '223.24.215.40',
        'status': 'รออนุมัติ',
        'idCardPhoto': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
        'signature': 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=400',
        'total_loans': 1,
        'old_debt': 0,
        'remark': 'ลูกค้ายื่นกู้ใหม่ รอตรวจสอบรูปและลายเซ็น'
    }
]

bank_accounts = {
    'kbank': 145000,
    'scb': 98500,
    'cash': 41000
}

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

    <!-- Mobile Top Bar -->
    <div class="md:hidden bg-[#18092e] text-white p-4 flex items-center justify-between shadow-md sticky top-0 z-40">
        <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-xl bg-purple-600 flex items-center justify-center font-black">B</div>
            <span class="font-bold text-lg">BizFlow <span class="text-xs bg-purple-500 px-1.5 py-0.5 rounded">PLUS</span></span>
        </div>
        <button onclick="toggleSidebar()" class="text-purple-300 hover:text-white text-xl p-2"><i class="fa-solid fa-bars"></i></button>
    </div>

    <!-- Sidebar Menu -->
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
                        <a href="/apply" target="_blank" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-emerald-300 hover:bg-emerald-950/40 border border-emerald-500/30 mt-1">
                            <i class="fa-solid fa-globe text-sm text-emerald-400 w-5"></i><span>🔗 หน้าบ้านยื่นกู้ (/apply)</span>
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

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50 w-full">
        <header class="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 md:px-8 py-4 flex items-center justify-between shadow-sm">
            <h2 id="page-title" class="text-lg md:text-xl font-bold text-slate-800">แดชบอร์ดหลัก</h2>
            <div class="flex items-center space-x-4">
                <div class="relative cursor-pointer" onclick="switchTab('debtors')">
                    <i class="fa-solid fa-bell text-xl text-purple-600 hover:text-purple-800"></i>
                    <span id="bell-badge" class="absolute -top-1 -right-1 bg-rose-600 text-white font-bold text-[10px] w-4 h-4 rounded-full flex items-center justify-center animate-pulse">1</span>
                </div>
                <a href="/apply" target="_blank" class="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium text-xs md:text-sm shadow-md flex items-center space-x-1.5">
                    <i class="fa-solid fa-external-link-alt"></i><span>เปิดหน้าบ้าน (ขอกู้)</span>
                </a>
            </div>
        </header>

        <div class="p-4 md:p-8">

            <!-- 1. Section: Dashboard -->
            <div id="section-dashboard" class="space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                    <div onclick="openFolderDetail('old_debt')" class="p-5 rounded-2xl bg-amber-500 text-white shadow-lg cursor-pointer hover:opacity-95 transition-all">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-amber-100 uppercase tracking-wider">📁 ยอดค้างเก่าคงเหลือ</span>
                            <i class="fa-solid fa-folder-open text-amber-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">670,541.19 บ.</h3>
                        <p class="text-[10px] text-amber-100/80 mt-1">ยอดสะสมหลายปี • กดดูรายชื่อ →</p>
                    </div>

                    <div onclick="openFolderDetail('current_debt')" class="p-5 rounded-2xl bg-rose-700 text-white shadow-lg cursor-pointer hover:opacity-95 transition-all">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-rose-200 uppercase tracking-wider">💼 เงินต้นคงค้าง</span>
                            <i class="fa-solid fa-briefcase text-rose-300 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">97,770.00 บ.</h3>
                        <p class="text-[10px] text-rose-200/80 mt-1">ค้างใหม่ปัจจุบัน • กดดูรายชื่อ →</p>
                    </div>

                    <div onclick="openFolderDetail('new_investment')" class="p-5 rounded-2xl bg-blue-600 text-white shadow-lg cursor-pointer hover:opacity-95 transition-all">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-blue-200 uppercase tracking-wider">🔱 เงินลงทุนใหม่ (เดือนนี้)</span>
                            <i class="fa-solid fa-chart-line text-blue-200 text-lg"></i>
                        </div>
                        <h3 id="dash-new-investment" class="text-2xl font-black tracking-tight">1,151,860.00 บ.</h3>
                        <p class="text-[10px] text-blue-100/80 mt-1">ปล่อยกู้เดือนนี้ • กดดูรายการ →</p>
                    </div>

                    <div onclick="openFolderDetail('monthly_profit')" class="p-5 rounded-2xl bg-emerald-600 text-white shadow-lg cursor-pointer hover:opacity-95 transition-all">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-emerald-200 uppercase tracking-wider">💰 กำไรสะสม (เดือนนี้)</span>
                            <i class="fa-solid fa-sack-dollar text-emerald-200 text-lg"></i>
                        </div>
                        <h3 class="text-2xl font-black tracking-tight">71,405.49 บ.</h3>
                        <p class="text-[10px] text-emerald-100/80 mt-1">ดอกเบี้ยรับเดือนนี้ • กดดูรายการ →</p>
                    </div>
                </div>

                <!-- แจ้งเตือนรายการที่ต้องทวงวันนี้ -->
                <div class="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
                    <div class="flex items-center justify-between">
                        <h4 class="font-bold text-slate-800 text-base flex items-center">
                            <i class="fa-solid fa-bell text-amber-500 mr-2 animate-bounce"></i> รายการที่ต้องทวงวันนี้ (ประจำวันที่ 30 ต.ค. 2026)
                        </h4>
                        <span class="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-bold">1 รายการต้องติดตาม</span>
                    </div>
                    <div class="divide-y divide-slate-100 text-xs">
                        <div class="py-2.5 flex items-center justify-between">
                            <div>
                                <span class="font-bold text-slate-800">หนึ่งฤดี นาน้อย (0929237819)</span>
                                <p class="text-slate-400">ประเภท: รายวัน • ยอดที่ต้องเก็บวันนี้: ฿5,000</p>
                            </div>
                            <button onclick="openUserDetail(0)" class="px-3 py-1 bg-purple-50 text-purple-700 rounded-lg font-bold border border-purple-200">ตรวจสอบ / ดูสลิป</button>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สรุปรายรับ - รายจ่าย (ปี 2026)</h4>
                        <div class="h-64"><canvas id="financeChart"></canvas></div>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สัดส่วนบัญชีเงินฝาก</h4>
                        <div class="h-64 flex items-center justify-center"><canvas id="accountChart"></canvas></div>
                    </div>
                </div>
            </div>

            <!-- 2. Section: Debtors -->
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
                                <th class="p-3.5 text-center">จัดการคำขอ / ดูรูป & ลายเซ็น</th>
                            </tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <!-- 3. Section: Banking -->
            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white shadow-lg space-y-3">
                        <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                        <input type="number" id="bank-kbank-input" value="{{ bank_kbank }}" class="w-full px-3 py-2 bg-emerald-700 border border-emerald-500 rounded-xl text-xl font-black text-white">
                        <button onclick="updateBankBalance('kbank')" class="w-full py-1.5 bg-white text-emerald-800 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                    </div>
                    <div class="p-6 rounded-2xl bg-purple-700 text-white shadow-lg space-y-3">
                        <h4 class="font-bold text-lg">ธนาคารไทยพาณิชย์ (SCB)</h4>
                        <input type="number" id="bank-scb-input" value="{{ bank_scb }}" class="w-full px-3 py-2 bg-purple-800 border border-purple-600 rounded-xl text-xl font-black text-white">
                        <button onclick="updateBankBalance('scb')" class="w-full py-1.5 bg-white text-purple-900 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                    </div>
                    <div class="p-6 rounded-2xl bg-slate-800 text-white shadow-lg space-y-3">
                        <h4 class="font-bold text-lg">เงินสด (Cash)</h4>
                        <input type="number" id="bank-cash-input" value="{{ bank_cash }}" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-xl text-xl font-black text-white">
                        <button onclick="updateBankBalance('cash')" class="w-full py-1.5 bg-white text-slate-900 rounded-lg text-xs font-bold shadow">บันทึกยอดเงิน</button>
                    </div>
                </div>
            </div>

            <!-- 4. Section: Transactions -->
            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">บันทึกการชำระหนี้ / สลิปโอนเงิน</h3>
                    <p class="text-xs text-slate-500">บันทึกค่างวดและรับชำระดอกเบี้ยจากลูกค้า</p>
                </div>
            </div>

            <!-- 5. Section: Contracts -->
            <div id="section-contracts" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-file-contract text-indigo-600 mr-2"></i> จัดการสัญญาเงินกู้ดิจิทัล
                    </h3>
                    <p class="text-xs text-slate-500">ตรวจสอบเอกสารสัญญาเงินกู้ ลายเซ็นอิเล็กทรอนิกส์ และรูปถ่ายบัตรประชาชนของลูกหนี้</p>
                    <div class="p-4 bg-slate-50 border rounded-xl text-xs text-slate-600 flex justify-between items-center">
                        <div>
                            <p class="font-bold text-slate-800">สัญญา #541542 - หนึ่งฤดี นาน้อย</p>
                            <p class="text-[11px] text-slate-400">สถานะ: รอตรวจสอบลายเซ็นและบัตร</p>
                        </div>
                        <button onclick="openUserDetail(0)" class="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-bold">ตรวจสอบสัญญา</button>
                    </div>
                </div>
            </div>

            <!-- 6. Section: Annual Reports -->
            <div id="section-annual_reports" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <i class="fa-solid fa-chart-line text-teal-600 mr-2"></i> รายงานสรุปผลประกอบการประจำปี (2026)
                    </h3>
                    <p class="text-xs text-slate-500">สรุปยอดปล่อยกู้ กำไรสะสม และสถิติการเงินประจำปี</p>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="p-4 bg-teal-50 border border-teal-200 rounded-xl text-center">
                            <p class="text-xs font-bold text-teal-800">รายรับรวมทั้งปี</p>
                            <h4 class="text-xl font-black text-teal-950 mt-1">฿1,504,400</h4>
                        </div>
                        <div class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-center">
                            <p class="text-xs font-bold text-rose-800">รายจ่ายรวมทั้งปี</p>
                            <h4 class="text-xl font-black text-rose-950 mt-1">฿115,200</h4>
                        </div>
                        <div class="p-4 bg-purple-50 border border-purple-200 rounded-xl text-center">
                            <p class="text-xs font-bold text-purple-800">กำไรสุทธิทั้งปี</p>
                            <h4 class="text-xl font-black text-purple-950 mt-1">฿1,389,200</h4>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 7. Section: Settings (เพิ่มปุ่ม Backup CSV และ Upload CSV) -->
            <div id="section-settings" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
                    <h3 class="text-lg font-bold text-slate-800 border-b pb-3">⚙️ ตั้งค่าระบบหลังบ้าน (System Settings)</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- สำรองข้อมูล & นำเข้าข้อมูล -->
                        <div class="p-4 bg-purple-50/50 border border-purple-200 rounded-2xl space-y-3">
                            <h4 class="text-xs font-bold text-purple-900 uppercase"><i class="fa-solid fa-database mr-1"></i> สำรองข้อมูล & นำเข้าข้อมูล (Backup / Restore)</h4>
                            <p class="text-xs text-slate-500">ดาวน์โหลดฐานข้อมูลลูกหนี้ทั้งหมดเป็นไฟล์ CSV หรืออัปโหลดไฟล์เพื่อกู้คืนข้อมูล</p>
                            
                            <div class="pt-2 flex gap-3">
                                <a href="/export-csv" class="flex-1 py-2.5 bg-purple-600 text-white rounded-xl text-xs font-bold shadow hover:bg-purple-700 text-center flex items-center justify-center space-x-1.5">
                                    <i class="fa-solid fa-download"></i><span>สำรองข้อมูล (Export CSV)</span>
                                </a>
                            </div>

                            <form action="/import-csv" method="POST" enctype="multipart/form-data" class="pt-2 border-t border-purple-200 space-y-2">
                                <label class="block text-xs font-semibold text-slate-700">อัปโหลดไฟล์ CSV เพื่อกู้คืนข้อมูล</label>
                                <input type="file" name="csv_file" accept=".csv" required class="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-purple-200 file:text-purple-800">
                                <button type="submit" class="w-full py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow hover:bg-slate-900">
                                    <i class="fa-solid fa-upload mr-1"></i> นำเข้าข้อมูล (Import CSV)
                                </button>
                            </form>
                        </div>

                        <!-- LINE Notify & Config -->
                        <div class="p-4 bg-slate-50 border rounded-2xl space-y-3">
                            <h4 class="text-xs font-bold text-purple-900 uppercase">📱 การแจ้งเตือน LINE Notify</h4>
                            <input type="text" id="set-line" value="A1b2C3d4E5f6G7h8..." class="w-full px-3 py-2 bg-white border rounded-xl text-xs font-mono">
                            <button onclick="alert('บันทึกสำเร็จ!')" class="w-full py-2 bg-purple-600 text-white rounded-xl text-xs font-bold shadow">บันทึกการตั้งค่า</button>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- Modal 1: ดูรายละเอียดแฟ้มการเงิน -->
    <div id="folderDetailModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <h3 id="folder-modal-title" class="text-lg font-bold text-slate-800">รายละเอียดรายการ</h3>
                <button onclick="closeFolderModal()" class="px-3 py-1 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">✕ ปิด</button>
            </div>
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl mb-4 flex justify-between items-center">
                <span class="text-xs font-bold text-slate-500">ยอดรวมทั้งหมดในแฟ้มนี้:</span>
                <span id="folder-modal-total" class="text-xl font-black text-purple-900">0.00 บ.</span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-100 text-slate-600">
                        <tr>
                            <th class="p-2.5">วันที่/เวลา</th>
                            <th class="p-2.5">ชื่อ-เบอร์โทร</th>
                            <th class="p-2.5">รายละเอียดรายการ</th>
                            <th class="p-2.5 text-right">จำนวนเงิน</th>
                        </tr>
                    </thead>
                    <tbody id="folder-modal-table-body" class="divide-y divide-slate-100"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal 2: โปรไฟล์ลูกค้า & ตรวจสอบรูปภาพและลายเซ็น -->
    <div id="userDetailModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <button onclick="closeUserDetailModal()" class="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold">← ย้อนกลับ</button>
                <span id="detail-user-id" class="text-xs font-mono font-bold text-slate-400">#541542</span>
            </div>

            <div class="p-5 rounded-2xl bg-purple-50 border border-purple-100 space-y-2 mb-4">
                <div class="flex justify-between items-center">
                    <h3 id="detail-phone" class="text-xl font-black text-purple-900">0929237819</h3>
                    <a id="detail-fb-link" href="#" target="_blank" class="px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-bold"><i class="fa-brands fa-facebook"></i> Facebook</a>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-slate-700 pt-2 border-t border-purple-200/60">
                    <p>ชื่อ: <b id="detail-name">-</b></p>
                    <p>ธนาคาร: <b id="detail-bank">-</b> (<span id="detail-acc" class="font-mono">-</span>)</p>
                    <p>IP Address: <b id="detail-ip" class="font-mono text-purple-700">-</b></p>
                    <p>ประเภทชำระ: <b id="detail-term" class="text-purple-800 font-bold">-</b></p>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-3 mb-4">
                <div class="p-3 bg-purple-100/70 border border-purple-200 rounded-xl text-center">
                    <p class="text-[10px] font-bold text-purple-700 uppercase">เครดิตปัจจุบัน</p>
                    <h4 id="box-current-credit" class="text-sm font-black text-purple-900 mt-0.5">฿0</h4>
                </div>
                <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-center">
                    <p class="text-[10px] font-bold text-amber-700 uppercase">ยอดค้างเก่า</p>
                    <h4 id="box-old-debt" class="text-sm font-black text-amber-900 mt-0.5">฿0</h4>
                </div>
                <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-center">
                    <p class="text-[10px] font-bold text-emerald-700 uppercase">ยอดกู้ใหม่</p>
                    <h4 id="box-new-loan" class="text-sm font-black text-emerald-900 mt-0.5">฿0</h4>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="p-3 bg-slate-50 border rounded-xl text-center">
                    <p class="text-xs font-bold text-slate-700 mb-2">รูปถ่ายบัตรประชาชน</p>
                    <img id="detail-id-card-img" src="" alt="บัตรประชาชน" class="w-full h-28 object-cover rounded-lg border cursor-pointer hover:opacity-90" onclick="window.open(this.src)">
                    <p class="text-[10px] text-slate-400 mt-1">คลิกที่รูปเพื่อขยาย</p>
                </div>
                <div class="p-3 bg-slate-50 border rounded-xl text-center">
                    <p class="text-xs font-bold text-slate-700 mb-2">ลายเซ็นอิเล็กทรอนิกส์</p>
                    <img id="detail-signature-img" src="" alt="ลายเซ็น" class="w-full h-28 object-contain bg-white rounded-lg border cursor-pointer hover:opacity-90" onclick="window.open(this.src)">
                    <p class="text-[10px] text-slate-400 mt-1">คลิกที่รูปเพื่อขยาย</p>
                </div>
            </div>

            <div id="approve-btn-container" class="grid grid-cols-2 gap-3 mb-4"></div>
        </div>
    </div>

    <script>
        let debtorsList = {{ debtors | tojson }};
        let currentFilterStatus = 'ทั้งหมด';
        let currentEditIndex = -1;

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
        }

        function switchTab(tab) {
            ['dashboard', 'debtors', 'banking', 'transactions', 'contracts', 'annual_reports', 'settings'].forEach(s => {
                const sec = document.getElementById('section-' + s);
                const nav = document.getElementById('nav-' + s);
                if (sec) sec.classList.add('hidden');
                if (nav) nav.className = "w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-purple-200/80 hover:bg-purple-900/30";
            });

            const activeSec = document.getElementById('section-' + tab);
            const activeNav = document.getElementById('nav-' + tab);
            if (activeSec) activeSec.classList.remove('hidden');
            if (activeNav) activeNav.className = "w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs sidebar-item-active";

            const titles = {
                'dashboard': 'แดชบอร์ดหลัก',
                'debtors': 'รายชื่อลูกหนี้ & คำขอกู้',
                'banking': 'บัญชีธนาคาร & เงินสด',
                'transactions': 'บันทึกการชำระหนี้ / สลิป',
                'contracts': 'จัดการสัญญาเงินกู้ดิจิทัล',
                'annual_reports': 'รายงานสรุปผลประกอบการประจำปี',
                'settings': 'ตั้งค่าระบบหลังบ้าน'
            };
            document.getElementById('page-title').innerText = titles[tab];

            if (window.innerWidth < 768) {
                document.getElementById('sidebar').classList.add('-translate-x-full');
            }
        }

        function updateBankBalance(bankName) {
            const val = document.getElementById('bank-' + bankName + '-input').value;
            alert('อัปเดตยอดเงินเป็น ฿' + Number(val).toLocaleString() + ' เรียบร้อย!');
        }

        function openFolderDetail(folderType) {
            const modal = document.getElementById('folderDetailModal');
            const title = document.getElementById('folder-modal-title');
            const total = document.getElementById('folder-modal-total');
            const tbody = document.getElementById('folder-modal-table-body');

            if (folderType === 'new_investment') {
                title.innerText = "🔱 เงินลงทุนใหม่ (ประจำเดือนนี้)";
                total.innerText = "1,151,860.00 บ.";
                tbody.innerHTML = `
                    <tr><td class="p-2.5">29/10/2026</td><td class="p-2.5 font-bold">หนึ่งฤดี (0929237819)</td><td class="p-2.5">ปล่อยกู้เงินสด (รายวัน)</td><td class="p-2.5 text-right font-bold text-blue-600">1,000,000.00 บ.</td></tr>
                `;
            } else {
                title.innerText = "รายละเอียดแฟ้มข้อมูล";
                total.innerText = "670,541.19 บ.";
                tbody.innerHTML = `<tr><td colspan="4" class="p-3 text-center text-slate-400">แสดงรายการข้อมูลสะสม</td></tr>`;
            }
            modal.classList.remove('hidden');
        }

        function closeFolderModal() {
            document.getElementById('folderDetailModal').classList.add('hidden');
        }

        function renderDebtorsTable() {
            const tbody = document.getElementById('debtor-table-body');
            tbody.innerHTML = '';

            const keyword = (document.getElementById('searchInput') ? document.getElementById('searchInput').value : '').toLowerCase();
            const filtered = debtorsList.filter(item => {
                const matchKeyword = item.name.toLowerCase().includes(keyword) || item.phone.includes(keyword);
                const matchStatus = (currentFilterStatus === 'ทั้งหมด') || (item.status === currentFilterStatus);
                return matchKeyword && matchStatus;
            });

            filtered.forEach((item, index) => {
                let statusBadge = item.status === 'รออนุมัติ' 
                    ? `<span class="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-bold">รออนุมัติ</span>`
                    : `<span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">ปกติ</span>`;

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="p-3.5">
                            <button onclick="openUserDetail(${index})" class="text-left font-bold text-indigo-600 hover:underline block">
                                <span class="text-sm">${item.name}</span><br>
                                <span class="font-mono text-xs text-purple-700"><i class="fa-solid fa-phone mr-1"></i>${item.phone}</span>
                            </button>
                            <a href="${item.facebook}" target="_blank" class="text-[10px] text-blue-600 hover:underline mt-0.5 inline-block"><i class="fa-brands fa-facebook"></i> โปรไฟล์ FB</a>
                        </td>
                        <td class="p-3.5 text-xs text-slate-600 font-medium">${item.date}</td>
                        <td class="p-3.5 font-bold text-slate-900">฿${item.principal.toLocaleString()}</td>
                        <td class="p-3.5"><span class="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg font-bold text-xs">${item.payment_term || 'รายวัน'}</span></td>
                        <td class="p-3.5">${statusBadge}</td>
                        <td class="p-3.5 text-center">
                            <button onclick="openUserDetail(${index})" class="px-3 py-1.5 bg-purple-600 text-white rounded-xl text-xs font-bold shadow-sm hover:bg-purple-700">
                                <i class="fa-solid fa-eye mr-1"></i> ตรวจสอบสัญญา & รูป
                            </button>
                        </td>
                    </tr>
                `;
            });
        }

        function openUserDetail(index) {
            currentEditIndex = index;
            const item = debtorsList[index];
            document.getElementById('detail-user-id').innerText = item.id;
            document.getElementById('detail-phone').innerText = item.phone;
            document.getElementById('detail-name').innerText = item.name;
            document.getElementById('detail-bank').innerText = item.bank;
            document.getElementById('detail-acc').innerText = item.acc;
            document.getElementById('detail-ip').innerText = item.ip;
            document.getElementById('detail-total-loans').innerText = (item.total_loans || 1) + ' ครั้ง';
            document.getElementById('detail-term').innerText = item.payment_term || 'รายวัน';
            document.getElementById('detail-fb-link').href = item.facebook || '#';

            document.getElementById('box-current-credit').innerText = '฿' + (item.principal || 0).toLocaleString();
            document.getElementById('box-old-debt').innerText = '฿' + (item.old_debt || 0).toLocaleString();
            document.getElementById('box-new-loan').innerText = '฿' + (item.principal || 0).toLocaleString();

            document.getElementById('detail-id-card-img').src = item.idCardPhoto || 'https://via.placeholder.com/400';
            document.getElementById('detail-signature-img').src = item.signature || 'https://via.placeholder.com/400';

            const btnContainer = document.getElementById('approve-btn-container');
            if (item.status === 'รออนุมัติ') {
                btnContainer.innerHTML = `
                    <button onclick="approveLoan(${index})" class="py-2.5 bg-emerald-600 text-white font-bold text-xs rounded-xl shadow">อนุมัติวงเงิน</button>
                    <button onclick="rejectLoan(${index})" class="py-2.5 bg-rose-600 text-white font-bold text-xs rounded-xl shadow">ยกเลิก</button>
                `;
            } else {
                btnContainer.innerHTML = '';
            }
            document.getElementById('userDetailModal').classList.remove('hidden');
        }

        function approveLoan(index) {
            debtorsList[index].status = 'ปกติ';
            alert('อนุมัติวงเงินเรียบร้อย!');
            closeUserDetailModal();
            renderDebtorsTable();
            document.getElementById('bell-badge').style.display = 'none';
        }

        function rejectLoan(index) {
            debtorsList[index].status = 'ยกเลิก';
            alert('ยกเลิกคำขอเรียบร้อย!');
            closeUserDetailModal();
            renderDebtorsTable();
        }

        function closeUserDetailModal() { document.getElementById('userDetailModal').classList.add('hidden'); }
        function setFilterStatus(status) { currentFilterStatus = status; renderDebtorsTable(); }

        window.onload = function() {
            renderDebtorsTable();
            const ctx1 = document.getElementById('financeChart').getContext('2d');
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'ต.ค.'],
                    datasets: [
                        { label: 'รายรับ', data: [65000, 78000, 90000, 81000, 86000, 150000], backgroundColor: '#10b981' },
                        { label: 'รายจ่าย', data: [22000, 19000, 25000, 20000, 17000, 18200], backgroundColor: '#f43f5e' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            const ctx2 = document.getElementById('accountChart').getContext('2d');
            new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['กสิกรไทย', 'ไทยพาณิชย์', 'เงินสด'],
                    datasets: [{ data: [145000, 98500, 41000], backgroundColor: ['#059669', '#7c3aed', '#334155'] }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    </script>
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
            <p class="text-xs text-slate-500 mt-1">เลือกรูปแบบการชำระ กรอกข้อมูล และเซ็นสัญญาเพื่อส่งขอกู้</p>
        </div>

        <form action="/submit-application" method="POST" enctype="multipart/form-data" class="space-y-4" onsubmit="prepareSignature()">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ - นามสกุลจริง</label>
                    <input type="text" name="name" required placeholder="เช่น สมชาย ใจดี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เบอร์โทรศัพท์</label>
                    <input type="text" name="phone" required placeholder="0891234567" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-700">
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-brands fa-facebook text-blue-600 mr-1"></i> ลิงก์ Facebook</label>
                    <input type="url" name="facebook" required placeholder="https://www.facebook.com/your.profile" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm text-blue-700">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">รูปแบบการชำระหนี้</label>
                    <select name="payment_term" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold text-purple-900">
                        <option value="รายวัน">รายวัน (ทวงทุกวัน)</option>
                        <option value="รายวันเว้นอาทิตย์">รายวันเว้นอาทิตย์ (หยุดวันอาทิตย์)</option>
                        <option value="ราย 15 วัน">ราย 15 วัน (ชำระทุกกึ่งเดือน)</option>
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
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.strokeStyle = '#0f172a';
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX || e.touches[0].clientX) - rect.left;
            const y = (e.clientY || e.touches[0].clientY) - rect.top;
            ctx.lineTo(x, y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(x, y);
        }

        canvas.addEventListener('mousedown', startPosition);
        canvas.addEventListener('mouseup', finishedPosition);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('touchstart', startPosition);
        canvas.addEventListener('touchend', finishedPosition);
        canvas.addEventListener('touchmove', draw);

        function clearSignature() { ctx.clearRect(0, 0, canvas.width, canvas.height); }
        function prepareSignature() {
            document.getElementById('signature_data').value = canvas.toDataURL('image/png');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def admin_dashboard():
    return render_template_string(ADMIN_TEMPLATE, 
                                 debtors=debtors_database,
                                 bank_kbank=bank_accounts['kbank'],
                                 bank_scb=bank_accounts['scb'],
                                 bank_cash=bank_accounts['cash'])

@app.route('/apply')
def apply_form():
    return render_template_string(APPLY_TEMPLATE)

@app.route('/submit-application', methods=['POST'])
def submit_application():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    amount = float(request.form.get('amount') or 0)
    new_entry = {
        'id': f"#{len(debtors_database)+541540}",
        'username': request.form.get('phone'),
        'name': request.form.get('name'),
        'phone': request.form.get('phone'),
        'facebook': request.form.get('facebook'),
        'acc': request.form.get('account'),
        'bank': request.form.get('bank'),
        'principal': amount,
        'interest_type': 'ดอกคงที่',
        'payment_term': request.form.get('payment_term', 'รายวัน'),
        'daily_interest_rate': 0,
        'fixed_interest': 2000,
        'installment_amount': 0,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'ip': client_ip,
        'status': 'รออนุมัติ',
        'idCardPhoto': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
        'signature': 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=400',
        'total_loans': 1,
        'old_debt': 0,
        'remark': 'ยื่นกู้ผ่านเว็บใหม่ รอแอดมินตรวจสอบ'
    }
    debtors_database.insert(0, new_entry)
    return "<script>alert('ยื่นคำขอกู้เรียบร้อย!'); window.location.href='/apply';</script>"

# --- ฟังก์ชัน Export ข้อมูลเป็นไฟล์ CSV ---
@app.route('/export-csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    # เขียน Header ของ CSV
    writer.writerow(['ID', 'Name', 'Phone', 'Facebook', 'Bank', 'Account', 'Principal', 'PaymentTerm', 'Status', 'Date'])
    
    for d in debtors_database:
        writer.writerow([d['id'], d['name'], d['phone'], d['facebook'], d['bank'], d['acc'], d['principal'], d['payment_term'], d['status'], d['date']])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=debtors_backup.csv"}
    )

# --- ฟังก์ชัน Import ข้อมูลจากไฟล์ CSV ---
@app.route('/import-csv', methods=['POST'])
def import_csv():
    if 'csv_file' not in request.files:
        return "<script>alert('ไม่พบไฟล์ CSV'); window.location.href='/';</script>"
    
    file = request.files['csv_file']
    if file.filename == '':
        return "<script>alert('ยังไม่ได้เลือกไฟล์'); window.location.href='/';</script>"
    
    try:
        stream = io.TextIOWrapper(file.stream, encoding="utf-8")
        reader = csv.reader(stream)
        next(reader) # ข้าม Header
        
        for row in reader:
            if len(row) >= 10:
                new_d = {
                    'id': row[0],
                    'name': row[1],
                    'phone': row[2],
                    'facebook': row[3],
                    'bank': row[4],
                    'acc': row[5],
                    'principal': float(row[6] or 0),
                    'payment_term': row[7],
                    'status': row[8],
                    'date': row[9],
                    'ip': '127.0.0.1',
                    'idCardPhoto': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
                    'signature': 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=400',
                    'total_loans': 1,
                    'old_debt': 0,
                    'remark': 'นำเข้าจาก CSV'
                }
                debtors_database.append(new_d)
        
        return "<script>alert('นำเข้าข้อมูลจาก CSV สำเร็จ!'); window.location.href='/';</script>"
    except Exception as e:
        return f"<script>alert('เกิดข้อผิดพลาดในการนำเข้า: {str(e)}'); window.location.href='/';</script>"

if __name__ == '__main__':
    app.run(debug=True)
