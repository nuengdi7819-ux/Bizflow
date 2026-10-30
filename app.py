<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ ระบบบริหารสินเชื่อ & สัญญาเงินกู้แบบมืออาชีพ</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Prompt', sans-serif; background-color: #0b0f19; color: #f3f4f6; }
        @keyframes breathing {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
            50% { transform: scale(1.01); box-shadow: 0 0 35px rgba(16, 185, 129, 0.4); }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
        }
        @keyframes breathing-blue {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); }
            50% { transform: scale(1.01); box-shadow: 0 0 35px rgba(59, 130, 246, 0.4); }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); }
        }
        .breathing-card-green { animation: breathing 4s ease-in-out infinite; }
        .breathing-card-blue { animation: breathing-blue 4s ease-in-out infinite; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #111827; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
    </style>
</head>
<body class="flex h-screen overflow-hidden">

    <!-- 1. SIDEBAR (Fixed Sidebar) -->
    <aside class="w-64 bg-[#111827] border-r border-gray-800 flex flex-col z-20 flex-shrink-0 h-full">
        <!-- Logo Area -->
        <div class="p-5 border-b border-gray-800 flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-purple-500/30">B</div>
            <div>
                <h1 class="font-bold text-lg tracking-wide text-white flex items-center gap-1.5">
                    BizFlow <span class="bg-purple-600/30 text-purple-400 text-xs px-2 py-0.5 rounded-full border border-purple-500/30">PLUS</span>
                </h1>
                <p class="text-xs text-gray-400">ระบบจัดการลูกหนี้ & บัญชี</p>
            </div>
        </div>

        <!-- Navigation Menu -->
        <div class="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6 text-sm">
            <div>
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-3">1. ภาพรวม & การเงิน</p>
                <div class="space-y-1">
                    <button onclick="switchView('dashboard')" id="nav-dashboard" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-purple-400 bg-purple-500/10 border border-purple-500/20 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 13a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1v-7z"></path></svg>
                        แดชบอร์ดหลัก
                    </button>
                    <button onclick="openModal('bankModal')" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"></path></svg>
                        บัญชีธนาคาร & พื้นที่ส่วนตัว
                    </button>
                </div>
            </div>

            <div>
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-3">2. จัดการลูกหนี้ & คำขอกู้</p>
                <div class="space-y-1">
                    <button onclick="openModal('customerListModal')" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                        รายชื่อลูกหนี้ทั้งหมด
                    </button>
                    <button onclick="openModal('otpManageModal')" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                        อนุมัติรหัส OTP ลูกค้า <span id="otpBadge" class="ml-auto bg-amber-500/20 text-amber-400 text-xs px-2 py-0.5 rounded-full">0</span>
                    </button>
                    <button onclick="switchView('clientApply')" id="nav-client" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
                        หน้าบ้านสมาชิก (/apply)
                    </button>
                </div>
            </div>

            <div>
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-3">3. รายงาน & ตั้งค่า</p>
                <div class="space-y-1">
                    <button onclick="openModal('annualReportModal')" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                        รายงานผลประกอบการประจำปี
                    </button>
                    <button onclick="openModal('settingsModal')" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path></svg>
                        ตั้งค่าระบบหลังบ้าน & Telegram
                    </button>
                </div>
            </div>
        </div>
    </aside>

    <!-- MAIN CONTENT AREA (Scrollable) -->
    <main class="flex-1 flex flex-col h-full overflow-y-auto custom-scrollbar">
        <!-- Top Navigation Bar -->
        <header class="bg-[#111827]/80 backdrop-blur border-b border-gray-800 sticky top-0 z-10 px-8 py-4 flex items-center justify-between">
            <div>
                <h2 class="text-xl font-bold text-white">BizFlow+ แดชบอร์ดบริหารสินเชื่อ</h2>
                <p class="text-xs text-emerald-400 flex items-center gap-1.5 mt-0.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> ระบบพร้อมใช้งาน (เรียลไทม์)
                </p>
            </div>
            <div class="flex items-center gap-3">
                <button onclick="copyApplyLink()" class="bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                    คัดลอกลิงก์ยื่นกู้ (/apply)
                </button>
                <button onclick="openModal('addEntryModal')" class="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2 shadow-lg shadow-purple-600/30 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    + เพิ่มรายการใหม่ (แอดมิน)
                </button>
                <button onclick="switchView('clientApply')" class="bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    จำลองยื่นหน้าบ้าน
                </button>
            </div>
        </header>

        <!-- DASHBOARD VIEW -->
        <div id="view-dashboard" class="p-8 space-y-8">
            <!-- Control Banner -->
            <div class="bg-gradient-to-r from-purple-900/40 via-gray-900 to-indigo-900/40 border border-purple-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
                <div class="flex items-center gap-4">
                    <div class="p-3 bg-purple-600/20 border border-purple-500/40 rounded-xl text-purple-400">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                    </div>
                    <div>
                        <h3 class="font-bold text-white text-lg">แผงควบคุมการบันทึกข้อมูลด่วน (Admin Control Panel)</h3>
                        <p class="text-sm text-gray-400">บันทึกปล่อยกู้ใหม่ หรือบันทึกยอดค้างเก่าเข้าสู่ระบบแบบเรียลไทม์โดยตรง</p>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <button onclick="copyApplyLink()" class="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 px-4 py-2.5 rounded-xl text-sm font-medium transition flex items-center gap-2">
                        คัดลอกส่งลิงก์ลูกค้า
                    </button>
                    <button onclick="openModal('addEntryModal')" class="bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl text-sm font-medium shadow-lg shadow-purple-600/30 transition flex items-center gap-2">
                        + บันทึกรายการใหม่
                    </button>
                </div>
            </div>

            <!-- Dual Hero Cards & Net Cashflow -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Hero Inflow -->
                <div onclick="openDrilldown('inflow')" class="bg-[#111827] border-2 border-emerald-500/50 rounded-3xl p-6 breathing-card-green cursor-pointer hover:border-emerald-400 transition relative">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs font-semibold px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">กระแสเงินสดรับเข้าวันนี้ (Cash Inflow)</span>
                        <span class="text-xs text-emerald-400 animate-pulse font-medium">LIVE UPDATE</span>
                    </div>
                    <h2 class="text-xl font-bold text-white">ยอดเก็บสดวันนี้</h2>
                    <p class="text-xs text-gray-400 mb-6">รวมทุกรายการตัดดอก/ตัดต้น/ยอดค้างเก่าที่รับชำระเข้ามาวันนี้</p>
                    <div class="bg-gray-900/80 border border-emerald-500/20 rounded-2xl p-5 flex items-center justify-between">
                        <span class="text-sm text-gray-400">ยอดรวมรับชำระวันนี้สุทธิ</span>
                        <span id="stat-inflow" class="text-3xl font-extrabold text-emerald-400">฿ 18,500.00</span>
                    </div>
                    <div class="flex items-center justify-between mt-4 text-xs text-gray-400">
                        <span>รับชำระแล้ว: <strong class="text-white">6 รายการ</strong></span>
                        <span class="text-emerald-400 hover:underline">คลิกเพื่อดูรายละเอียด ➔</span>
                    </div>
                </div>

                <!-- Hero Outflow -->
                <div onclick="openDrilldown('outflow')" class="bg-[#111827] border-2 border-blue-500/50 rounded-3xl p-6 breathing-card-blue cursor-pointer hover:border-blue-400 transition relative">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs font-semibold px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full border border-blue-500/30">เงินทุนปล่อยออกวันนี้ (Capital Outflow)</span>
                        <span class="text-xs text-blue-400 animate-pulse font-medium">LIVE UPDATE</span>
                    </div>
                    <h2 class="text-xl font-bold text-white">ยอดลงทุนวันนี้</h2>
                    <p class="text-xs text-gray-400 mb-6">รวมยอดเงินต้นที่อนุมัติปล่อยกู้ใหม่และโอนออกในวันนี้ทั้งหมด</p>
                    <div class="bg-gray-900/80 border border-blue-500/20 rounded-2xl p-5 flex items-center justify-between">
                        <span class="text-sm text-gray-400">ยอดรวมเงินต้นที่โอนปล่อยกู้วันนี้</span>
                        <span id="stat-outflow" class="text-3xl font-extrabold text-blue-400">฿ 15,000.00</span>
                    </div>
                    <div class="flex items-center justify-between mt-4 text-xs text-gray-400">
                        <span>สัญญากู้Yอนุมัติวันนี้: <strong class="text-white">2 รายการ</strong></span>
                        <span class="text-blue-400 hover:underline">คลิกเพื่อบันทึกโอนยอด ➔</span>
                    </div>
                </div>
            </div>

            <!-- Net Cashflow Bar -->
            <div onclick="openDrilldown('netflow')" class="bg-[#111827] border border-gray-800 rounded-2xl p-5 flex flex-col md:flex-row items-center justify-between gap-4 cursor-pointer hover:border-gray-700 transition">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-purple-600/20 text-purple-400 rounded-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                    </div>
                    <div>
                        <h4 class="font-semibold text-white text-sm">ดุลกระแสเงินสดสุทธิวันนี้ (Net Cashflow)</h4>
                        <p class="text-xs text-gray-400">( ยอดเก็บสดวันนี้ ฿18,500 - ยอดลงทุนปล่อยกู้ ฿15,000 )</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="text-xs text-gray-400 block">คงเหลือเงินสดส่วนต่างหมุนเวียน</span>
                    <span class="text-xl font-bold text-emerald-400">+ ฿ 3,500.00</span>
                </div>
            </div>

            <!-- Secondary KPI Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Card 1: Old Arrears -->
                <div onclick="openDrilldown('arrears')" class="bg-[#111827] border border-gray-800 rounded-2xl p-6 cursor-pointer hover:border-gray-700 transition relative">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs text-gray-400 font-medium">ยอดค้างสะสมเดิม</span>
                        <div class="p-2 bg-red-500/10 text-red-400 rounded-xl"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>
                    </div>
                    <h3 class="text-2xl font-extrabold text-white mb-2">฿ 12,500.00</h3>
                    <p class="text-xs text-gray-500">คงค้างไว้ตลอดเวลาจนกว่าจะเคลียร์หมด (ไม่รีเซ็ต)</p>
                    <div class="mt-4 pt-4 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-400">
                        <span>ลูกหนี้ยอดค้าง</span>
                        <span class="text-red-400 font-medium">ดูรายชื่อ ➔</span>
                    </div>
                </div>

                <!-- Card 2: Principal -->
                <div onclick="openDrilldown('principal')" class="bg-[#111827] border border-gray-800 rounded-2xl p-6 cursor-pointer hover:border-gray-700 transition relative">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs text-gray-400 font-medium">รวมเงินต้นที่ยังไม่ถูกปิด</span>
                        <div class="p-2 bg-blue-500/10 text-blue-400 rounded-xl"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"></path></svg></div>
                    </div>
                    <h3 class="text-2xl font-extrabold text-white mb-2">฿ 85,000.00</h3>
                    <p class="text-xs text-gray-500">คำนวณตามเงินต้นคงเหลือจริง ณ ปัจจุบัน</p>
                    <div class="mt-4 pt-4 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-400">
                        <span>สัญญาแอคทีฟ</span>
                        <span class="text-blue-400 font-medium">ดูรายชื่อ ➔</span>
                    </div>
                </div>

                <!-- Card 3: Monthly Profit -->
                <div onclick="openDrilldown('profit')" class="bg-[#111827] border border-gray-800 rounded-2xl p-6 cursor-pointer hover:border-gray-700 transition relative">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs text-gray-400 font-medium">ดอกเบี้ย + ค่าปรับ + ค้างเก่า - ส่วนลด</span>
                        <div class="p-2 bg-amber-500/10 text-amber-400 rounded-xl"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>
                    </div>
                    <h3 class="text-2xl font-extrabold text-white mb-2">฿ 8,450.00</h3>
                    <p class="text-xs text-amber-400/90 font-medium">✨ จะรีเซ็ตเป็น 0 ใหม่ทุกวันที่ 1 ของเดือนอัตโนมัติ</p>
                    <div class="mt-4 pt-4 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-400">
                        <span>รายรับสุทธิรอบนี้</span>
                        <span class="text-amber-400 font-medium">ดูรายงาน ➔</span>
                    </div>
                </div>
            </div>

            <!-- Two Columns Tables Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Column 1: Today's Transactions Tracker -->
                <div class="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
                            <div>
                                <h3 class="font-bold text-white text-base flex items-center gap-2">
                                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                                    ช่องที่ 1: รายการธุรกรรมวันนี้
                                </h3>
                                <p class="text-xs text-gray-400 mt-0.5">แสดงความเคลื่อนไหวทั้งหมดที่เกิดขึ้นในวันนี้แบบเรียลไทม์</p>
                            </div>
                            <!-- Filter Tabs -->
                            <div class="flex items-center gap-1.5 bg-gray-900 p-1 rounded-xl border border-gray-800 text-xs">
                                <button onclick="filterTransactions('all')" id="filter-all" class="px-3 py-1.5 rounded-lg bg-purple-600 text-white font-medium transition">ทั้งหมด</button>
                                <button onclick="filterTransactions('payment')" id="filter-payment" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">ตัดยอดวันนี้</button>
                                <button onclick="filterTransactions('approved')" id="filter-approved" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">อนุมัติวันนี้</button>
                                <button onclick="filterTransactions('pending')" id="filter-pending" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">รออนุมัติ</button>
                            </div>
                        </div>

                        <div class="bg-purple-900/20 border border-purple-500/30 text-purple-300 text-xs px-3 py-2 rounded-xl mb-4 flex items-center justify-between">
                            <span>📌 เรียงลำดับอัตโนมัติ: ตัดยอดชำระวันนี้ ➔ คำขอกู้ที่อนุมัติแล้ว ➔ คำขอที่รออนุมัติ</span>
                            <span class="text-purple-400 font-semibold">Realtime</span>
                        </div>

                        <!-- Transaction Items List -->
                        <div class="space-y-3" id="transaction-list">
                            <!-- Item 1: Payment -->
                            <div class="bg-gray-900/80 border border-gray-800 hover:border-gray-700 p-4 rounded-xl flex items-center justify-between gap-3 transition" data-type="payment">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">🟢</div>
                                    <div>
                                        <h4 class="font-bold text-white text-sm">สมชาย ใจดี <span class="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded ml-2">ชำระตัดยอด</span></h4>
                                        <p class="text-xs text-gray-400">ตัดดอกเบี้ย ฿200 / ตัดเงินต้น ฿300 • 17:30 น.</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <span class="text-emerald-400 font-bold block text-sm">+ ฿ 500.00</span>
                                    <button onclick="openClientHistory('สมชาย ใจดี')" class="text-xs text-purple-400 hover:underline">ดูประวัติ</button>
                                </div>
                            </div>

                            <!-- Item 2: Approved -->
                            <div class="bg-gray-900/80 border border-gray-800 hover:border-gray-700 p-4 rounded-xl flex items-center justify-between gap-3 transition" data-type="approved">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">🔵</div>
                                    <div>
                                        <h4 class="font-bold text-white text-sm">นพดล คงคา <span class="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded ml-2">อนุมัติสัญญาแล้ว</span></h4>
                                        <p class="text-xs text-gray-400">เงินต้น ฿5,000 (ดอกลอย 4%/วัน) • 14:15 น.</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <span class="text-blue-400 font-bold block text-sm">฿ 5,000.00</span>
                                    <span class="text-xs text-gray-500">เริ่มคิดดอกวันพรุ่งนี้</span>
                                </div>
                            </div>

                            <!-- Item 3: Pending -->
                            <div class="bg-gray-900/80 border border-gray-800 hover:border-gray-700 p-4 rounded-xl flex items-center justify-between gap-3 transition" data-type="pending">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">🟡</div>
                                    <div>
                                        <h4 class="font-bold text-white text-sm">วิชัย ร่ำรวย <span class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded ml-2">คำขอกู้รออนุมัติ</span></h4>
                                        <p class="text-xs text-gray-400">ขอกู้เงินต้น ฿3,000 • ลิงก์ FB พร้อม • ลายเซ็นแนบแล้ว</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <button onclick="openModal('reviewModal')" class="bg-purple-600 hover:bg-purple-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium shadow transition">ตรวจอนุมัติ</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-800 text-center">
                        <button onclick="openDrilldown('all-transactions')" class="text-xs text-gray-400 hover:text-white transition">ดูประวัติรายการธุรกรรมทั้งหมด ➔</button>
                    </div>
                </div>

                <!-- Column 2: Today's Collection Due List -->
                <div class="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="font-bold text-white text-base flex items-center gap-2">
                                    <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                    ช่องที่ 2: รายการตามเก็บยอดวันนี้
                                </h3>
                                <p class="text-xs text-gray-400 mt-0.5">ลูกหนี้ที่ถึงกำหนดต้องตามเก็บเงินในวันนี้</p>
                            </div>
                            <span class="text-xs font-semibold px-2.5 py-1 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">3 รายการ</span>
                        </div>

                        <!-- Collection Due Items -->
                        <div class="space-y-3">
                            <!-- Due 1 -->
                            <div class="bg-gray-900/80 border border-gray-800 p-4 rounded-xl flex items-center justify-between gap-3">
                                <div>
                                    <h4 class="font-bold text-white text-sm flex items-center gap-2">
                                        มานี มีเงิน 
                                        <span class="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full">จ่ายทุกวัน</span>
                                    </h4>
                                    <p class="text-xs text-gray-400">ยอดเงินต้นกู้: ฿5,000</p>
                                </div>
                                <button onclick="openPaymentModal('มานี มีเงิน', 5000)" class="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-xl text-xs font-medium shadow flex items-center gap-1.5 transition">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                    บันทึกรับชำระ
                                </button>
                            </div>

                            <!-- Due 2 -->
                            <div class="bg-gray-900/80 border border-gray-800 p-4 rounded-xl flex items-center justify-between gap-3">
                                <div>
                                    <h4 class="font-bold text-white text-sm flex items-center gap-2">
                                        สมศักดิ์ รักเรียน 
                                        <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full">รอบ 29-2</span>
                                    </h4>
                                    <p class="text-xs text-gray-400">ยอดเงินต้นกู้: ฿10,000</p>
                                </div>
                                <button onclick="openPaymentModal('สมศักดิ์ รักเรียน', 10000)" class="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-xl text-xs font-medium shadow flex items-center gap-1.5 transition">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                    บันทึกรับชำระ
                                </button>
                            </div>

                            <!-- Due 3 -->
                            <div class="bg-gray-900/80 border border-gray-800 p-4 rounded-xl flex items-center justify-between gap-3">
                                <div>
                                    <h4 class="font-bold text-white text-sm flex items-center gap-2">
                                        ท้องเกียรติ ยอดค้าง 
                                        <span class="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">ยอดค้างเก่า</span>
                                    </h4>
                                    <p class="text-xs text-gray-400">ยอดค้างเดิม: ฿2,500</p>
                                </div>
                                <button onclick="openPaymentModal('ท้องเกียรติ ยอดค้าง', 2500, true)" class="bg-red-600 hover:bg-red-500 text-white px-3.5 py-2 rounded-xl text-xs font-medium shadow flex items-center gap-1.5 transition">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                                    เก็บยอดค้าง
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-800 text-xs text-gray-500 flex items-center justify-center gap-1.5">
                        <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        การชำระทุกรายการจะถูกนำไป ตัดดอกเบี้ยก่อนเงินต้นเสมอ
                    </div>
                </div>
            </div>
        </div>

        <!-- CLIENT APPLY VIEW (/apply) -->
        <div id="view-client" class="p-8 hidden max-w-3xl mx-auto w-full">
            <div class="bg-[#111827] border border-gray-800 rounded-3xl p-8 shadow-2xl">
                <div class="text-center mb-8">
                    <div class="w-14 h-14 bg-purple-600/20 text-purple-400 border border-purple-500/30 rounded-2xl flex items-center justify-center mx-auto mb-3 font-bold text-2xl">📝</div>
                    <h2 class="text-2xl font-bold text-white">ยื่นคำขอกู้เงินออนไลน์ & ทำสัญญา</h2>
                    <p class="text-sm text-gray-400 mt-1">กรอกข้อมูลเบอร์โทรศัพท์เพื่อตรวจสอบสมาชิก และยืนยันตัวตนผ่าน OTP</p>
                </div>

                <!-- Step 1: Phone & OTP Gate -->
                <div id="client-step-1" class="space-y-5">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-2">เบอร์โทรศัพท์มือถือ *</label>
                        <div class="flex gap-3">
                            <input type="tel" id="otp-phone" placeholder="0891234567" class="flex-1 bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm focus:border-purple-500 focus:outline-none">
                            <button onclick="requestOTP()" class="bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-xl text-sm font-medium transition shadow-lg shadow-purple-600/30">ขอรหัส OTP</button>
                        </div>
                    </div>

                    <div id="otp-verify-box" class="hidden space-y-4 pt-4 border-t border-gray-800">
                        <div>
                            <label class="block text-xs font-semibold text-amber-400 uppercase mb-2">กรอกรหัส OTP 6 หลัก (ส่งแจ้งเตือนหาแอดมินทาง Telegram แล้ว)</label>
                            <input type="text" id="otp-code" placeholder="123456" maxlength="6" class="w-full bg-gray-900 border border-amber-500/50 rounded-xl px-4 py-3 text-white text-center tracking-widest text-lg font-bold focus:outline-none">
                        </div>
                        <button onclick="verifyOTP()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-3.5 rounded-xl text-sm font-medium transition shadow-lg shadow-emerald-600/30">ยืนยัน OTP เพื่อเข้ากรอกสัญญา</button>
                    </div>
                </div>

                <!-- Step 2: Full Application Form -->
                <div id="client-step-2" class="hidden space-y-6 pt-4">
                    <div class="bg-purple-900/20 border border-purple-500/30 p-4 rounded-xl text-xs text-purple-300 flex items-center gap-3">
                        <span class="text-lg">💡</span>
                        <span>ระบบตรวจพบสมาชิกเก่า: ดึงข้อมูลเดิมให้อัตโนมัติและไม่บังคับแนบรูปบัตรประชาชน</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">ชื่อ - นามสกุลจริง *</label>
                            <input type="text" id="apply-name" value="สมชาย ใจดี" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">เบอร์โทรศัพท์ (ยืนยันแล้ว)</label>
                            <input type="text" id="apply-phone-display" disabled class="w-full bg-gray-900/50 border border-gray-800 rounded-xl px-4 py-3 text-gray-400 text-sm">
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">ลิงก์ Facebook *</label>
                        <input type="url" id="apply-fb" value="https://facebook.com/somchai.sample" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm focus:outline-none">
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">จำนวนเงินต้นที่ขอกู้ (บาท) *</label>
                            <input type="number" id="apply-amount" value="5000" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">ระบบกำหนดการจ่าย *</label>
                            <select class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm focus:outline-none">
                                <option>จ่ายทุกวัน (ทวงทุกวัน)</option>
                                <option>กำหนดจ่ายประจำเดือน (รอบ 29-2)</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1.5">แนบไฟล์รูปถ่ายบัตรประชาชน (บังคับเฉพาะลูกค้าใหม่)</label>
                        <input type="file" class="w-full text-xs text-gray-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-600 file:text-white hover:file:bg-purple-500 bg-gray-900 border border-gray-800 rounded-xl">
                    </div>

                    <!-- Interactive Canvas Signature Pad -->
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <label class="block text-xs font-semibold text-gray-400 uppercase">ลงลายเซ็นอิเล็กทรอนิกส์ *</label>
                            <button type="button" onclick="clearSignature()" class="text-xs text-red-400 hover:underline">ล้างลายเซ็น</button>
                        </div>
                        <div class="border border-gray-800 rounded-xl bg-gray-900 overflow-hidden relative">
                            <canvas id="sigCanvas" class="w-full h-36 cursor-crosshair touch-none"></canvas>
                            <div id="sigPlaceholder" class="absolute inset-0 flex items-center justify-center text-gray-600 text-sm pointer-events-none">
                                [ ใช้นิ้วลากหรือเมาส์เซ็นชื่อตรงนี้ ]
                            </div>
                        </div>
                    </div>

                    <button onclick="submitLoanApplication()" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white py-4 rounded-xl font-bold text-base shadow-xl shadow-purple-600/30 transition">
                        ส่งคำขอกู้เงินและทำสัญญาออนไลน์ ➔
                    </button>
                </div>
            </div>
        </div>
    </main>

    <!-- MODALS CONTAINER -->
    <!-- Drilldown / History Modal -->
    <div id="drilldownModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-gray-800 flex items-center justify-between">
                <h3 id="drilldown-title" class="font-bold text-white text-lg">รายละเอียดข้อมูลธุรกรรม</h3>
                <button onclick="closeModal('drilldownModal')" class="text-gray-400 hover:text-white p-1">✕</button>
            </div>
            <div class="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-4" id="drilldown-content">
                <!-- Dynamic Content injected via JS -->
            </div>
            <div class="p-4 border-t border-gray-800 text-right">
                <button onclick="closeModal('drilldownModal')" class="bg-gray-800 hover:bg-gray-700 text-white px-5 py-2 rounded-xl text-sm font-medium">ปิดหน้าต่าง</button>
            </div>
        </div>
    </div>

    <!-- Admin Manual Entry Modal (+ เพิ่มรายการใหม่) -->
    <div id="addEntryModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-gray-800 flex items-center justify-between">
                <h3 class="font-bold text-white text-lg">➕ บันทึกรายการใหม่ / ยอดค้างเก่า (แอดมิน)</h3>
                <button onclick="closeModal('addEntryModal')" class="text-gray-400 hover:text-white p-1">✕</button>
            </div>
            <div class="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-5 text-sm">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">วันที่ทำสัญญา / เริ่มรายการ</label>
                        <input type="date" id="admin-date" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">ประเภทรายการ</label>
                        <select id="admin-entry-type" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                            <option value="loan">รายการปล่อยกู้ใหม่</option>
                            <option value="arrear">ยอดค้างเก่ายกมา</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">ชื่อลูกหนี้ / ค้นหาเบอร์โทรศัพท์</label>
                    <input type="text" placeholder="ระบุชื่อ หรือค้นหาเบอร์โทรเดิม..." class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">ลิงก์ Facebook ลูกค้า</label>
                    <input type="url" placeholder="https://facebook.com/..." class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">จำนวนเงินต้น (บาท)</label>
                        <input type="number" id="admin-principal" value="5000" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">ประเภทดอกเบี้ย</label>
                        <select class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white">
                            <option>ดอกลอย (คิดตาม % ต้นคงเหลือ)</option>
                            <option>จบต้นดอก (รันค่างวด)</option>
                        </select>
                    </div>
                </div>

                <!-- Toggles -->
                <div class="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-3">
                    <div class="flex items-center justify-between">
                        <div>
                            <h4 class="font-bold text-white text-xs">ล็อกดอกเบี้ยตายตัว (Fixed Interest)</h4>
                            <p class="text-[11px] text-gray-400">คิดดอกคงที่ทุกวันแม้เงินต้นลด</p>
                        </div>
                        <input type="checkbox" class="w-4 h-4 accent-purple-600">
                    </div>
                    <div class="flex items-center justify-between pt-2 border-t border-gray-800">
                        <div>
                            <h4 class="font-bold text-white text-xs">เริ่มคิดดอกเบี้ยวันถัดไป (Next Day Interest)</h4>
                            <p class="text-[11px] text-gray-400">วันนี้ (Day 0) ฟรีดอกเบี้ย เริ่มคิดวันพรุ่งนี้</p>
                        </div>
                        <input type="checkbox" checked class="w-4 h-4 accent-purple-600" id="admin-nextday">
                    </div>
                </div>
            </div>
            <div class="p-4 border-t border-gray-800 flex items-center justify-end gap-3">
                <button onclick="closeModal('addEntryModal')" class="bg-gray-800 hover:bg-gray-700 text-white px-5 py-2.5 rounded-xl text-sm font-medium">ยกเลิก</button>
                <button onclick="saveAdminEntry()" class="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2.5 rounded-xl text-sm font-medium shadow-lg shadow-purple-600/30">บันทึกเข้าระบบ</button>
            </div>
        </div>
    </div>

    <!-- Payment Modal -->
    <div id="paymentModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-md flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-gray-800 flex items-center justify-between">
                <h3 class="font-bold text-white text-base" id="paymentModalTitle">บันทึกรับชำระเงิน</h3>
                <button onclick="closeModal('paymentModal')" class="text-gray-400 hover:text-white p-1">✕</button>
            </div>
            <div class="p-6 space-y-4 text-sm">
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">ยอดเงินที่ชำระเข้ามา (บาท)</label>
                    <input type="number" id="pay-amount" value="500" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-white text-lg font-bold">
                </div>
                <div class="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs p-3 rounded-xl">
                    ⚠️ ระบบจะทำการ **ตัดชำระดอกเบี้ยค้างสะสมให้หมดก่อนเสมอ** หากมีเงินเหลือจึงนำไปตัดเงินต้น
                </div>
            </div>
            <div class="p-4 border-t border-gray-800 flex items-center justify-end gap-3">
                <button onclick="closeModal('paymentModal')" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-xl text-sm">ยกเลิก</button>
                <button onclick="confirmPayment()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-xl text-sm font-medium shadow">ยืนยันรับชำระเงิน</button>
            </div>
        </div>
    </div>

    <!-- Settings Modal (Telegram & Back-end config) -->
    <div id="settingsModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-lg flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-gray-800 flex items-center justify-between">
                <h3 class="font-bold text-white text-lg">⚙️ ตั้งค่า Telegram Bot & ระบบหลังบ้าน</h3>
                <button onclick="closeModal('settingsModal')" class="text-gray-400 hover:text-white p-1">✕</button>
            </div>
            <div class="p-6 space-y-4 text-sm">
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Telegram Bot Token</label>
                    <input type="text" id="tg-token" value="750000000:AAHxxxxxx..." class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white font-mono text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Telegram Chat ID</label>
                    <input type="text" id="tg-chatid" value="-100123456789" class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2.5 text-white font-mono text-xs">
                </div>
                <div class="p-4 bg-purple-900/20 border border-purple-500/30 rounded-xl text-xs text-purple-300">
                    💡 เมื่อลูกค้าขอรหัส OTP หรือยื่นคำขอกู้สำเร็จ บอท Telegram จะส่งข้อความแจ้งเตือนหาแอดมินทันทีแบบเรียลไทม์
                </div>
            </div>
            <div class="p-4 border-t border-gray-800 flex items-center justify-end gap-3">
                <button onclick="closeModal('settingsModal')" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-xl text-sm">ปิด</button>
                <button onclick="saveSettings()" class="bg-purple-600 hover:bg-purple-500 text-white px-5 py-2 rounded-xl text-sm font-medium">บันทึกการตั้งค่า</button>
            </div>
        </div>
    </div>

    <!-- Dummy modals for other menu clicks -->
    <div id="bankModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-md p-6 text-center space-y-4">
            <h3 class="font-bold text-white text-lg">🏦 บัญชีธนาคารรับโอนเงิน</h3>
            <p class="text-sm text-gray-400">บัญชีหลัก: กสิกรไทย (KBANK) - 123-4-56789-0 (คุณแอดมิน)</p>
            <button onclick="closeModal('bankModal')" class="bg-purple-600 text-white px-5 py-2 rounded-xl text-sm">ปิดหน้าต่าง</button>
        </div>
    </div>

    <div id="customerListModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-xl p-6 space-y-4">
            <h3 class="font-bold text-white text-lg">👥 รายชื่อลูกหนี้ทั้งหมดในระบบ (Active)</h3>
            <div class="space-y-2 text-sm text-left">
                <div class="bg-gray-900 p-3 rounded-xl flex justify-between items-center"><span>สมชาย ใจดี (0891234567)</span><span class="text-emerald-400">฿5,000</span></div>
                <div class="bg-gray-900 p-3 rounded-xl flex justify-between items-center"><span>นพดล คงคา (0812345678)</span><span class="text-emerald-400">฿5,000</span></div>
                <div class="bg-gray-900 p-3 rounded-xl flex justify-between items-center"><span>มานี มีเงิน (0834567890)</span><span class="text-emerald-400">฿5,000</span></div>
            </div>
            <button onclick="closeModal('customerListModal')" class="w-full bg-gray-800 text-white py-2.5 rounded-xl text-sm">ปิด</button>
        </div>
    </div>

    <div id="otpManageModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-md p-6 space-y-4">
            <h3 class="font-bold text-white text-lg">🔑 คำขออนุมัติรหัส OTP ลูกค้า</h3>
            <p class="text-sm text-gray-400" id="otp-request-status">ขณะนี้มีคำขอ OTP จากเบอร์: <strong class="text-white">0891234567</strong></p>
            <div class="bg-gray-900 p-4 rounded-xl text-center">
                <span class="text-xs text-gray-400 block mb-1">รหัส OTP 6 หลักที่สร้างให้:</span>
                <span id="generated-otp" class="text-3xl font-extrabold text-amber-400 tracking-widest">749201</span>
            </div>
            <button onclick="closeModal('otpManageModal')" class="w-full bg-purple-600 text-white py-2.5 rounded-xl text-sm font-medium">คัดลอกรหัสส่งลูกค้า / ปิด</button>
        </div>
    </div>

    <div id="annualReportModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111827] border border-gray-800 rounded-3xl w-full max-w-md p-6 text-center space-y-4">
            <h3 class="font-bold text-white text-lg">📈 รายงานผลประกอบการประจำปี</h3>
            <p class="text-sm text-gray-400">ยอดสะสมกำไรสุทธิรวมทั้งปี: <strong class="text-emerald-400">฿ 128,450.00</strong></p>
            <button onclick="closeModal('annualReportModal')" class="bg-gray-800 text-white px-5 py-2 rounded-xl text-sm">ปิด</button>
        </div>
    </div>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        // Switch Views
        function switchView(viewName) {
            if(viewName === 'dashboard') {
                document.getElementById('view-dashboard').classList.remove('hidden');
                document.getElementById('view-client').classList.add('hidden');
                document.getElementById('nav-dashboard').className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-purple-400 bg-purple-500/10 border border-purple-500/20 transition";
                document.getElementById('nav-client').className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition";
            } else if(viewName === 'clientApply') {
                document.getElementById('view-dashboard').classList.add('hidden');
                document.getElementById('view-client').classList.remove('hidden');
                document.getElementById('nav-client').className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-purple-400 bg-purple-500/10 border border-purple-500/20 transition";
                document.getElementById('nav-dashboard').className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 transition";
                initCanvas();
            }
        }

        // Modal Controls
        function openModal(modalId) {
            document.getElementById(modalId).classList.remove('hidden');
        }
        function closeModal(modalId) {
            document.getElementById(modalId).classList.add('hidden');
        }

        // Copy Link
        function copyApplyLink() {
            const dummyUrl = window.location.href.split('#')[0] + "#apply";
            navigator.clipboard.writeText(dummyUrl);
            alert("คัดลอกลิงก์ยื่นกู้เรียบร้อยแล้ว: " + dummyUrl);
        }

        // Drilldown Details
        function openDrilldown(type) {
            openModal('drilldownModal');
            const titleEl = document.getElementById('drilldown-title');
            const contentEl = document.getElementById('drilldown-content');
            
            if(type === 'inflow') {
                titleEl.textContent = "รายละเอียด: ยอดเก็บสดวันนี้ (Cash Inflow)";
                contentEl.innerHTML = `
                    <div class="space-y-3">
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>1. สมชาย ใจดี (ตัดดอก + ตัดต้น)</span><span class="text-emerald-400 font-bold">+฿500</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>2. มานี มีเงิน (จ่ายรายวัน)</span><span class="text-emerald-400 font-bold">+฿300</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>3. สมศักดิ์ รักเรียน (รอบประจำเดือน)</span><span class="text-emerald-400 font-bold">+฿1,500</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>4. สุชาติ มั่งคั่ง (เคลียร์ค้างเก่า)</span><span class="text-emerald-400 font-bold">+฿2,500</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>5. วิชัย โชคดี (จ่ายดอกเบี้ย)</span><span class="text-emerald-400 font-bold">+฿200</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>6. ประสิทธิ์ ร่ำรวย (ตัดต้นเพิ่ม)</span><span class="text-emerald-400 font-bold">+฿13,500</span></div>
                    </div>
                `;
            } else if(type === 'outflow') {
                titleEl.textContent = "รายละเอียด: ยอดลงทุนปล่อยกู้ใหม่วันนี้ (Capital Outflow)";
                contentEl.innerHTML = `
                    <div class="space-y-3">
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>1. นพดล คงคา (โอนเข้า กสิกรไทย)</span><span class="text-blue-400 font-bold">฿5,000</span></div>
                        <div class="bg-gray-900 p-3.5 rounded-xl flex justify-between items-center text-sm"><span>2. ว Eรพล ใจเด็ด (โอนเข้า ไทยพาณิชย์)</span><span class="text-blue-400 font-bold">฿10,000</span></div>
                    </div>
                `;
            } else {
                titleEl.textContent = "ประวัติรายการธุรกรรมเชิงลึก (" + type + ")";
                contentEl.innerHTML = `<p class="text-gray-400 text-sm">แสดงบันทึกรายละเอียดประวัติข้อมูลทั้งหมดของหมวดหมู่นี้ในระบบเรียบร้อยแล้ว</p>`;
            }
        }

        // Filter Transactions
        function filterTransactions(category) {
            document.querySelectorAll('#filter-all, #filter-payment, #filter-approved, #filter-pending').forEach(btn => {
                btn.className = "px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition";
            });
            document.getElementById('filter-' + category).className = "px-3 py-1.5 rounded-lg bg-purple-600 text-white font-medium transition";

            const items = document.querySelectorAll('#transaction-list > div');
            items.forEach(item => {
                if(category === 'all' || item.getAttribute('data-type') === category) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        // Payment modal trigger
        let currentPayingName = "";
        function openPaymentModal(name, amount, isArrear=false) {
            currentPayingName = name;
            document.getElementById('paymentModalTitle').textContent = "บันทึกรับชำระเงิน: " + name;
            document.getElementById('pay-amount').value = isArrear ? amount : 500;
            openModal('paymentModal');
        }
        function confirmPayment() {
            alert("บันทึกรับชำระเงินจาก " + currentPayingName + " เรียบร้อยแล้ว! ระบบตัดดอกเบี้ยก่อนและอัปเดตยอดเก็บสดวันนี้แล้ว");
            closeModal('paymentModal');
        }

        // Client OTP & Signature Logic
        function requestOTP() {
            const phone = document.getElementById('otp-phone').value;
            if(!phone) { alert("กรุณากรอกเบอร์โทรศัพท์ก่อนครับ"); return; }
            document.getElementById('otp-verify-box').classList.remove('hidden');
            document.getElementById('otpBadge').textContent = "1";
            alert("ระบบส่งรหัส OTP 749201 ไปยัง Telegram ของแอดมินเรียบร้อยแล้ว!");
        }

        function verifyOTP() {
            const code = document.getElementById('otp-code').value;
            if(code === "749201" || code.length === 6) {
                document.getElementById('client-step-1').classList.add('hidden');
                document.getElementById('client-step-2').classList.remove('hidden');
                document.getElementById('apply-phone-display').value = document.getElementById('otp-phone').value;
                alert("ยืนยัน OTP สำเร็จ! เข้าสู่หน้ากรอกสัญญาออนไลน์");
            } else {
                alert("รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่");
            }
        }

        // HTML5 Signature Canvas
        let canvas, ctx, isDrawing = false;
        function initCanvas() {
            canvas = document.getElementById('sigCanvas');
            if(!canvas) return;
            ctx = canvas.getContext('2d');
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = 140;
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.lineCap = "round";

            canvas.addEventListener('mousedown', startDraw);
            canvas.addEventListener('mousemove', drawing);
            canvas.addEventListener('mouseup', stopDraw);
            canvas.addEventListener('touchstart', (e) => { startDraw(e.touches[0]); e.preventDefault(); });
            canvas.addEventListener('touchmove', (e) => { drawing(e.touches[0]); e.preventDefault(); });
            canvas.addEventListener('touchend', stopDraw);
        }
        function startDraw(e) {
            isDrawing = true;
            document.getElementById('sigPlaceholder').style.display = 'none';
            const rect = canvas.getBoundingClientRect();
            ctx.beginPath();
            ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
        }
        function drawing(e) {
            if(!isDrawing) return;
            const rect = canvas.getBoundingClientRect();
            ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
            ctx.stroke();
        }
        function stopDraw() { isDrawing = false; }
        function clearSignature() {
            if(!ctx) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            document.getElementById('sigPlaceholder').style.display = 'flex';
        }

        function submitLoanApplication() {
            alert("ยื่นคำขอกู้เงินและส่งสัญญาสำเร็จ! ระบบส่งแจ้งเตือน Telegram หาแอดมินเรียบร้อย");
            switchView('dashboard');
        }

        function saveAdminEntry() {
            alert("บันทึกรายการใหม่เข้าสู่ระบบหลังบ้านเรียบร้อยแล้ว!");
            closeModal('addEntryModal');
        }
        function saveSettings() {
            alert("บันทึกตั้งค่า Telegram สำเร็จ!");
            closeModal('settingsModal');
        }
        function openClientHistory(name) {
            alert("เปิดหน้าประวัติบัญชีลูกหนี้ของ: " + name);
        }
    </script>
</body>
</html>
