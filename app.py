from flask import Flask, render_template_string, request
import os
from datetime import datetime

app = Flask(__name__)

# ฐานข้อมูลจำลอง (ในระบบจริงเชื่อมต่อ Supabase)
debtors_database = [
    {
        'id': '#541534',
        'username': '0812345678',
        'name': 'กิตติศักดิ์ มีพร้อม',
        'phone': '0812345678',
        'acc': '1234567890',
        'bank': 'KBANK',
        'principal': 15000,
        'interest': '5% (฿750)',
        'requested_amount': 15000,
        'total': 15750,
        'date': '29/10/2026 21:15',
        'ip': '182.52.12.45',
        'status': 'รออนุมัติ',
        'duedate': 'รอกำหนด',
        'idCardPhoto': 'id_card_new.jpg',
        'remark': 'ลูกค้ายื่นกู้ใหม่ รอแอดมินตรวจสอบ'
    },
    {
        'id': '#541532',
        'username': '0944948563',
        'name': 'น้ำทิพย์ ทิมทอง',
        'phone': '0944948563',
        'acc': '0173271891',
        'bank': 'KBANK',
        'principal': 50000,
        'interest': '5% (฿2,500)',
        'requested_amount': 50000,
        'total': 52500,
        'date': '29/10/2026 20:05',
        'ip': '2407:b1c0:dc2:c588:d1a',
        'status': 'ปกติ',
        'duedate': '5 พ.ย. 2026',
        'idCardPhoto': 'id_card_sample.jpg',
        'remark': 'อนุมัติเรียบร้อย ลูกค้าประวัติเดิม'
    },
    {
        'id': '#541533',
        'username': '0979388900',
        'name': 'นิภา อินทรี',
        'phone': '0979388900',
        'acc': '9412200232',
        'bank': 'SCB',
        'principal': 120000,
        'interest': '3% (฿3,600)',
        'requested_amount': 120000,
        'total': 123600,
        'date': '29/10/2026 19:41',
        'ip': '1.20.94.4',
        'status': 'เกินกำหนด',
        'duedate': '28 ต.ค. 2026',
        'idCardPhoto': 'id_card_sample2.jpg',
        'remark': 'ติดต่อนัดชำระปลายเดือน'
    }
]

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการลูกหนี้ & บัญชีการเงินขั้นสูง</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Google Fonts (Kanit & Inter) -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #f8fafc; }
        .sidebar-item-active {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(126, 34, 206, 0.2) 100%);
            border: 1px solid rgba(192, 132, 252, 0.4);
            color: #f3e8ff;
            box-shadow: 0 4px 20px -2px rgba(147, 51, 234, 0.25);
        }
        .sidebar-bg { background: linear-gradient(180deg, #18092e 0%, #0d061a 50%, #110726 100%); }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex">

    <!-- Sidebar -->
    <aside class="w-72 sidebar-bg text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl min-h-screen border-r border-purple-900/35">
        <div>
            <!-- Header / Logo -->
            <div class="p-6 pb-8 border-b border-purple-900/40">
                <div class="flex items-center space-x-3.5">
                    <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-violet-400 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg shadow-purple-900/50">
                        <i class="fa-solid fa-bold"></i>
                    </div>
                    <div>
                        <div class="flex items-center space-x-1.5">
                            <span class="text-2xl font-black text-white tracking-tight">BizFlow</span>
                            <span class="bg-gradient-to-r from-purple-400 to-indigo-300 text-slate-950 font-black text-xs px-2 py-0.5 rounded-md shadow-sm uppercase tracking-wider">PLUS</span>
                        </div>
                        <p class="text-xs text-purple-300/70 font-light mt-0.5">ระบบจัดการลูกหนี้ & บัญชี</p>
                    </div>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-4 space-y-1.5">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active">
                    <i class="fa-solid fa-chart-pie text-lg text-purple-400 w-6"></i>
                    <span>แดชบอร์ดการเงิน</span>
                </button>

                <button onclick="switchTab('debtors')" id="nav-debtors" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-hand-holding-dollar text-lg text-amber-400 w-6"></i>
                    <span>จัดการลูกหนี้ & ตรวจ IP</span>
                </button>

                <button onclick="switchTab('transactions')" id="nav-transactions" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-receipt text-lg text-emerald-400 w-6"></i>
                    <span>บันทึกรายรับ-รายจ่าย</span>
                </button>

                <button onclick="switchTab('banking')" id="nav-banking" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-building-columns text-lg text-sky-400 w-6"></i>
                    <span>บัญชีธนาคาร & เงินสด</span>
                </button>

                <a href="/apply" target="_blank" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-emerald-300 hover:bg-emerald-950/40 border border-emerald-500/30 mt-4">
                    <i class="fa-solid fa-globe text-lg text-emerald-400 w-6"></i>
                    <span>🔗 เปิดหน้าบ้าน (ให้ลูกค้ากรอกกู้)</span>
                </a>
            </nav>
        </div>

        <!-- Bottom Widgets -->
        <div class="p-4 space-y-4">
            <div class="p-3.5 rounded-2xl bg-purple-950/40 border border-purple-800/40 backdrop-blur-md">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold text-purple-200">Supabase Status</span>
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        Connected
                    </span>
                </div>
                <p class="text-[11px] text-purple-300/60 mt-1 truncate">db.pdpeqsubrbmdjxgmtjpy...</p>
            </div>

            <div class="pt-3 border-t border-purple-900/40 flex items-center justify-between px-2">
                <div class="flex items-center space-x-3">
                    <div class="w-9 h-9 rounded-full bg-purple-800/60 border border-purple-500/30 flex items-center justify-center text-xs font-bold text-purple-200">NU</div>
                    <div>
                        <p class="text-xs font-bold text-slate-100">nuengdi7819-ux</p>
                        <p class="text-[10px] text-purple-300/60">ผู้ดูแลระบบ</p>
                    </div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50">
        <!-- Top Bar -->
        <header class="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10 px-8 py-4 flex items-center justify-between shadow-sm">
            <div>
                <h2 id="page-title" class="text-xl font-bold text-slate-800">แดชบอร์ดการเงิน</h2>
            </div>
            <div class="flex items-center space-x-3">
                <a href="/apply" target="_blank" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium text-sm shadow-md shadow-purple-500/20 flex items-center space-x-2">
                    <i class="fa-solid fa-external-link-alt text-xs"></i>
                    <span>เปิดหน้าบ้าน (ให้ลูกค้ายื่นกู้)</span>
                </a>
            </div>
        </header>

        <!-- Dynamic Content Sections -->
        <div class="p-8">

            <!-- 1. Section: Dashboard -->
            <div id="section-dashboard" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div class="p-6 rounded-2xl bg-gradient-to-br from-amber-500/10 via-white to-amber-500/5 border-2 border-amber-400/40 shadow-lg relative overflow-hidden">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-amber-700 uppercase">ยอดปล่อยทุน (ลูกหนี้คงค้าง)</span>
                                <h3 class="text-2xl font-black text-slate-900 mt-2">฿284,500</h3>
                            </div>
                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-orange-400 text-white flex items-center justify-center">
                                <i class="fa-solid fa-hand-holding-dollar text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-white to-emerald-500/5 border-2 border-emerald-400/40 shadow-lg relative overflow-hidden">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-emerald-700 uppercase">รายรับเดือนนี้</span>
                                <h3 class="text-2xl font-black text-slate-900 mt-2">฿92,400</h3>
                            </div>
                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white flex items-center justify-center">
                                <i class="fa-solid fa-arrow-down-left text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-gradient-to-br from-rose-500/10 via-white to-rose-500/5 border-2 border-rose-400/40 shadow-lg relative overflow-hidden">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-rose-700 uppercase">รายจ่ายเดือนนี้</span>
                                <h3 class="text-2xl font-black text-slate-900 mt-2">฿18,200</h3>
                            </div>
                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-pink-500 text-white flex items-center justify-center">
                                <i class="fa-solid fa-arrow-up-right text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="p-6 rounded-2xl bg-gradient-to-br from-purple-600/10 via-white to-indigo-600/5 border-2 border-purple-400/40 shadow-lg relative overflow-hidden">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-purple-700 uppercase">เงินสด/ธนาคารคงเหลือ</span>
                                <h3 class="text-2xl font-black text-slate-900 mt-2">฿284,500</h3>
                            </div>
                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center">
                                <i class="fa-solid fa-wallet text-xl"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                    <div class="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สรุปรายรับ - รายจ่าย (ปี 2026)</h4>
                        <div class="h-64"><canvas id="financeChart"></canvas></div>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สัดส่วนบัญชีเงินฝาก</h4>
                        <div class="h-64 flex items-center justify-center"><canvas id="accountChart"></canvas></div>
                    </div>
                </div>
            </div>

            <!-- 2. Section: Debtors & IP Audit -->
            <div id="section-debtors" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                        <div>
                            <h3 class="text-lg font-bold text-slate-800">รายชื่อลูกหนี้ & ประวัติการยื่นกู้</h3>
                            <p class="text-xs text-slate-500">คลิกปุ่มกรองด้านล่างเพื่อเลือกดูเฉพาะยอดที่ **รออนุมัติ** หรือค้นหาตามเบอร์โทร/ชื่อ</p>
                        </div>
                        <div class="flex items-center space-x-3">
                            <input type="text" id="searchInput" oninput="filterDebtors()" placeholder="ค้นหาด้วยชื่อ หรือ เบอร์โทร..." class="w-64 px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                        </div>
                    </div>

                    <!-- ปุ่มกรองตัวเลือกตามสถานะ (Quick Status Filter) -->
                    <div class="flex flex-wrap items-center gap-2 mb-6 pb-4 border-b border-slate-100">
                        <button onclick="setFilterStatus('ทั้งหมด')" id="filter-all" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-purple-600 text-white shadow-sm">
                            ทั้งหมด
                        </button>
                        <button onclick="setFilterStatus('รออนุมัติ')" id="filter-pending" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-amber-50 text-amber-800 border border-amber-300 hover:bg-amber-100 flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                            <span>รออนุมัติ</span>
                            <span id="pending-count" class="px-1.5 py-0.2 bg-amber-200/80 rounded-md text-[10px] font-black">0</span>
                        </button>
                        <button onclick="setFilterStatus('ปกติ')" id="filter-approved" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-600 hover:bg-slate-200">
                            อนุมัติแล้ว / ปกติ
                        </button>
                        <button onclick="setFilterStatus('เกินกำหนด')" id="filter-overdue" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-600 hover:bg-slate-200">
                            เกินกำหนด
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-500 rounded-xl">
                                <tr>
                                    <th class="p-3.5 font-semibold">ชื่อผู้ใช้ (กดเพื่อเช็ค)</th>
                                    <th class="p-3.5 font-semibold">ชื่อ-นามสกุล</th>
                                    <th class="p-3.5 font-semibold">เลขบัญชี / ธนาคาร</th>
                                    <th class="p-3.5 font-semibold">ยอดขอกู้</th>
                                    <th class="p-3.5 font-semibold">IP Address</th>
                                    <th class="p-3.5 font-semibold">สถานะ</th>
                                    <th class="p-3.5 font-semibold text-center">จัดการอนุมัติ / เช็คโปรไฟล์</th>
                                </tr>
                            </thead>
                            <tbody id="debtor-table-body" class="divide-y divide-slate-100">
                                <!-- Data rendered via JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 3. Section: Transactions -->
            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">บันทึกรายรับ - รายจ่าย</h3>
                    <p class="text-xs text-slate-500 mb-4">บันทึกธุรกรรมการเงินและดอกเบี้ยเข้าออกจากระบบ</p>
                </div>
            </div>

            <!-- 4. Section: Banking -->
            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white shadow-lg">
                        <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                        <h3 class="text-3xl font-black mt-4">฿145,000</h3>
                    </div>
                    <div class="p-6 rounded-2xl bg-purple-700 text-white shadow-lg">
                        <h4 class="font-bold text-lg">ธนาคารไทยพาณิชย์ (SCB)</h4>
                        <h3 class="text-3xl font-black mt-4">฿98,500</h3>
                    </div>
                    <div class="p-6 rounded-2xl bg-slate-800 text-white shadow-lg">
                        <h4 class="font-bold text-lg">เงินสด (Cash)</h4>
                        <h3 class="text-3xl font-black mt-4">฿41,000</h3>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- User Detail Modal -->
    <div id="userDetailModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <button onclick="closeUserDetailModal()" class="flex items-center space-x-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold">
                    <i class="fa-solid fa-arrow-left"></i> <span>ย้อนกลับ</span>
                </button>
                <span id="detail-user-id" class="text-xs font-mono font-bold text-slate-400">#541532</span>
            </div>

            <div id="detail-card-header" class="p-6 rounded-2xl space-y-3 mb-6 transition-all">
                <div class="flex items-center justify-between">
                    <h3 id="detail-phone" class="text-2xl font-black">0944948563</h3>
                    <span id="detail-status-badge" class="px-3 py-1 rounded-full text-xs font-bold shadow-sm">-</span>
                </div>
                
                <div class="grid grid-cols-2 gap-y-2 text-sm pt-2 border-t border-slate-200/50">
                    <div><p class="text-xs opacity-75">ชื่อ-สกุล:</p><p id="detail-name" class="font-bold">-</p></div>
                    <div><p class="text-xs opacity-75">ธนาคาร:</p><p id="detail-bank" class="font-bold">-</p></div>
                    <div><p class="text-xs opacity-75">เลขบัญชี:</p><p id="detail-account" class="font-mono font-bold">-</p></div>
                    <div><p class="text-xs opacity-75">วัน/เวลาที่ยื่น:</p><p id="detail-date" class="font-medium">-</p></div>
                    <div class="col-span-2 mt-1">
                        <p class="text-xs opacity-75">IP Address ที่บันทึกได้:</p>
                        <p id="detail-ip" class="font-mono font-bold text-purple-700 bg-purple-100/90 px-2.5 py-1 rounded w-max text-xs mt-0.5 shadow-sm">-</p>
                    </div>
                </div>
            </div>

            <div class="mb-6">
                <h4 class="text-sm font-bold text-slate-800 mb-2.5 flex items-center">
                    <i class="fa-solid fa-id-card text-purple-600 mr-2"></i> รูปถ่ายคู่บัตรประชาชน / เอกสารแนบ
                </h4>
                <div id="detail-image-box" class="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-center">
                    <p class="text-xs text-slate-400 py-2">ไม่มีไฟล์ภาพแนบ</p>
                </div>
            </div>

            <!-- ปุ่มกกดอนุมัติเคส -->
            <div id="approve-btn-container" class="mb-4"></div>

            <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                <h4 class="text-xs font-bold text-purple-900 mb-1">หมายเหตุ</h4>
                <p id="detail-remark" class="text-sm text-slate-600">ไม่มีหมายเหตุ</p>
            </div>
        </div>
    </div>

    <script>
        let debtorsList = {{ debtors | tojson }};
        let currentFilterStatus = 'ทั้งหมด';

        function renderDebtorsTable() {
            const tbody = document.getElementById('debtor-table-body');
            tbody.innerHTML = '';

            // คำนวณจำนวนเคสรออนุมัติ
            const pendingCount = debtorsList.filter(item => item.status === 'รออนุมัติ').length;
            document.getElementById('pending-count').innerText = pendingCount;

            const keyword = document.getElementById('searchInput').value.toLowerCase();
            const filtered = debtorsList.filter(item => {
                const matchesKeyword = item.name.toLowerCase().includes(keyword) || item.phone.includes(keyword);
                const matchesStatus = (currentFilterStatus === 'ทั้งหมด') || (item.status === currentFilterStatus);
                return matchesKeyword && matchesStatus;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400 font-medium">ไม่พบรายการลูกหนี้ในสถานะนี้</td></tr>`;
                return;
            }

            filtered.forEach((item) => {
                const originalIndex = debtorsList.indexOf(item);
                
                // แยกสี Badge ให้ชัดเจน
                let statusBadge = '';
                if (item.status === 'รออนุมัติ') {
                    statusBadge = `<span class="px-3 py-1 bg-amber-100 text-amber-800 border border-amber-300 rounded-full text-xs font-bold inline-flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>รออนุมัติ</span>`;
                } else if (item.status === 'ปกติ' || item.status === 'อนุมัติแล้ว') {
                    statusBadge = `<span class="px-3 py-1 bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-full text-xs font-bold">ปกติ (อนุมัติแล้ว)</span>`;
                } else {
                    statusBadge = `<span class="px-3 py-1 bg-rose-100 text-rose-800 border border-rose-300 rounded-full text-xs font-bold">เกินกำหนด</span>`;
                }

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3.5">
                            <button onclick="openUserDetail(${originalIndex})" class="font-bold text-indigo-600 hover:text-indigo-800 hover:underline font-mono">
                                ${item.phone}
                            </button>
                        </td>
                        <td class="p-3.5 font-bold text-slate-800">${item.name}</td>
                        <td class="p-3.5"><span class="font-semibold text-slate-700">${item.bank}</span> <br><span class="font-mono text-xs text-slate-500">${item.acc}</span></td>
                        <td class="p-3.5 font-bold text-slate-900">฿${item.requested_amount.toLocaleString()}</td>
                        <td class="p-3.5 font-mono text-xs text-purple-700 font-bold">${item.ip}</td>
                        <td class="p-3.5">${statusBadge}</td>
                        <td class="p-3.5 text-center">
                            <button onclick="openUserDetail(${originalIndex})" class="px-3 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 rounded-xl text-xs font-bold transition-all shadow-sm">
                                <i class="fa-solid fa-magnifying-glass mr-1"></i> ตรวจสอบ / อนุมัติ
                            </button>
                        </td>
                    </tr>
                `;
            });
        }

        function setFilterStatus(status) {
            currentFilterStatus = status;
            
            // ปรับแต่งสไตล์ปุ่มกรอง
            const btnMap = { 'ทั้งหมด': 'filter-all', 'รออนุมัติ': 'filter-pending', 'ปกติ': 'filter-approved', 'เกินกำหนด': 'filter-overdue' };
            Object.keys(btnMap).forEach(key => {
                const btn = document.getElementById(btnMap[key]);
                if (key === status) {
                    btn.className = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-purple-600 text-white shadow-sm";
                } else {
                    btn.className = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200";
                }
            });

            renderDebtorsTable();
        }

        function openUserDetail(index) {
            const item = debtorsList[index];
            document.getElementById('detail-user-id').innerText = item.id;
            document.getElementById('detail-phone').innerText = item.phone;
            document.getElementById('detail-name').innerText = item.name;
            document.getElementById('detail-bank').innerText = item.bank;
            document.getElementById('detail-account').innerText = item.acc;
            document.getElementById('detail-date').innerText = item.date;
            document.getElementById('detail-ip').innerText = item.ip;
            document.getElementById('detail-remark').innerText = item.remark || 'ไม่มีหมายเหตุ';

            const cardHeader = document.getElementById('detail-card-header');
            const badge = document.getElementById('detail-status-badge');
            const btnContainer = document.getElementById('approve-btn-container');

            if (item.status === 'รออนุมัติ') {
                cardHeader.className = "p-6 rounded-2xl bg-amber-50 border border-amber-200/80 text-amber-950 space-y-3 mb-6";
                badge.className = "px-3 py-1 bg-amber-200 text-amber-900 font-bold text-xs";
                badge.innerText = "รออนุมัติ";
                btnContainer.innerHTML = `<button onclick="approveLoan(${index})" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-xl shadow-md transition-all"><i class="fa-solid fa-check-circle mr-1"></i> กดอนุมัติวงเงินกู้นี้</button>`;
            } else {
                cardHeader.className = "p-6 rounded-2xl bg-emerald-50 border border-emerald-200/80 text-emerald-950 space-y-3 mb-6";
                badge.className = "px-3 py-1 bg-emerald-200 text-emerald-900 font-bold text-xs";
                badge.innerText = item.status;
                btnContainer.innerHTML = '';
            }

            const imgBox = document.getElementById('detail-image-box');
            if (item.idCardPhoto) {
                imgBox.innerHTML = `<div class="text-center"><p class="text-xs text-emerald-600 font-bold mb-2"><i class="fa-solid fa-check-circle"></i> มีไฟล์แนบบัตรประชาชน</p><span class="px-3 py-1 bg-slate-200 text-slate-700 text-xs font-mono rounded-lg">${item.idCardPhoto}</span></div>`;
            } else {
                imgBox.innerHTML = `<p class="text-xs text-slate-400 py-2">ไม่มีไฟล์รูปแนบบัตรประชาชน</p>`;
            }

            document.getElementById('userDetailModal').classList.remove('hidden');
        }

        function approveLoan(index) {
            debtorsList[index].status = 'ปกติ';
            debtorsList[index].remark = 'อนุมัติวงเงินโดยแอดมินแล้ว';
            alert('ทำการอนุมัติรายการกู้เงินสำเร็จ!');
            closeUserDetailModal();
            renderDebtorsTable();
        }

        function closeUserDetailModal() {
            document.getElementById('userDetailModal').classList.add('hidden');
        }

        function filterDebtors() {
            renderDebtorsTable();
        }

        function switchTab(tab) {
            ['dashboard', 'debtors', 'transactions', 'banking'].forEach(s => {
                const sec = document.getElementById('section-' + s);
                const nav = document.getElementById('nav-' + s);
                if (sec) sec.classList.add('hidden');
                if (nav) nav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white";
            });

            const activeSec = document.getElementById('section-' + tab);
            const activeNav = document.getElementById('nav-' + tab);
            if (activeSec) activeSec.classList.remove('hidden');
            if (activeNav) activeNav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active";

            const titles = {
                'dashboard': 'แดชบอร์ดการเงิน',
                'debtors': 'จัดการลูกหนี้ & ตรวจสอบ IP',
                'transactions': 'บันทึกรายรับ-รายจ่าย',
                'banking': 'บัญชีธนาคาร & เงินสด'
            };
            document.getElementById('page-title').innerText = titles[tab];
        }

        window.onload = function() {
            renderDebtorsTable();
            const ctx1 = document.getElementById('financeChart').getContext('2d');
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.'],
                    datasets: [
                        { label: 'รายรับ', data: [65000, 78000, 90000, 81000, 86000, 92400], backgroundColor: '#10b981' },
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
    <title>BizFlow+ - ยื่นคำขอกู้เงินและทำสัญญาออนไลน์</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; } </style>
</head>
<body class="py-12 px-4 flex items-center justify-center">
    <div class="max-w-2xl w-full bg-white rounded-3xl shadow-2xl p-8 border border-purple-100">
        <div class="text-center mb-8">
            <h1 class="text-2xl font-black text-slate-900">แบบฟอร์มยื่นกู้ & ทำสัญญาออนไลน์</h1>
            <p class="text-xs text-slate-500 mt-1">กรอกข้อมูลส่วนตัว แนบรูปบัตร และเซ็นสัญญาเพื่อส่งขอกู้</p>
        </div>

        <form action="/submit-application" method="POST" enctype="multipart/form-data" class="space-y-4">
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
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ธนาคารรับเงิน</label>
                    <input type="text" name="bank" required placeholder="เช่น กสิกรไทย" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เลขที่บัญชี</label>
                    <input type="text" name="account" required placeholder="เลขบัญชี" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-mono">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">ขอกู้วงเงิน (บาท)</label>
                <input type="number" name="amount" required placeholder="เช่น 10000" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm font-bold">
            </div>
            <div class="p-4 bg-slate-50 border-2 border-dashed border-slate-300 rounded-2xl">
                <label class="block text-xs font-bold text-slate-700 mb-1">อัปโหลดรูปถ่ายคู่บัตรประชาชน</label>
                <input type="file" name="id_card_photo" accept="image/*" required class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-100 file:text-purple-700">
            </div>
            <button type="submit" class="w-full py-3.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow-lg mt-4">
                ยื่นคำขอกู้เงินและส่งข้อมูล
            </button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def admin_dashboard():
    return render_template_string(ADMIN_TEMPLATE, debtors=debtors_database)

@app.route('/apply')
def apply_form():
    return render_template_string(APPLY_TEMPLATE)

@app.route('/submit-application', methods=['POST'])
def submit_application():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    name = request.form.get('name')
    phone = request.form.get('phone')
    bank = request.form.get('bank')
    account = request.form.get('account')
    amount = float(request.form.get('amount') or 0)
    id_card_photo = request.files.get('id_card_photo')
    photo_filename = id_card_photo.filename if id_card_photo else 'uploaded_photo.jpg'

    new_entry = {
        'id': f"#{len(debtors_database)+541540}",
        'username': phone,
        'name': name,
        'phone': phone,
        'acc': account,
        'bank': bank,
        'principal': amount,
        'interest': '5% (คำนวณอัตโนมัติ)',
        'requested_amount': amount,
        'total': amount * 1.05,
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'ip': client_ip,
        'status': 'รออนุมัติ',
        'duedate': 'รอกำหนด',
        'idCardPhoto': photo_filename,
        'remark': 'ลูกค้ายื่นกู้ใหม่ รอแอดมินอนุมัติ'
    }
    debtors_database.insert(0, new_entry)
    return "<script>alert('ยื่นคำขอกู้เรียบร้อยแล้ว!'); window.location.href='/';</script>"

if __name__ == '__main__':
    app.run(debug=True)
