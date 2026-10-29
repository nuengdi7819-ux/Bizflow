from flask import Flask, render_template_string, request
import os
from datetime import datetime

app = Flask(__name__)

# ฐานข้อมูลจำลอง
debtors_database = [
    {
        'id': '#541534',
        'username': '0812345678',
        'name': 'กิตติศักดิ์ มีพร้อม',
        'phone': '0812345678',
        'facebook': 'https://facebook.com/kittisak',
        'acc': '1234567890',
        'bank': 'KBANK',
        'principal': 15000,
        'interest_type': 'ดอกลอย',
        'daily_interest_rate': 100,
        'fixed_interest': 0,
        'installment_amount': 0,
        'start_date': '2026-10-20',
        'date': '29/10/2026 21:15',
        'ip': '182.52.12.45',
        'status': 'รออนุมัติ',
        'idCardPhoto': 'id_card_new.jpg',
        'signature': 'signature_sample.png',
        'remark': 'ลูกค้ายื่นกู้ใหม่ รอแอดมินติดต่อ'
    }
]

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการลูกหนี้ & คำนวณดอกเบี้ย</title>
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
    <div class="md:hidden bg-[#18092e] text-white p-4 flex items-center justify-between shadow-md">
        <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-xl bg-purple-600 flex items-center justify-center font-black">B</div>
            <span class="font-bold text-lg">BizFlow <span class="text-xs bg-purple-500 px-1.5 py-0.5 rounded">PLUS</span></span>
        </div>
        <button onclick="toggleSidebar()" class="text-purple-300 hover:text-white text-xl p-2">
            <i class="fa-solid fa-bars"></i>
        </button>
    </div>

    <!-- Sidebar (Responsive Drawer) -->
    <aside id="sidebar" class="w-72 sidebar-bg text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl h-screen fixed md:static inset-y-0 left-0 z-50 transform -translate-x-full md:translate-x-0 transition-transform duration-300 border-r border-purple-900/35">
        <div>
            <div class="p-6 pb-8 border-b border-purple-900/40 flex items-center justify-between">
                <div class="flex items-center space-x-3.5">
                    <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 to-violet-400 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg">B</div>
                    <div>
                        <span class="text-2xl font-black text-white">BizFlow <span class="bg-purple-400 text-slate-950 text-xs px-2 py-0.5 rounded font-bold">PLUS</span></span>
                        <p class="text-xs text-purple-300/70">ระบบจัดการลูกหนี้</p>
                    </div>
                </div>
                <button onclick="toggleSidebar()" class="md:hidden text-purple-300 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <nav class="p-4 space-y-1.5">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm text-purple-200/80 hover:bg-purple-900/30">
                    <i class="fa-solid fa-chart-pie text-lg text-purple-400 w-6"></i><span>แดชบอร์ดการเงิน</span>
                </button>
                <button onclick="switchTab('debtors')" id="nav-debtors" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm sidebar-item-active">
                    <i class="fa-solid fa-hand-holding-dollar text-lg text-amber-400 w-6"></i><span>จัดการลูกหนี้ & ดอกเบี้ย</span>
                </button>
                <a href="/apply" target="_blank" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm text-emerald-300 hover:bg-emerald-950/40 border border-emerald-500/30 mt-4">
                    <i class="fa-solid fa-globe text-lg text-emerald-400 w-6"></i><span>🔗 หน้าบ้านยื่นกู้ (ลูกค้า)</span>
                </a>
            </nav>
        </div>
        <div class="p-4 border-t border-purple-900/40 text-xs text-purple-300/60">
            สถานะ: ออนไลน์ (มือถือรองรับ)
        </div>
    </aside>

    <!-- Main Area -->
    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50 w-full">
        <header class="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 md:px-8 py-4 flex items-center justify-between shadow-sm">
            <h2 id="page-title" class="text-lg md:text-xl font-bold text-slate-800">จัดการลูกหนี้ & ดอกเบี้ย</h2>
            <a href="/apply" target="_blank" class="px-3.5 py-2 bg-purple-600 text-white rounded-xl font-medium text-xs md:text-sm shadow-md whitespace-nowrap">
                <i class="fa-solid fa-external-link-alt mr-1"></i> หน้าบ้านขอกู้
            </a>
        </header>

        <div class="p-4 md:p-8">
            <div id="section-debtors" class="space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-4 md:p-6 shadow-sm overflow-x-auto">
                    <div class="flex flex-wrap items-center gap-2 mb-6 pb-4 border-b border-slate-100">
                        <button onclick="setFilterStatus('ทั้งหมด')" id="filter-all" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white">ทั้งหมด</button>
                        <button onclick="setFilterStatus('รออนุมัติ')" id="filter-pending" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-amber-50 text-amber-800 border border-amber-300">รออนุมัติ</button>
                        <button onclick="setFilterStatus('ปกติ')" id="filter-approved" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-600">อนุมัติแล้ว</button>
                    </div>

                    <table class="w-full text-left text-sm min-w-[700px]">
                        <thead class="bg-slate-50 text-slate-500">
                            <tr>
                                <th class="p-3.5">เบอร์โทร / Facebook</th>
                                <th class="p-3.5">ชื่อ-นามสกุล</th>
                                <th class="p-3.5">เงินต้นกู้</th>
                                <th class="p-3.5">ประเภทดอกเบี้ย</th>
                                <th class="p-3.5">ดอกเบี้ยสะสมปัจจุบัน</th>
                                <th class="p-3.5">สถานะ</th>
                                <th class="p-3.5 text-center">จัดการคำขอ</th>
                            </tr>
                        </thead>
                        <tbody id="debtor-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <!-- Modal -->
    <div id="userDetailModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <button onclick="closeUserDetailModal()" class="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold">← ย้อนกลับ</button>
                <span id="detail-user-id" class="text-xs font-mono font-bold text-slate-400">#541534</span>
            </div>

            <div class="p-5 rounded-2xl bg-purple-50 border border-purple-100 space-y-2 mb-4">
                <div class="flex justify-between items-center">
                    <h3 id="detail-phone" class="text-xl font-black text-purple-900">0812345678</h3>
                    <a id="detail-fb-link" href="#" target="_blank" class="px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-bold"><i class="fa-brands fa-facebook"></i> Facebook</a>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-slate-700 pt-2 border-t border-purple-200/60">
                    <p>ชื่อ: <b id="detail-name">-</b></p>
                    <p>ธนาคาร: <b id="detail-bank">-</b> (<span id="detail-acc" class="font-mono">-</span>)</p>
                    <p>IP Address: <b id="detail-ip" class="font-mono text-purple-700">-</b></p>
                    <p>เงินต้นกู้: <b id="detail-principal" class="text-slate-900 font-bold text-sm">-</b></p>
                </div>
            </div>

            <div class="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3 mb-4">
                <h4 class="text-xs font-bold text-purple-900 uppercase">⚙️ กำหนดประเภทดอกเบี้ย</h4>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">เลือกประเภทดอกเบี้ย</label>
                    <select id="edit-interest-type" onchange="toggleInterestFields()" class="w-full px-3 py-2 bg-white border rounded-xl text-xs font-bold">
                        <option value="ดอกลอย">1. ดอกลอย (คิดดอกสะสมรายวัน)</option>
                        <option value="ดอกคงที่">2. ดอกคงที่ (แอดมินแก้ไขได้)</option>
                        <option value="จบต้นดอก">3. จบต้นดอก (แบ่งจ่ายเป็นงวด)</option>
                    </select>
                </div>

                <div id="field-daily" class="space-y-1">
                    <label class="block text-xs font-semibold text-slate-600">ดอกเบี้ยลอยต่อวัน (บาท/วัน)</label>
                    <input type="number" id="edit-daily-rate" placeholder="เช่น 100" class="w-full px-3 py-2 bg-white border rounded-xl text-xs font-bold text-amber-700">
                </div>
                <div id="field-fixed" class="space-y-1 hidden">
                    <label class="block text-xs font-semibold text-slate-600">จำนวนดอกเบี้ยคงที่ทั้งหมด (บาท)</label>
                    <input type="number" id="edit-fixed-rate" placeholder="เช่น 2000" class="w-full px-3 py-2 bg-white border rounded-xl text-xs font-bold text-emerald-700">
                </div>
                <div id="field-installment" class="space-y-1 hidden">
                    <label class="block text-xs font-semibold text-slate-600">ยอดผ่อนชำระต่องวด (บาท/งวด)</label>
                    <input type="number" id="edit-installment-amount" placeholder="เช่น 500" class="w-full px-3 py-2 bg-white border rounded-xl text-xs font-bold text-indigo-700">
                </div>

                <button onclick="saveInterestSettings()" class="w-full py-2 bg-purple-600 text-white rounded-xl text-xs font-bold shadow">บันทึกดอกเบี้ย</button>
            </div>

            <div id="approve-btn-container" class="grid grid-cols-2 gap-3 mb-4"></div>
        </div>
    </div>

    <script>
        let debtorsList = {{ debtors | tojson }};
        let currentFilterStatus = 'ทั้งหมด';
        let currentEditIndex = -1;

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('-translate-x-full');
        }

        function calculateDaysPassed(startDateStr) {
            if (!startDateStr) return 0;
            const start = new Date(startDateStr);
            const today = new Date();
            const diffTime = Math.abs(today - start);
            return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        }

        function renderDebtorsTable() {
            const tbody = document.getElementById('debtor-table-body');
            tbody.innerHTML = '';

            const filtered = debtorsList.filter(item => currentFilterStatus === 'ทั้งหมด' || item.status === currentFilterStatus);

            filtered.forEach((item, index) => {
                const daysPassed = calculateDaysPassed(item.start_date || '2026-10-25');
                let interestDisplay = '';

                if (item.interest_type === 'ดอกลอย') {
                    const accumulated = daysPassed * (item.daily_interest_rate || 0);
                    interestDisplay = `<span class="text-amber-700 font-bold">฿${accumulated.toLocaleString()}</span> <span class="text-[10px] text-slate-400">(${daysPassed} วัน)</span>`;
                } else if (item.interest_type === 'ดอกคงที่') {
                    interestDisplay = `<span class="text-emerald-700 font-bold">฿${(item.fixed_interest || 0).toLocaleString()}</span>`;
                } else if (item.interest_type === 'จบต้นดอก') {
                    interestDisplay = `<span class="text-indigo-700 font-bold">งวดละ ฿${(item.installment_amount || 0).toLocaleString()}</span>`;
                } else {
                    interestDisplay = `<span class="text-slate-400 text-xs">รอตั้งค่า</span>`;
                }

                let statusBadge = item.status === 'รออนุมัติ' 
                    ? `<span class="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-bold">รออนุมัติ</span>`
                    : `<span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">ปกติ</span>`;

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="p-3.5">
                            <p class="font-mono font-bold text-indigo-600">${item.phone}</p>
                            <a href="${item.facebook}" target="_blank" class="text-[11px] text-blue-600 hover:underline"><i class="fa-brands fa-facebook"></i> FB</a>
                        </td>
                        <td class="p-3.5 font-bold text-slate-800">${item.name}</td>
                        <td class="p-3.5 font-bold text-slate-900">฿${item.principal.toLocaleString()}</td>
                        <td class="p-3.5"><span class="px-2 py-0.5 bg-slate-100 text-slate-700 rounded font-semibold text-xs">${item.interest_type || 'ยังไม่กำหนด'}</span></td>
                        <td class="p-3.5">${interestDisplay}</td>
                        <td class="p-3.5">${statusBadge}</td>
                        <td class="p-3.5 text-center">
                            <button onclick="openUserDetail(${index})" class="px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-xl text-xs font-bold whitespace-nowrap">
                                จัดการ
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
            document.getElementById('detail-principal').innerText = '฿' + item.principal.toLocaleString();
            document.getElementById('detail-fb-link').href = item.facebook || '#';

            document.getElementById('edit-interest-type').value = item.interest_type || 'ดอกลอย';
            document.getElementById('edit-daily-rate').value = item.daily_interest_rate || '';
            document.getElementById('edit-fixed-rate').value = item.fixed_interest || '';
            document.getElementById('edit-installment-amount').value = item.installment_amount || '';
            toggleInterestFields();

            const btnContainer = document.getElementById('approve-btn-container');
            if (item.status === 'รออนุมัติ') {
                btnContainer.innerHTML = `
                    <button onclick="approveLoan(${index})" class="py-2.5 bg-emerald-600 text-white font-bold text-xs rounded-xl">อนุมัติวงเงิน</button>
                    <button onclick="rejectLoan(${index})" class="py-2.5 bg-rose-600 text-white font-bold text-xs rounded-xl">ยกเลิก</button>
                `;
            } else {
                btnContainer.innerHTML = '';
            }
            document.getElementById('userDetailModal').classList.remove('hidden');
        }

        function toggleInterestFields() {
            const type = document.getElementById('edit-interest-type').value;
            document.getElementById('field-daily').classList.toggle('hidden', type !== 'ดอกลอย');
            document.getElementById('field-fixed').classList.toggle('hidden', type !== 'ดอกคงที่');
            document.getElementById('field-installment').classList.toggle('hidden', type !== 'จบต้นดอก');
        }

        function saveInterestSettings() {
            if (currentEditIndex === -1) return;
            debtorsList[currentEditIndex].interest_type = document.getElementById('edit-interest-type').value;
            debtorsList[currentEditIndex].daily_interest_rate = floatVal('edit-daily-rate');
            debtorsList[currentEditIndex].fixed_interest = floatVal('edit-fixed-rate');
            debtorsList[currentEditIndex].installment_amount = floatVal('edit-installment-amount');
            alert('อัปเดตดอกเบี้ยสำเร็จ!');
            renderDebtorsTable();
        }

        function floatVal(id) { return parseFloat(document.getElementById(id).value) || 0; }
        function approveLoan(index) { debtorsList[index].status = 'ปกติ'; alert('อนุมัติเรียบร้อย!'); closeUserDetailModal(); renderDebtorsTable(); }
        function rejectLoan(index) { debtorsList[index].status = 'ยกเลิก'; alert('ยกเลิกเรียบร้อย!'); closeUserDetailModal(); renderDebtorsTable(); }
        function closeUserDetailModal() { document.getElementById('userDetailModal').classList.add('hidden'); }
        function setFilterStatus(status) { currentFilterStatus = status; renderDebtorsTable(); }

        window.onload = function() { renderDebtorsTable(); }
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
            <p class="text-xs text-slate-500 mt-1">กรอกข้อมูลส่วนตัว ใส่ลิงก์ Facebook และเซ็นสัญญาเพื่อส่งขอกู้</p>
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

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1"><i class="fa-brands fa-facebook text-blue-600 mr-1"></i> ลิงก์โปรไฟล์ Facebook</label>
                <input type="url" name="facebook" required placeholder="https://www.facebook.com/your.profile" class="w-full px-4 py-2.5 bg-slate-50 border rounded-xl text-sm text-blue-700">
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
                ยื่นคำขอกู้เงิน
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
    return render_template_string(ADMIN_TEMPLATE, debtors=debtors_database)

@app.route('/apply')
def apply_form():
    return render_template_string(APPLY_TEMPLATE)

@app.route('/submit-application', methods=['POST'])
def submit_application():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    new_entry = {
        'id': f"#{len(debtors_database)+541540}",
        'username': request.form.get('phone'),
        'name': request.form.get('name'),
        'phone': request.form.get('phone'),
        'facebook': request.form.get('facebook'),
        'acc': request.form.get('account'),
        'bank': request.form.get('bank'),
        'principal': float(request.form.get('amount') or 0),
        'interest_type': 'ยังไม่กำหนด',
        'daily_interest_rate': 0,
        'fixed_interest': 0,
        'installment_amount': 0,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'ip': client_ip,
        'status': 'รออนุมัติ',
        'idCardPhoto': 'uploaded_id.jpg',
        'signature': 'signed',
        'remark': 'ยื่นกู้ผ่านเว็บ'
    }
    debtors_database.insert(0, new_entry)
    return "<script>alert('ยื่นคำขอกู้เรียบร้อย!'); window.location.href='/';</script>"

if __name__ == '__main__':
    app.run(debug=True)
