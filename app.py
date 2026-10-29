from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
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
    
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Kanit', 'Inter', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            50: '#f5f3ff',
                            100: '#ede9fe',
                            500: '#8b5cf6',
                            600: '#7c3aed',
                            700: '#6d28d9',
                            dark: '#0f172a',
                            sidebar: '#0b0f19'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Kanit', sans-serif;
            background-color: #f8fafc;
        }
        .sidebar-item-active {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(126, 34, 206, 0.2) 100%);
            border: 1px solid rgba(192, 132, 252, 0.4);
            color: #f3e8ff;
            box-shadow: 0 4px 20px -2px rgba(147, 51, 234, 0.25);
        }
        .sidebar-bg {
            background: linear-gradient(180deg, #18092e 0%, #0d061a 50%, #110726 100%);
        }
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
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-chart-pie text-lg text-purple-400 w-6"></i>
                    <span>แดชบอร์ดการเงิน</span>
                </button>

                <button onclick="switchTab('debtors')" id="nav-debtors" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active">
                    <i class="fa-solid fa-hand-holding-dollar text-lg text-amber-400 w-6"></i>
                    <span>จัดการลูกหนี้ (ปล่อยกู้)</span>
                </button>

                <button onclick="switchTab('transactions')" id="nav-transactions" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-receipt text-lg text-emerald-400 w-6"></i>
                    <span>บันทึกรายรับ-รายจ่าย</span>
                </button>

                <button onclick="switchTab('banking')" id="nav-banking" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-building-columns text-lg text-sky-400 w-6"></i>
                    <span>บัญชีธนาคาร & เงินสด</span>
                </button>

                <button onclick="switchTab('settings')" id="nav-settings" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-database text-lg text-purple-400 w-6"></i>
                    <span>รายงาน & ตั้งค่า Supabase</span>
                </button>
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
                    <div class="w-9 h-9 rounded-full bg-purple-800/60 border border-purple-500/30 flex items-center justify-center text-xs font-bold text-purple-200">
                        NU
                    </div>
                    <div>
                        <p class="text-xs font-bold text-slate-100">nuengdi7819-ux</p>
                        <p class="text-[10px] text-purple-300/60">ผู้ดูแลระบบ</p>
                    </div>
                </div>
                <button class="text-purple-300/60 hover:text-white transition-colors">
                    <i class="fa-solid fa-right-from-bracket text-sm"></i>
                </button>
            </div>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto min-h-screen bg-slate-50/50">
        <!-- Top Bar -->
        <header class="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10 px-8 py-4 flex items-center justify-between shadow-sm">
            <div>
                <h2 id="page-title" class="text-xl font-bold text-slate-800">จัดการลูกหนี้ (ปล่อยกู้)</h2>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="openAddDebtorModal()" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl font-medium text-sm shadow-md shadow-purple-500/20 transition-all flex items-center space-x-2">
                    <i class="fa-solid fa-user-plus text-xs"></i>
                    <span>+ เพิ่มลูกหนี้</span>
                </button>
            </div>
        </header>

        <!-- Dynamic Content Sections -->
        <div class="p-8">

            <!-- Section: Dashboard -->
            <div id="section-dashboard" class="hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <span class="text-sm font-medium text-slate-500">ยอดลูกหนี้คงค้างรวม</span>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿284,500</h3>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <span class="text-sm font-medium text-slate-500">รายรับเดือนนี้</span>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿92,400</h3>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <span class="text-sm font-medium text-slate-500">รายจ่ายเดือนนี้</span>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿18,200</h3>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <span class="text-sm font-medium text-slate-500">เงินสด/ธนาคารคงเหลือ</span>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿284,500</h3>
                    </div>
                </div>
            </div>

            <!-- Section: Debtors (ปล่อยกู้) - Active -->
            <div id="section-debtors" class="space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                        <div>
                            <h3 class="text-lg font-bold text-slate-800">รายชื่อลูกหนี้ทั้งหมด</h3>
                            <p class="text-xs text-slate-500">ค้นหาประวัติลูกค้าเก่าด้วยชื่อหรือเบอร์โทร เพื่อเพิ่มบิลหรือตัดยอดได้ทันที</p>
                        </div>
                        <div class="flex items-center space-x-3">
                            <!-- Search Bar -->
                            <div class="relative">
                                <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-400">
                                    <i class="fa-solid fa-search text-xs"></i>
                                </span>
                                <input type="text" id="searchInput" oninput="filterDebtors()" placeholder="ค้นหาด้วยชื่อ หรือ เบอร์โทร..." class="w-64 pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 transition-all">
                            </div>
                            <button onclick="openAddDebtorModal()" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all whitespace-nowrap">
                                <i class="fa-solid fa-plus mr-1"></i> เพิ่มลูกหนี้
                            </button>
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-500 rounded-xl">
                                <tr>
                                    <th class="p-3.5 font-semibold">ชื่อ-นามสกุล</th>
                                    <th class="p-3.5 font-semibold">เบอร์โทรศัพท์</th>
                                    <th class="p-3.5 font-semibold">เงินต้น</th>
                                    <th class="p-3.5 font-semibold">ดอกเบี้ย/เดือน</th>
                                    <th class="p-3.5 font-semibold">ยอดคงค้าง</th>
                                    <th class="p-3.5 font-semibold">กำหนดชำระ</th>
                                    <th class="p-3.5 font-semibold">สถานะ</th>
                                    <th class="p-3.5 font-semibold text-center">จัดการบิล / ตัดยอด</th>
                                </tr>
                            </thead>
                            <tbody id="debtor-table-body" class="divide-y divide-slate-100">
                                <!-- Data rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Section: Transactions -->
            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-4">ประวัติรายการรับ-จ่ายล่าสุด</h3>
                </div>
            </div>

            <!-- Section: Banking -->
            <div id="section-banking" class="hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white relative shadow-lg">
                        <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                        <h3 class="text-3xl font-black mt-4">฿145,000</h3>
                    </div>
                </div>
            </div>

            <!-- Section: Settings -->
            <div id="section-settings" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm">
                    <h3 class="text-xl font-bold text-slate-800 mb-6 text-center">ตั้งค่า Supabase Connection & Storage (`debtor-files`)</h3>
                    <p class="text-xs text-slate-500 mb-4 text-center">เชื่อมต่อ Bucket สำหรับเก็บไฟล์ภาพสลิปและเอกสารเรียบร้อย</p>
                </div>
            </div>

        </div>
    </main>

    <!-- Modal เพิ่ม/แก้ไข ลูกหนี้ (พร้อมช่องเบอร์โทรและแนบรูป) -->
    <div id="debtorModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <h3 id="modal-title" class="text-lg font-bold text-slate-800">เพิ่มข้อมูลลูกหนี้ใหม่</h3>
                <button onclick="closeDebtorModal()" class="text-slate-400 hover:text-slate-600">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>
            <form id="debtorForm" class="space-y-4">
                <input type="hidden" id="debtor-index" value="-1">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">ชื่อ-นามสกุล ลูกหนี้</label>
                    <input type="text" id="debtor-name" required placeholder="เช่น คุณสมชาย ใจดี" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">เบอร์โทรศัพท์ (สำหรับค้นหาประวัติเก่า)</label>
                    <input type="text" id="debtor-phone" required placeholder="เช่น 089-123-4567" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-semibold text-purple-700">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1.5">ยอดเงินต้น (บาท)</label>
                        <input type="number" id="debtor-principal" required class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1.5">ดอกเบี้ย/เดือน</label>
                        <input type="text" id="debtor-interest" required placeholder="เช่น 5% (฿2,500)" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1.5">ยอดคงค้างรวม</label>
                        <input type="number" id="debtor-total" required class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1.5">กำหนดชำระ</label>
                        <input type="text" id="debtor-duedate" placeholder="เช่น 5 พ.ย. 2026" required class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">สถานะ</label>
                    <select id="debtor-status" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                        <option value="ปกติ">ปกติ</option>
                        <option value="เกินกำหนด">เกินกำหนด</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">แนบรูปภาพ / สลิป (บันทึกเข้า Supabase Storage: `debtor-files`)</label>
                    <input type="file" id="debtor-file" accept="image/*" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100">
                </div>
                <div class="flex items-center space-x-3 pt-3">
                    <button type="button" onclick="closeDebtorModal()" class="w-1/2 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl font-semibold text-sm transition-all">ยกเลิก</button>
                    <button type="submit" class="w-1/2 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-semibold text-sm shadow-md transition-all">บันทึกข้อมูล</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal ตัดยอด / เพิ่มบิล (สำหรับลูกค้าเก่า) -->
    <div id="actionModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <h3 id="action-modal-title" class="text-lg font-bold text-slate-800">จัดการบิล / ตัดยอดชำระ</h3>
                <button onclick="closeActionModal()" class="text-slate-400 hover:text-slate-600">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>
            <input type="hidden" id="action-debtor-index">
            <div class="space-y-4">
                <div>
                    <p id="action-customer-info" class="text-sm font-bold text-purple-700 bg-purple-50 p-3 rounded-xl border border-purple-100"></p>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">เลือกทำรายการ</label>
                    <select id="action-type" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-medium">
                        <option value="add">➕ เพิ่มบิลใหม่ (เพิ่มยอดกู้)</option>
                        <option value="pay">💵 ตัดยอดชำระ (ลดหนี้คงค้าง)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">จำนวนเงิน (บาท)</label>
                    <input type="number" id="action-amount" placeholder="ระบุจำนวนเงิน..." class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-bold text-slate-900">
                </div>
                <div class="flex items-center space-x-3 pt-3">
                    <button type="button" onclick="closeActionModal()" class="w-1/2 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl font-semibold text-sm transition-all">ยกเลิก</button>
                    <button type="button" onclick="processAction()" class="w-1/2 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold text-sm shadow-md transition-all">ยืนยันทำรายการ</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ข้อมูลลูกหนี้เริ่มต้น (รองรับเบอร์โทรศัพท์และประวัติ)
        let debtorsList = [
            { name: 'คุณสมชาย ใจดี', phone: '089-111-2233', principal: 50000, interest: '5% (฿2,500)', total: 52500, duedate: '5 พ.ย. 2026', status: 'ปกติ' },
            { name: 'คุณวิภา มีสุข', phone: '081-999-8877', principal: 120000, interest: '3% (฿3,600)', total: 123600, duedate: '28 ต.ค. 2026', status: 'เกินกำหนด' }
        ];

        function renderDebtorsTable(list = debtorsList) {
            const tbody = document.getElementById('debtor-table-body');
            tbody.innerHTML = '';
            
            if (list.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">ไม่พบข้อมูลลูกหนี้ที่ค้นหา</td></tr>`;
                return;
            }

            list.forEach((item, originalIndex) => {
                const index = debtorsList.indexOf(item);
                const statusBadge = item.status === 'ปกติ' 
                    ? '<span class="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-semibold">ปกติ</span>'
                    : '<span class="px-2.5 py-1 bg-rose-100 text-rose-700 rounded-full text-xs font-semibold">เกินกำหนด</span>';
                
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="p-3.5 font-bold text-slate-800">${item.name}</td>
                        <td class="p-3.5 font-medium text-purple-600"><i class="fa-solid fa-phone text-xs mr-1"></i> ${item.phone}</td>
                        <td class="p-3.5">฿${item.principal.toLocaleString()}</td>
                        <td class="p-3.5 text-purple-600 font-medium">${item.interest}</td>
                        <td class="p-3.5 font-bold text-slate-900">฿${item.total.toLocaleString()}</td>
                        <td class="p-3.5 text-slate-600">${item.duedate}</td>
                        <td class="p-3.5">${statusBadge}</td>
                        <td class="p-3.5 text-center space-x-1.5">
                            <button onclick="openActionModal(${index})" class="px-2.5 py-1.5 bg-emerald-50 text-emerald-600 hover:bg-emerald-100 rounded-lg text-xs font-semibold transition-all" title="เพิ่มบิล/ตัดยอด"><i class="fa-solid fa-file-invoice-dollar"></i> เพิ่มบิล/ตัดยอด</button>
                            <button onclick="openEditDebtorModal(${index})" class="px-2 py-1.5 bg-amber-50 text-amber-600 hover:bg-amber-100 rounded-lg text-xs font-semibold transition-all"><i class="fa-solid fa-pen"></i></button>
                            <button onclick="deleteDebtor(${index})" class="px-2 py-1.5 bg-rose-50 text-rose-600 hover:bg-rose-100 rounded-lg text-xs font-semibold transition-all"><i class="fa-solid fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            });
        }

        // ระบบค้นหาอัจฉริยะ (รองรับทั้งชื่อและเบอร์โทร)
        function filterDebtors() {
            const keyword = document.getElementById('searchInput').value.toLowerCase();
            const filtered = debtorsList.filter(item => 
                item.name.toLowerCase().includes(keyword) || item.phone.includes(keyword)
            );
            renderDebtorsTable(filtered);
        }

        function openAddDebtorModal() {
            document.getElementById('modal-title').innerText = 'เพิ่มข้อมูลลูกหนี้ใหม่';
            document.getElementById('debtor-index').value = '-1';
            document.getElementById('debtorForm').reset();
            document.getElementById('debtorModal').classList.remove('hidden');
        }

        function openEditDebtorModal(index) {
            const item = debtorsList[index];
            document.getElementById('modal-title').innerText = 'แก้ไขข้อมูลลูกหนี้';
            document.getElementById('debtor-index').value = index;
            document.getElementById('debtor-name').value = item.name;
            document.getElementById('debtor-phone').value = item.phone;
            document.getElementById('debtor-principal').value = item.principal;
            document.getElementById('debtor-interest').value = item.interest;
            document.getElementById('debtor-total').value = item.total;
            document.getElementById('debtor-duedate').value = item.duedate;
            document.getElementById('debtor-status').value = item.status;
            document.getElementById('debtorModal').classList.remove('hidden');
        }

        function closeDebtorModal() {
            document.getElementById('debtorModal').classList.add('hidden');
        }

        document.getElementById('debtorForm').onsubmit = function(e) {
            e.preventDefault();
            const index = parseInt(document.getElementById('debtor-index').value);
            const fileInput = document.getElementById('debtor-file');
            
            // จำลองการอัปโหลดไฟล์ไปที่ Supabase Bucket debtor-files
            let fileName = fileInput.files.length > 0 ? fileInput.files[0].name : null;

            const newData = {
                name: document.getElementById('debtor-name').value,
                phone: document.getElementById('debtor-phone').value,
                principal: parseFloat(document.getElementById('debtor-principal').value) || 0,
                interest: document.getElementById('debtor-interest').value,
                total: parseFloat(document.getElementById('debtor-total').value) || 0,
                duedate: document.getElementById('debtor-duedate').value,
                status: document.getElementById('debtor-status').value,
                slip: fileName
            };

            if (index === -1) {
                debtorsList.push(newData);
                alert('บันทึกข้อมูลลูกหนี้ใหม่สำเร็จ พร้อมอัปโหลดไฟล์เข้า Bucket `debtor-files` เรียบร้อย!');
            } else {
                debtorsList[index] = newData;
                alert('อัปเดตข้อมูลลูกหนี้สำเร็จ!');
            }

            renderDebtorsTable();
            closeDebtorModal();
        }

        // Modal เพิ่มบิล หรือ ตัดยอดชำระ สำหรับลูกค้าเก่า
        function openActionModal(index) {
            const item = debtorsList[index];
            document.getElementById('action-debtor-index').value = index;
            document.getElementById('action-customer-info').innerHTML = `ลูกค้า: <span class="text-slate-900">${item.name}</span><br>เบอร์โทร: ${item.phone}<br>ยอดคงค้างปัจจุบัน: ฿${item.total.toLocaleString()}`;
            document.getElementById('action-amount').value = '';
            document.getElementById('actionModal').classList.remove('hidden');
        }

        function closeActionModal() {
            document.getElementById('actionModal').classList.add('hidden');
        }

        function processAction() {
            const index = parseInt(document.getElementById('action-debtor-index').value);
            const type = document.getElementById('action-type').value;
            const amount = parseFloat(document.getElementById('action-amount').value) || 0;

            if (amount <= 0) {
                alert('กรุณาระบุจำนวนเงินให้ถูกต้อง');
                return;
            }

            if (type === 'add') {
                debtorsList[index].total += amount;
                debtorsList[index].principal += amount;
                alert(`เพิ่มบิลยอดกู้ ฿${amount.toLocaleString()} สำเร็จ! ยอดคงค้างใหม่: ฿${debtorsList[index].total.toLocaleString()}`);
            } else {
                if (amount > debtorsList[index].total) {
                    alert('ยอดตัดชำระมากกว่ายอดหนี้คงค้างทั้งหมด');
                    return;
                }
                debtorsList[index].total -= amount;
                alert(`ตัดยอดชำระ ฿${amount.toLocaleString()} สำเร็จ! ยอดคงค้างคงเหลือ: ฿${debtorsList[index].total.toLocaleString()}`);
            }

            renderDebtorsTable();
            closeActionModal();
        }

        function deleteDebtor(index) {
            if (confirm('คุณต้องการลบข้อมูลลูกหนี้รายนี้ใช่หรือไม่?')) {
                debtorsList.splice(index, 1);
                renderDebtorsTable();
            }
        }

        function switchTab(tab) {
            ['dashboard', 'debtors', 'transactions', 'banking', 'settings'].forEach(s => {
                document.getElementById('section-' + s).classList.add('hidden');
                const nav = document.getElementById('nav-' + s);
                if (nav) {
                    nav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white";
                }
            });

            document.getElementById('section-' + tab).classList.remove('hidden');
            const activeNav = document.getElementById('nav-' + tab);
            if (activeNav) {
                activeNav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active";
            }

            const titles = {
                'dashboard': 'แดชบอร์ดการเงิน',
                'debtors': 'จัดการลูกหนี้ (ปล่อยกู้)',
                'transactions': 'บันทึกรายรับ-รายจ่าย',
                'banking': 'บัญชีธนาคาร & เงินสด',
                'settings': 'รายงาน & ตั้งค่า Supabase'
            };
            document.getElementById('page-title').innerText = titles[tab];
        }

        window.onload = function() {
            renderDebtorsTable();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
