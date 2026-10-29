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
        .glass-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.6);
        }
        .sidebar-item-active {
            background: #ffffff !important;
            box-shadow: 0 4px 15px -3px rgba(139, 92, 246, 0.15), 0 2px 6px -2px rgba(99, 102, 241, 0.1);
            color: #6d28d9 !important;
            font-weight: 600 !important;
            border: 1px solid rgba(216, 180, 254, 0.5);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
    </style>
</head>
<body class="text-slate-800 antialiased bg-slate-50 flex h-screen overflow-hidden">

    <!-- Mobile Sidebar Toggle Overlay -->
    <div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 bg-slate-900/40 z-40 hidden md:hidden transition-opacity backdrop-blur-xs"></div>

    <!-- Sidebar Main Menu (Deep Royal / Vibrant Purple Theme) -->
    <aside id="sidebar" class="fixed md:static inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-purple-950 via-slate-900 to-indigo-950 border-r border-purple-900/50 text-purple-100 flex flex-col transition-all duration-300 transform -translate-x-full md:translate-x-0 shadow-2xl shadow-purple-950/50">
        <!-- Logo & Brand Header -->
        <div class="p-5 flex items-center justify-between border-b border-purple-900/60">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-pink-500 flex items-center justify-center text-white shadow-lg shadow-purple-600/40 font-bold text-lg">
                    <i class="fa-solid font-bold text-lg">฿</i>
                </div>
                <div>
                    <div class="flex items-center space-x-1.5">
                        <span class="text-xl font-bold tracking-tight text-white">BizFlow</span>
                        <span class="px-1.5 py-0.5 text-[10px] font-black bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-md uppercase tracking-wider shadow-xs">PLUS</span>
                    </div>
                    <p class="text-[11px] text-purple-300/80 font-normal">ระบบจัดการลูกหนี้ & บัญชี</p>
                </div>
            </div>
            <button onclick="toggleSidebar()" class="md:hidden text-purple-400 hover:text-white">
                <i class="fa-solid fa-xmark text-lg"></i>
            </button>
        </div>

        <!-- Navigation Links -->
        <nav class="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
            <a href="#" onclick="switchTab('dashboard')" id="nav-dashboard" class="sidebar-item sidebar-item-active flex items-center space-x-3 px-3.5 py-3 rounded-xl text-purple-200 hover:bg-purple-900/40 hover:text-white transition duration-150">
                <i class="fa-solid fa-chart-pie w-5 text-purple-400"></i>
                <span class="font-medium text-sm">แดชบอร์ดการเงิน</span>
            </a>
            <a href="#" onclick="switchTab('debtors')" id="nav-debtors" class="sidebar-item flex items-center space-x-3 px-3.5 py-3 rounded-xl text-purple-200/80 hover:bg-purple-900/40 hover:text-white transition duration-150">
                <i class="fa-solid fa-hand-holding-dollar w-5 text-amber-400"></i>
                <span class="font-medium text-sm">จัดการลูกหนี้ (ปล่อยกู้)</span>
            </a>
            <a href="#" onclick="switchTab('transactions')" id="nav-transactions" class="sidebar-item flex items-center space-x-3 px-3.5 py-3 rounded-xl text-purple-200/80 hover:bg-purple-900/40 hover:text-white transition duration-150">
                <i class="fa-solid fa-receipt w-5 text-emerald-400"></i>
                <span class="font-medium text-sm">บันทึกรายรับ-รายจ่าย</span>
            </a>
            <a href="#" onclick="switchTab('accounts')" id="nav-accounts" class="sidebar-item flex items-center space-x-3 px-3.5 py-3 rounded-xl text-purple-200/80 hover:bg-purple-900/40 hover:text-white transition duration-150">
                <i class="fa-solid fa-building-columns w-5 text-sky-400"></i>
                <span class="font-medium text-sm">บัญชีธนาคาร & เงินสด</span>
            </a>
            <a href="#" onclick="switchTab('supabase')" id="nav-supabase" class="sidebar-item flex items-center space-x-3 px-3.5 py-3 rounded-xl text-purple-200/80 hover:bg-purple-900/40 hover:text-white transition duration-150">
                <i class="fa-solid fa-database w-5 text-indigo-400"></i>
                <span class="font-medium text-sm">รายงาน & ตั้งค่า Supabase</span>
            </a>
        </nav>

        <!-- Supabase Live Connection Widget -->
        <div class="p-3.5 mx-3 mb-3 rounded-xl bg-purple-900/30 backdrop-blur-md border border-purple-800/50 shadow-inner">
            <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-semibold text-purple-200">Supabase Status</span>
                <span id="sidebar-db-badge" class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    <span class="w-1.5 h-1.5 mr-1 rounded-full bg-emerald-400 animate-pulse"></span> Connected
                </span>
            </div>
            <p class="text-[11px] text-purple-300/70 truncate" id="sidebar-db-url">db.pdpeqsubrbmdjxgmtjpy...</p>
        </div>

        <!-- User Profile Footer -->
        <div class="p-3.5 border-t border-purple-900/60 bg-purple-950/60 backdrop-blur-xs flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-purple-800/80 flex items-center justify-center text-xs font-bold text-purple-200 border border-purple-600/50">
                    NU
                </div>
                <div class="truncate">
                    <div class="text-xs font-bold text-white truncate">nuengdi7819-ux</div>
                    <div class="text-[10px] text-purple-300 font-medium">ผู้ดูแลระบบ</div>
                </div>
            </div>
            <button class="text-purple-400 hover:text-rose-400 transition p-1" title="ออกจากระบบ">
                <i class="fa-solid fa-right-from-bracket text-sm"></i>
            </button>
        </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        <!-- Top Navbar -->
        <header class="bg-white border-b border-slate-200/80 px-4 py-3 sm:px-6 flex items-center justify-between shadow-sm z-10">
            <div class="flex items-center space-x-3">
                <button onclick="toggleSidebar()" class="md:hidden text-slate-600 hover:text-slate-900 p-1.5 rounded-lg border border-slate-200">
                    <i class="fa-solid fa-bars text-lg"></i>
                </button>
                <h2 id="page-title" class="text-lg font-bold text-slate-900">แดชบอร์ดการเงิน</h2>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="openDebtorModal()" class="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white text-xs font-medium shadow-md shadow-purple-500/20 transition active:scale-95">
                    <i class="fa-solid fa-user-plus text-xs"></i>
                    <span class="hidden sm:inline">+ เพิ่มลูกหนี้</span>
                </button>
                <button onclick="openTxModal()" class="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium shadow-sm transition active:scale-95">
                    <i class="fa-solid fa-plus text-xs"></i>
                    <span>+ บันทึกรายการ</span>
                </button>
            </div>
        </header>

        <!-- Main Content Views container -->
        <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">

            <!-- 1. DASHBOARD VIEW -->
            <div id="view-dashboard" class="view-content space-y-6">
                <!-- Stat Cards Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
                    <!-- Stat Card 1 -->
                    <div class="glass-card p-5 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-slate-500">ยอดลูกหนี้คงค้างทั้งหมด</span>
                            <div class="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
                                <i class="fa-solid fa-sack-dollar text-sm"></i>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h3 class="text-2xl font-bold text-slate-900" id="dash-total-debt">฿145,000</h3>
                            <p class="text-xs text-amber-600 mt-1 flex items-center">
                                <i class="fa-solid fa-clock mr-1"></i> รอชำระดอกเบี้ยเดือนนี้ ฿8,500
                            </p>
                        </div>
                    </div>

                    <!-- Stat Card 2 -->
                    <div class="glass-card p-5 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-slate-500">รายรับเดือนนี้</span>
                            <div class="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                                <i class="fa-solid fa-arrow-down-left text-sm"></i>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h3 class="text-2xl font-bold text-slate-900" id="dash-monthly-income">฿32,400</h3>
                            <p class="text-xs text-emerald-600 mt-1 flex items-center">
                                <i class="fa-solid fa-arrow-trend-up mr-1"></i> +12% จากเดือนที่แล้ว
                            </p>
                        </div>
                    </div>

                    <!-- Stat Card 3 -->
                    <div class="glass-card p-5 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-slate-500">รายจ่ายเดือนนี้</span>
                            <div class="w-8 h-8 rounded-xl bg-rose-500/10 text-rose-600 flex items-center justify-center">
                                <i class="fa-solid fa-arrow-up-right text-sm"></i>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h3 class="text-2xl font-bold text-slate-900" id="dash-monthly-expense">฿14,200</h3>
                            <p class="text-xs text-slate-500 mt-1 flex items-center">
                                ค่าใช้จ่ายดำเนินงานทั่วไป
                            </p>
                        </div>
                    </div>

                    <!-- Stat Card 4 -->
                    <div class="glass-card p-5 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-slate-500">เงินสดคงเหลือรวม</span>
                            <div class="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-600 flex items-center justify-center">
                                <i class="fa-solid fa-wallet text-sm"></i>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h3 class="text-2xl font-bold text-slate-900" id="dash-total-cash">฿284,500</h3>
                            <p class="text-xs text-purple-600 mt-1 flex items-center">
                                <i class="fa-solid fa-shield-check mr-1"></i> รวม 3 บัญชีธนาคาร
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Chart 1: Financial Trend -->
                    <div class="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-slate-800 text-sm">ภาพรวมรายรับ-รายจ่าย (6 เดือนล่าสุด)</h3>
                            <span class="text-xs text-slate-400">หน่วย: บาท</span>
                        </div>
                        <div class="h-64">
                            <canvas id="financeChart"></canvas>
                        </div>
                    </div>

                    <!-- Recent Debtor Activity -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-slate-800 text-sm">ลูกหนี้ครบกำหนดชำระเร็วๆ นี้</h3>
                            <a href="#" onclick="switchTab('debtors')" class="text-xs text-purple-600 hover:underline">ดูทั้งหมด</a>
                        </div>
                        <div class="space-y-3 flex-1 overflow-y-auto" id="dash-upcoming-debtors">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. DEBTORS MANAGEMENT VIEW -->
            <div id="view-debtors" class="view-content hidden space-y-5">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div class="relative w-full sm:w-72">
                        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                        <input type="text" id="debtor-search" onkeyup="filterDebtors()" placeholder="ค้นหาชื่อลูกหนี้..." class="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none">
                    </div>
                    <div class="flex space-x-2 w-full sm:w-auto">
                        <button onclick="openDebtorModal()" class="w-full sm:w-auto px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-medium transition shadow-sm">
                            + ปล่อยกู้ใหม่
                        </button>
                    </div>
                </div>

                <!-- Debtors Table Card -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-4">ชื่อลูกหนี้</th>
                                    <th class="p-4">เงินต้น</th>
                                    <th class="p-4">ดอกเบี้ย/เดือน</th>
                                    <th class="p-4">กำหนดชำระ</th>
                                    <th class="p-4">สถานะ</th>
                                    <th class="p-4 text-right">จัดการ</th>
                                </tr>
                            </thead>
                            <tbody id="debtors-table-body" class="divide-y divide-slate-100">
                                <!-- Dynamic Content -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 3. TRANSACTIONS VIEW -->
            <div id="view-transactions" class="view-content hidden space-y-5">
                <div class="flex justify-between items-center">
                    <h3 class="font-bold text-slate-800 text-sm">ประวัติรายการรับ-จ่ายทั้งหมด</h3>
                    <button onclick="openTxModal()" class="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-medium transition">
                        + บันทึกรายการใหม่
                    </button>
                </div>

                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-4">วันที่</th>
                                    <th class="p-4">ประเภท</th>
                                    <th class="p-4">รายการ</th>
                                    <th class="p-4">หมวดหมู่</th>
                                    <th class="p-4 text-right">จำนวนเงิน</th>
                                </tr>
                            </thead>
                            <tbody id="tx-table-body" class="divide-y divide-slate-100">
                                <!-- Dynamic Content -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 4. BANK ACCOUNTS VIEW -->
            <div id="view-accounts" class="view-content hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-5" id="accounts-grid">
                    <!-- Dynamic Account Cards -->
                </div>
            </div>

            <!-- 5. SUPABASE SETTINGS VIEW -->
            <div id="view-supabase" class="view-content hidden space-y-6 max-w-3xl mx-auto">
                <div class="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200/80 shadow-sm space-y-6">
                    <div class="border-b border-slate-100 pb-4">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center text-lg">
                                <i class="fa-solid fa-database"></i>
                            </div>
                            <div>
                                <h3 class="text-base font-bold text-slate-900">ตั้งค่า Supabase Connection</h3>
                                <p class="text-xs text-slate-500">จัดการข้อมูลการเชื่อมต่อฐานข้อมูล Supabase ของ BizFlow+</p>
                            </div>
                        </div>
                    </div>

                    <!-- Connection Status Banner -->
                    <div id="sp-status-banner" class="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <span class="flex h-3 w-3 relative">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                            </span>
                            <div>
                                <h4 class="text-xs font-semibold text-emerald-900">เชื่อมต่อ Supabase สำเร็จ (Real-time Active)</h4>
                                <p class="text-[11px] text-emerald-700">Project: pdpeqsubrbmdjxgmtjpy (Direct PostgreSQL Connected)</p>
                            </div>
                        </div>
                        <span class="px-2.5 py-1 bg-emerald-600 text-white text-[10px] font-bold rounded-lg uppercase tracking-wider">Online</span>
                    </div>

                    <!-- Config Form -->
                    <form onsubmit="saveSupabaseConfig(event)" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-700 mb-1">Supabase URL</label>
                            <input type="text" id="sp-url" value="https://pdpeqsubrbmdjxgmtjpy.supabase.co" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-700 mb-1">Supabase Anon / Service Key</label>
                            <input type="password" id="sp-key" value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none">
                        </div>

                        <div class="pt-2 flex justify-end">
                            <button type="submit" class="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white text-xs font-medium rounded-xl shadow-md transition active:scale-95">
                                บันทึกการเชื่อมต่อ
                            </button>
                        </div>
                    </form>
                </div>
            </div>

        </main>
    </div>

    <!-- MODAL 1: Add/Edit Debtor -->
    <div id="modal-debtor" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl border border-slate-200 max-w-md w-full p-6 shadow-2xl space-y-4">
            <div class="flex justify-between items-center border-b pb-3">
                <h3 class="font-bold text-slate-800 text-sm" id="modal-debtor-title">เพิ่มข้อมูลลูกหนี้ใหม่</h3>
                <button onclick="closeDebtorModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form onsubmit="saveDebtor(event)" class="space-y-3 text-xs">
                <div>
                    <label class="block font-medium text-slate-700 mb-1">ชื่อ-นามสกุล ลูกหนี้</label>
                    <input type="text" id="debtor-name" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block font-medium text-slate-700 mb-1">จำนวนเงินกู้ (บาท)</label>
                        <input type="number" id="debtor-amount" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block font-medium text-slate-700 mb-1">ดอกเบี้ยต่อเดือน (บาท)</label>
                        <input type="number" id="debtor-interest" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                    </div>
                </div>
                <div>
                    <label class="block font-medium text-slate-700 mb-1">วันกำหนดชำระของทุกเดือน</label>
                    <input type="date" id="debtor-duedate" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                </div>
                <div>
                    <label class="block font-medium text-slate-700 mb-1">สถานะ</label>
                    <select id="debtor-status" class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                        <option value="ปกติ">ปกติ (ชำระตรงเวลา)</option>
                        <option value="ค้างชำระ">ค้างชำระ</option>
                        <option value="ปิดยอดแล้ว">ปิดยอดแล้ว</option>
                    </select>
                </div>
                <div class="pt-3 flex space-x-2 justify-end">
                    <button type="button" onclick="closeDebtorModal()" class="px-4 py-2 border rounded-xl text-slate-600 hover:bg-slate-50">ยกเลิก</button>
                    <button type="submit" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium">บันทึกข้อมูล</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 2: Add Transaction -->
    <div id="modal-tx" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl border border-slate-200 max-w-md w-full p-6 shadow-2xl space-y-4">
            <div class="flex justify-between items-center border-b pb-3">
                <h3 class="font-bold text-slate-800 text-sm">บันทึกรายการรับ-จ่ายใหม่</h3>
                <button onclick="closeTxModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form onsubmit="saveTransaction(event)" class="space-y-3 text-xs">
                <div>
                    <label class="block font-medium text-slate-700 mb-1">ประเภทรายการ</label>
                    <select id="tx-type" class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                        <option value="รายรับ">รายรับ (+)</option>
                        <option value="รายจ่าย">รายจ่าย (-)</option>
                    </select>
                </div>
                <div>
                    <label class="block font-medium text-slate-700 mb-1">รายละเอียด / รายการ</label>
                    <input type="text" id="tx-title" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block font-medium text-slate-700 mb-1">จำนวนเงิน (บาท)</label>
                        <input type="number" id="tx-amount" required class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block font-medium text-slate-700 mb-1">หมวดหมู่</label>
                        <select id="tx-category" class="w-full px-3 py-2 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none">
                            <option value="ดอกเบี้ยรับ">ดอกเบี้ยรับ</option>
                            <option value="รับชำระคืนเงินต้น">รับชำระคืนเงินต้น</option>
                            <option value="ค่าใช้จ่ายทั่วไป">ค่าใช้จ่ายทั่วไป</option>
                            <option value="เงินกู้ปล่อยใหม่">เงินกู้ปล่อยใหม่</option>
                        </select>
                    </div>
                </div>
                <div class="pt-3 flex space-x-2 justify-end">
                    <button type="button" onclick="closeTxModal()" class="px-4 py-2 border rounded-xl text-slate-600 hover:bg-slate-50">ยกเลิก</button>
                    <button type="submit" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-medium">บันทึกรายการ</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="toast" class="fixed bottom-5 right-5 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-3 text-xs z-50 transform translate-y-20 opacity-0 transition-all duration-300">
        <i id="toast-icon" class="fa-solid fa-circle-check text-emerald-400 text-base"></i>
        <span id="toast-message">บันทึกข้อมูลเรียบร้อยแล้ว</span>
    </div>

    <!-- Application JavaScript Logic -->
    <script>
        // Data State
        let debtors = [
            { id: 1, name: "สมชาย เข็มกลัด", amount: 50000, interest: 2500, duedate: "2026-11-05", status: "ปกติ" },
            { id: 2, name: "วิภาวี มั่นคง", amount: 30000, interest: 1500, duedate: "2026-11-01", status: "ค้างชำระ" },
            { id: 3, name: "กิตติศักดิ์ เจริญดี", amount: 65000, interest: 4500, duedate: "2026-11-15", status: "ปกติ" }
        ];

        let transactions = [
            { id: 1, date: "2026-10-28", type: "รายรับ", title: "รับดอกเบี้ย สมชาย เข็มกลัด", category: "ดอกเบี้ยรับ", amount: 2500 },
            { id: 2, date: "2026-10-25", type: "รายจ่าย", title: "ค่าน้ำมันสำรวจงาน", category: "ค่าใช้จ่ายทั่วไป", amount: 1200 },
            { id: 3, date: "2026-10-20", type: "รายรับ", title: "รับคืนเงินต้น วิภาวี", category: "รับชำระคืนเงินต้น", amount: 10000 }
        ];

        let accounts = [
            { name: "ธนาคารกสิกรไทย (KBANK)", number: "xxx-x-x1234-x", balance: 145000, color: "from-emerald-500 to-teal-700" },
            { name: "ธนาคารไทยพาณิชย์ (SCB)", number: "xxx-x-x5678-x", balance: 98500, color: "from-purple-600 to-indigo-800" },
            { name: "เงินสดคงเหลือ (Cash)", number: "กระเป๋าเงินสดหลัก", balance: 41000, color: "from-slate-700 to-slate-900" }
        ];

        // Chart Instance
        let financeChart;

        // On Page Load Initialization
        window.onload = function() {
            renderDebtors();
            renderTransactions();
            renderAccounts();
            renderUpcomingDebtors();
            initChart();
        };

        // Navigation Switcher
        function switchTab(tab) {
            const views = document.querySelectorAll('.view-content');
            views.forEach(v => v.classList.add('hidden'));

            const items = document.querySelectorAll('.sidebar-item');
            items.forEach(i => i.classList.remove('sidebar-item-active'));

            document.getElementById('view-' + tab).classList.remove('hidden');
            document.getElementById('nav-' + tab).classList.add('sidebar-item-active');

            const titles = {
                'dashboard': 'แดชบอร์ดการเงิน',
                'debtors': 'จัดการลูกหนี้ (ปล่อยกู้)',
                'transactions': 'บันทึกรายรับ-รายจ่าย',
                'accounts': 'บัญชีธนาคาร & เงินสด',
                'supabase': 'รายงาน & ตั้งค่า Supabase'
            };
            document.getElementById('page-title').innerText = titles[tab] || 'BizFlow+';

            // Close sidebar on mobile
            if (window.innerWidth < 768) {
                toggleSidebar();
            }
        }

        // Sidebar Toggle
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        }

        // Render Debtors Table
        function renderDebtors(items = debtors) {
            const tbody = document.getElementById('debtors-table-body');
            tbody.innerHTML = '';
            items.forEach(d => {
                const statusBadge = d.status === 'ปกติ' 
                    ? `<span class="px-2.5 py-1 bg-emerald-50 text-emerald-600 rounded-lg text-[10px] font-semibold border border-emerald-200">ปกติ</span>`
                    : (d.status === 'ค้างชำระ' 
                        ? `<span class="px-2.5 py-1 bg-rose-50 text-rose-600 rounded-lg text-[10px] font-semibold border border-rose-200">ค้างชำระ</span>`
                        : `<span class="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-lg text-[10px] font-semibold">ปิดยอดแล้ว</span>`);

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="p-4 font-medium text-slate-900">${d.name}</td>
                        <td class="p-4 font-semibold text-slate-800">฿${d.amount.toLocaleString()}</td>
                        <td class="p-4 text-emerald-600 font-medium">+฿${d.interest.toLocaleString()}</td>
                        <td class="p-4 text-slate-500">${d.duedate}</td>
                        <td class="p-4">${statusBadge}</td>
                        <td class="p-4 text-right space-x-2">
                            <button onclick="deleteDebtor(${d.id})" class="p-1.5 text-slate-400 hover:text-rose-500 transition"><i class="fa-solid fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            });
        }

        // Filter Debtors
        function filterDebtors() {
            const query = document.getElementById('debtor-search').value.toLowerCase();
            const filtered = debtors.filter(d => d.name.toLowerCase().includes(query));
            renderDebtors(filtered);
        }

        // Render Transactions
        function renderTransactions() {
            const tbody = document.getElementById('tx-table-body');
            tbody.innerHTML = '';
            transactions.forEach(t => {
                const isIncome = t.type === 'รายรับ';
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="p-4 text-slate-500">${t.date}</td>
                        <td class="p-4">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isIncome ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}">${t.type}</span>
                        </td>
                        <td class="p-4 font-medium text-slate-900">${t.title}</td>
                        <td class="p-4 text-slate-500">${t.category}</td>
                        <td class="p-4 text-right font-bold ${isIncome ? 'text-emerald-600' : 'text-rose-600'}">
                            ${isIncome ? '+' : '-'}฿${t.amount.toLocaleString()}
                        </td>
                    </tr>
                `;
            });
        }

        // Render Bank Accounts
        function renderAccounts() {
            const grid = document.getElementById('accounts-grid');
            grid.innerHTML = '';
            accounts.forEach(a => {
                grid.innerHTML += `
                    <div class="bg-gradient-to-br ${a.color} p-6 rounded-2xl text-white shadow-md relative overflow-hidden">
                        <div class="absolute right-3 bottom-3 opacity-10 text-7xl font-black">฿</div>
                        <p class="text-xs text-white/80 font-medium">${a.name}</p>
                        <p class="text-xs text-white/60 tracking-wider mt-1">${a.number}</p>
                        <div class="mt-6">
                            <span class="text-[10px] uppercase tracking-wider text-white/70">ยอดเงินคงเหลือ</span>
                            <h3 class="text-2xl font-bold mt-0.5">฿${a.balance.toLocaleString()}</h3>
                        </div>
                    </div>
                `;
            });
        }

        // Render Dashboard Upcoming Debtors
        function renderUpcomingDebtors() {
            const container = document.getElementById('dash-upcoming-debtors');
            container.innerHTML = '';
            debtors.slice(0, 3).forEach(d => {
                container.innerHTML += `
                    <div class="p-3 bg-slate-50 rounded-xl flex items-center justify-between">
                        <div>
                            <div class="font-medium text-xs text-slate-900">${d.name}</div>
                            <div class="text-[10px] text-slate-500">กำหนดชำระ: ${d.duedate}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-xs font-bold text-slate-800">฿${d.interest.toLocaleString()}</div>
                            <span class="text-[9px] text-emerald-600 font-medium">ดอกเบี้ย</span>
                        </div>
                    </div>
                `;
            });
        }

        // Initialize Chart
        function initChart() {
            const ctx = document.getElementById('financeChart').getContext('2d');
            financeChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.'],
                    datasets: [
                        {
                            label: 'รายรับ',
                            data: [18000, 22000, 25000, 29000, 31000, 32400],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.05)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'รายจ่าย',
                            data: [12000, 15000, 11000, 14000, 13000, 14200],
                            borderColor: '#f43f5e',
                            backgroundColor: 'transparent',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { font: { family: 'Kanit', size: 11 } } }
                    },
                    scales: {
                        y: { grid: { borderDash: [2, 2] } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // Modals Toggle
        function openDebtorModal() { document.getElementById('modal-debtor').classList.remove('hidden'); }
        function closeDebtorModal() { document.getElementById('modal-debtor').classList.add('hidden'); }
        function openTxModal() { document.getElementById('modal-tx').classList.remove('hidden'); }
        function closeTxModal() { document.getElementById('modal-tx').classList.add('hidden'); }

        // Save Debtor Handler
        function saveDebtor(e) {
            e.preventDefault();
            const newDebtor = {
                id: Date.now(),
                name: document.getElementById('debtor-name').value,
                amount: parseFloat(document.getElementById('debtor-amount').value),
                interest: parseFloat(document.getElementById('debtor-interest').value),
                duedate: document.getElementById('debtor-duedate').value,
                status: document.getElementById('debtor-status').value
            };
            debtors.unshift(newDebtor);
            renderDebtors();
            renderUpcomingDebtors();
            closeDebtorModal();
            showToast('เพิ่มข้อมูลลูกหนี้เรียบร้อยแล้ว');
        }

        // Delete Debtor
        function deleteDebtor(id) {
            debtors = debtors.filter(d => d.id !== id);
            renderDebtors();
            renderUpcomingDebtors();
            showToast('ลบรายการลูกหนี้สำเร็จ');
        }

        // Save Transaction Handler
        function saveTransaction(e) {
            e.preventDefault();
            const newTx = {
                id: Date.now(),
                date: new Date().toISOString().split('T')[0],
                type: document.getElementById('tx-type').value,
                title: document.getElementById('tx-title').value,
                category: document.getElementById('tx-category').value,
                amount: parseFloat(document.getElementById('tx-amount').value)
            };
            transactions.unshift(newTx);
            renderTransactions();
            closeTxModal();
            showToast('บันทึกรายการรับ-จ่ายเรียบร้อย');
        }

        // Save Supabase Config
        function saveSupabaseConfig(e) {
            e.preventDefault();
            showToast('บันทึกการตั้งค่า Supabase สำเร็จ');
        }

        // Toast Notification Helper
        function showToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toast-message').innerText = msg;
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 3000);
        }
    </script>
</body>
</html>
