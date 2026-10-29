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
        .glass-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.6);
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
    <aside class="w-72 sidebar-bg text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl min-h-screen border-r border-purple-900/30">
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

                <button onclick="switchTab('debtors')" id="nav-debtors" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-hand-holding-dollar text-lg text-amber-400 w-6"></i>
                    <span>จัดการลูกหนี้ (ปล่อยกู้)</span>
                </button>

                <button onclick="switchTab('transactions')" id="nav-transactions" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white">
                    <i class="fa-solid fa-receipt text-lg text-emerald-400 w-6"></i>
                    <span>บันทึกรายรับ-รายจ่าย</span>
                </button>

                <button onclick="switchTab('banking')" id="nav-banking" class="w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active">
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
            <!-- Supabase Status Widget -->
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

            <!-- Profile Widget -->
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
                <h2 id="page-title" class="text-xl font-bold text-slate-800">บัญชีธนาคาร & เงินสด</h2>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="switchTab('debtors')" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl font-medium text-sm shadow-md shadow-purple-500/20 transition-all flex items-center space-x-2">
                    <i class="fa-solid fa-user-plus text-xs"></i>
                    <span>+ เพิ่มลูกหนี้</span>
                </button>
                <button onclick="switchTab('transactions')" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-medium text-sm shadow-md shadow-slate-900/10 transition-all flex items-center space-x-2">
                    <i class="fa-solid fa-plus text-xs"></i>
                    <span>+ บันทึกรายการ</span>
                </button>
            </div>
        </header>

        <!-- Dynamic Content Sections -->
        <div class="p-8">

            <!-- Section 1: Dashboard -->
            <div id="section-dashboard" class="hidden space-y-6">
                <!-- Summary Cards Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-slate-500">ยอดลูกหนี้คงค้างรวม</span>
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                                <i class="fa-solid fa-hand-holding-dollar text-lg"></i>
                            </div>
                        </div>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿284,500</h3>
                        <p class="text-xs text-amber-600 mt-2 font-medium"><i class="fa-solid fa-arrow-up text-[10px]"></i> +12% จากเดือนที่แล้ว</p>
                    </div>

                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-slate-500">รายรับเดือนนี้</span>
                            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                                <i class="fa-solid fa-arrow-down-left text-lg"></i>
                            </div>
                        </div>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿92,400</h3>
                        <p class="text-xs text-emerald-600 mt-2 font-medium"><i class="fa-solid fa-arrow-up text-[10px]"></i> +8% จากเดือนที่แล้ว</p>
                    </div>

                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-slate-500">รายจ่ายเดือนนี้</span>
                            <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
                                <i class="fa-solid fa-arrow-up-right text-lg"></i>
                            </div>
                        </div>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿18,200</h3>
                        <p class="text-xs text-rose-500 mt-2 font-medium"><i class="fa-solid fa-arrow-down text-[10px]"></i> -3% จากเดือนที่แล้ว</p>
                    </div>

                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-slate-500">เงินสด/ธนาคารคงเหลือ</span>
                            <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                                <i class="fa-solid fa-wallet text-lg"></i>
                            </div>
                        </div>
                        <h3 class="text-2xl font-extrabold text-slate-800 mt-3">฿284,500</h3>
                        <p class="text-xs text-purple-600 mt-2 font-medium">พร้อมใช้งาน</p>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สรุปรายรับ - รายจ่าย (ปี 2026)</h4>
                        <div class="h-64">
                            <canvas id="financeChart"></canvas>
                        </div>
                    </div>
                    <div class="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
                        <h4 class="font-bold text-slate-800 text-lg mb-4">สัดส่วนบัญชีเงินฝาก</h4>
                        <div class="h-64 flex items-center justify-center">
                            <canvas id="accountChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Section 2: Debtors (ปล่อยกู้) -->
            <div id="section-debtors" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                        <div>
                            <h3 class="text-lg font-bold text-slate-800">รายชื่อลูกหนี้ทั้งหมด</h3>
                            <p class="text-xs text-slate-500">จัดการข้อมูลลูกหนี้ ยอดกู้ และอัตราดอกเบี้ย</p>
                        </div>
                        <div class="flex items-center space-x-3">
                            <input type="text" placeholder="ค้นหาลูกหนี้..." class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-500">
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-500 rounded-xl">
                                <tr>
                                    <th class="p-3.5 font-semibold">ชื่อ-นามสกุล</th>
                                    <th class="p-3.5 font-semibold">เงินต้น</th>
                                    <th class="p-3.5 font-semibold">ดอกเบี้ย/เดือน</th>
                                    <th class="p-3.5 font-semibold">ยอดคงค้าง</th>
                                    <th class="p-3.5 font-semibold">กำหนดชำระ</th>
                                    <th class="p-3.5 font-semibold">สถานะ</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr>
                                    <td class="p-3.5 font-bold text-slate-800">คุณสมชาย ใจดี</td>
                                    <td class="p-3.5">฿50,000</td>
                                    <td class="p-3.5 text-purple-600 font-medium">5% (฿2,500)</td>
                                    <td class="p-3.5 font-bold text-slate-900">฿52,500</td>
                                    <td class="p-3.5 text-slate-600">5 พ.ย. 2026</td>
                                    <td class="p-3.5"><span class="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-semibold">ปกติ</span></td>
                                </tr>
                                <tr>
                                    <td class="p-3.5 font-bold text-slate-800">คุณวิภา มีสุข</td>
                                    <td class="p-3.5">฿120,000</td>
                                    <td class="p-3.5 text-purple-600 font-medium">3% (฿3,600)</td>
                                    <td class="p-3.5 font-bold text-slate-900">฿123,600</td>
                                    <td class="p-3.5 text-rose-500 font-semibold">28 ต.ค. 2026</td>
                                    <td class="p-3.5"><span class="px-2.5 py-1 bg-rose-100 text-rose-700 rounded-full text-xs font-semibold">เกินกำหนด</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Section 3: Transactions -->
            <div id="section-transactions" class="hidden space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-4">ประวัติรายการรับ-จ่ายล่าสุด</h3>
                    <p class="text-sm text-slate-500">บันทึกธุรกรรมการเงินทั้งหมดในระบบ</p>
                </div>
            </div>

            <!-- Section 4: Banking & Cash (Active Screen Shown) -->
            <div id="section-banking" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- KBANK Card -->
                    <div class="p-6 rounded-2xl bg-emerald-600 text-white relative overflow-hidden shadow-lg shadow-emerald-600/20">
                        <div class="relative z-10 flex flex-col justify-between h-40">
                            <div>
                                <h4 class="font-bold text-lg">ธนาคารกสิกรไทย (KBANK)</h4>
                                <p class="text-xs text-emerald-200 mt-0.5">xxx-x-x1234-x</p>
                            </div>
                            <div>
                                <span class="text-xs text-emerald-200">ยอดเงินคงเหลือ</span>
                                <h3 class="text-3xl font-black tracking-tight mt-1">฿145,000</h3>
                            </div>
                        </div>
                        <i class="fa-solid fa-bold absolute -right-4 -bottom-6 text-9xl text-emerald-500/20"></i>
                    </div>

                    <!-- SCB Card -->
                    <div class="p-6 rounded-2xl bg-purple-700 text-white relative overflow-hidden shadow-lg shadow-purple-700/20">
                        <div class="relative z-10 flex flex-col justify-between h-40">
                            <div>
                                <h4 class="font-bold text-lg">ธนาคารไทยพาณิชย์ (SCB)</h4>
                                <p class="text-xs text-purple-200 mt-0.5">xxx-x-x5678-x</p>
                            </div>
                            <div>
                                <span class="text-xs text-purple-200">ยอดเงินคงเหลือ</span>
                                <h3 class="text-3xl font-black tracking-tight mt-1">฿98,500</h3>
                            </div>
                        </div>
                        <i class="fa-solid fa-bold absolute -right-4 -bottom-6 text-9xl text-purple-500/20"></i>
                    </div>

                    <!-- Cash Card -->
                    <div class="p-6 rounded-2xl bg-slate-800 text-white relative overflow-hidden shadow-lg shadow-slate-900/20">
                        <div class="relative z-10 flex flex-col justify-between h-40">
                            <div>
                                <h4 class="font-bold text-lg">เงินสดคงเหลือ (Cash)</h4>
                                <p class="text-xs text-slate-400 mt-0.5">กระเป๋าเงินสดหลัก</p>
                            </div>
                            <div>
                                <span class="text-xs text-slate-400">ยอดเงินคงเหลือ</span>
                                <h3 class="text-3xl font-black tracking-tight mt-1">฿41,000</h3>
                            </div>
                        </div>
                        <i class="fa-solid fa-bold absolute -right-4 -bottom-6 text-9xl text-slate-700/30"></i>
                    </div>
                </div>
            </div>

            <!-- Section 5: Settings / Supabase -->
            <div id="section-settings" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm">
                    <h3 class="text-xl font-bold text-slate-800 mb-6 text-center">ตั้งค่า Supabase Connection</h3>
                    <form class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Supabase URL</label>
                            <input type="text" value="https://pdpeqsubrbmdjxgmtjpy.supabase.co" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Supabase Anon Key</label>
                            <input type="password" value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                        </div>
                        <button type="button" class="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold text-sm shadow-md transition-all">
                            บันทึกการเชื่อมต่อ
                        </button>
                    </form>
                </div>
            </div>

        </div>
    </main>

    <script>
        function switchTab(tab) {
            // Hide all sections
            ['dashboard', 'debtors', 'transactions', 'banking', 'settings'].forEach(s => {
                document.getElementById('section-' + s).classList.add('hidden');
                const nav = document.getElementById('nav-' + s);
                if (nav) {
                    nav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 text-purple-200/80 hover:bg-purple-900/30 hover:text-white";
                }
            });

            // Show current section
            document.getElementById('section-' + tab).classList.remove('hidden');
            const activeNav = document.getElementById('nav-' + tab);
            if (activeNav) {
                activeNav.className = "w-full flex items-center space-x-3.5 px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 sidebar-item-active";
            }

            // Update page title
            const titles = {
                'dashboard': 'แดชบอร์ดการเงิน',
                'debtors': 'จัดการลูกหนี้ (ปล่อยกู้)',
                'transactions': 'บันทึกรายรับ-รายจ่าย',
                'banking': 'บัญชีธนาคาร & เงินสด',
                'settings': 'รายงาน & ตั้งค่า Supabase'
            };
            document.getElementById('page-title').innerText = titles[tab];
        }

        // Initialize Charts
        window.onload = function() {
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
                    datasets: [{
                        data: [145000, 98500, 41000],
                        backgroundColor: ['#059669', '#7c3aed', '#334155']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
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