from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# ฐานข้อมูลจำลอง (ในระบบจริงเชื่อมกับ Supabase PostgreSQL)
debtors_database = [
    {
        'id': '#541532',
        'username': '0944948563',
        'name': 'น้ำทิพย์ ทิมทอง',
        'phone': '0944948563',
        'acc': '0173271891',
        'bank': 'ธนาคารกสิกรไทย',
        'requested_amount': 50000,
        'total': 52500,
        'date': '29/10/2026 20:05',
        'ip': '2407:b1c0:dc2:c588:d1a',
        'status': 'ปกติ',
        'slip': 'slip_sample.jpg',
        'signature': 'signature_sample.png',
        'remark': 'ลูกค้าประวัติเดิม ชำระตรงเวลา'
    }
]

# --- 1. หน้าหลังบ้านสำหรับแอดมิน (BizFlow+ Dashboard) ---
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ - ระบบจัดการหลังบ้านแอดมิน</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Kanit', sans-serif; background-color: #f8fafc; } </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex">

    <!-- Sidebar -->
    <aside class="w-72 bg-gradient-to-b from-purple-950 via-slate-900 to-indigo-950 text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl min-h-screen border-r border-purple-900/40">
        <div class="p-6">
            <div class="flex items-center space-x-3.5 pb-6 border-b border-purple-900/40">
                <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 to-violet-400 flex items-center justify-center text-white font-black text-2xl shadow-lg">B</div>
                <div>
                    <h1 class="text-xl font-black text-white">BizFlow <span class="text-purple-400 text-xs px-1.5 py-0.5 bg-purple-900/60 rounded">PLUS</span></h1>
                    <p class="text-xs text-purple-300/70">ระบบบริหารจัดการเงินกู้ & IP Audit</p>
                </div>
            </div>
            <nav class="mt-6 space-y-2">
                <a href="/" class="flex items-center space-x-3 px-4 py-3 rounded-xl bg-purple-600/30 border border-purple-500/40 text-purple-200 font-medium text-sm">
                    <i class="fa-solid fa-users text-purple-400 w-5"></i>
                    <span>จัดการลูกหนี้ & ตรวจสอบ IP</span>
                </a>
                <a href="/apply" target="_blank" class="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-purple-900/30 text-slate-300 font-medium text-sm transition-all">
                    <i class="fa-solid fa-globe text-emerald-400 w-5"></i>
                    <span>🔗 เปิดหน้าบ้าน (ให้ลูกค้ากรอกกู้)</span>
                </a>
            </nav>
        </div>
        <div class="p-4 border-t border-purple-900/40 text-xs text-purple-300/60">
            Supabase DB: Connected (`debtor-files`)
        </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-8">
        <header class="flex justify-between items-center mb-6">
            <div>
                <h2 class="text-2xl font-bold text-slate-800">รายชื่อลูกค้าที่ยื่นกู้ & ทำสัญญาออนไลน์</h2>
                <p class="text-xs text-slate-500">ตรวจสอบข้อมูล IP Address, ไฟล์แนบ และลายเซ็นอิเล็กทรอนิกส์ของลูกค้า</p>
            </div>
            <a href="/apply" target="_blank" class="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-semibold shadow-md transition-all">
                <i class="fa-solid fa-external-link-alt mr-1.5"></i> ไปหน้าฟอร์มลูกค้ายื่นกู้
            </a>
        </header>

        <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-50 text-slate-500">
                    <tr>
                        <th class="p-3.5">วันที่ยื่นกู้</th>
                        <th class="p-3.5">ชื่อ-นามสกุล / เบอร์โทร</th>
                        <th class="p-3.5">ยอดขอกู้</th>
                        <th class="p-3.5">ธนาคาร / เลขบัญชี</th>
                        <th class="p-3.5">IP Address</th>
                        <th class="p-3.5 text-center">หลักฐาน/ลายเซ็น</th>
                        <th class="p-3.5 text-center">สถานะ</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for item in debtors %}
                    <tr class="hover:bg-slate-50/50">
                        <td class="p-3.5 text-xs text-slate-500">{{ item.date }}</td>
                        <td class="p-3.5">
                            <p class="font-bold text-slate-800">{{ item.name }}</p>
                            <p class="text-xs text-purple-600 font-mono"><i class="fa-solid fa-phone text-[10px]"></i> {{ item.phone }}</p>
                        </td>
                        <td class="p-3.5 font-bold text-slate-900">฿{{ "{:,}".format(item.requested_amount) }}</td>
                        <td class="p-3.5">
                            <p class="font-semibold text-slate-700">{{ item.bank }}</p>
                            <p class="text-xs font-mono text-slate-500">{{ item.acc }}</p>
                        </td>
                        <td class="p-3.5">
                            <span class="px-2 py-1 bg-purple-50 text-purple-700 font-mono text-xs rounded-lg border border-purple-200">
                                <i class="fa-solid fa-network-wired text-[10px] mr-1"></i> {{ item.ip }}
                            </span>
                        </td>
                        <td class="p-3.5 text-center space-x-1">
                            <span class="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded"><i class="fa-solid fa-file-contract"></i> เซ็นสัญญาแล้ว</span>
                        </td>
                        <td class="p-3.5 text-center">
                            <span class="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-semibold">{{ item.status }}</span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

# --- 2. หน้าบ้านสำหรับลูกค้า (Public Loan & Digital Contract Form) ---
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
    <style> 
        body { font-family: 'Kanit', sans-serif; background: linear-gradient(135deg, #18092e 0%, #0d061a 100%); min-height: 100vh; }
        canvas { touch-action: none; }
    </style>
</head>
<body class="py-12 px-4 flex items-center justify-center">
    <div class="max-w-2xl w-full bg-white rounded-3xl shadow-2xl p-8 border border-purple-100">
        <div class="text-center mb-8">
            <div class="w-14 h-14 bg-gradient-to-tr from-purple-600 to-violet-400 rounded-2xl mx-auto flex items-center justify-center text-white text-2xl font-black shadow-lg shadow-purple-500/30 mb-3">
                <i class="fa-solid fa-file-signature"></i>
            </div>
            <h1 class="text-2xl font-black text-slate-900">แบบฟอร์มยื่นกู้ & ทำสัญญาออนไลน์</h1>
            <p class="text-xs text-slate-500 mt-1">กรอกข้อมูลส่วนตัว ระบุวงเงิน และเซ็นสัญญาอิเล็กทรอนิกส์เพื่อส่งเข้าระบบ</p>
        </div>

        <form action="/submit-application" method="POST" class="space-y-5" onsubmit="prepareSignature()">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">ชื่อ - นามสกุลจริง</label>
                    <input type="text" name="name" required placeholder="เช่น สมชาย ใจดี" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">เบอร์โทรศัพท์ (ใช้เข้าระบบ)</label>
                    <input type="text" name="phone" required placeholder="0891234567" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-semibold text-purple-700">
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">ธนาคารรับเงิน</label>
                    <select name="bank" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-medium">
                        <option value="ธนาคารกสิกรไทย">ธนาคารกสิกรไทย (KBANK)</option>
                        <option value="ธนาคารไทยพาณิชย์">ธนาคารไทยพาณิชย์ (SCB)</option>
                        <option value="ธนาคารกรุงเทพ">ธนาคารกรุงเทพ (BBL)</option>
                        <option value="ธนาคารกรุงไทย">ธนาคารกรุงไทย (KTB)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1.5">เลขที่บัญชี</label>
                    <input type="text" name="account" required placeholder="ระบุเลขบัญชีธนาคาร" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-mono">
                </div>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1.5">ยอดเงินที่ต้องการขอกู้ (บาท)</label>
                <input type="number" name="amount" required placeholder="ระบุจำนวนเงิน เช่น 10000" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-purple-600 font-bold text-slate-900 text-lg">
            </div>

            <!-- กล่องข้อความสัญญาเงินกู้ -->
            <div class="p-4 bg-purple-50/60 border border-purple-100 rounded-2xl text-xs text-slate-600 space-y-1.5">
                <p class="font-bold text-purple-900"><i class="fa-solid fa-circle-info mr-1"></i> เงื่อนไขสัญญาเงินกู้:</p>
                <p>ข้าพเจ้ายอมรับว่าข้อมูลดังกล่าวเป็นความจริง และตกลงยินยอมชำระดอกเบี้ยตามกำหนด หากผิดนัดชำระยินยอมให้ดำเนินคดีตามกฎหมาย ระบบจะทำการบันทึก IP Address ของท่านไว้เป็นหลักฐาน</p>
            </div>

            <!-- ส่วนเซ็นสัญญาออนไลน์ (Digital Signature Canvas) -->
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1.5">ลงลายมือชื่ออิเล็กทรอนิกส์ (ใช้นิ้วหรือเมาส์เซ็นในกรอบ)</label>
                <div class="border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50 p-2 relative">
                    <canvas id="sig-canvas" width="550" height="150" class="w-full bg-white rounded-xl cursor-crosshair shadow-inner"></canvas>
                    <button type="button" onclick="clearSignature()" class="absolute bottom-4 right-4 px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold rounded-lg">ล้างลายเซ็น</button>
                </div>
                <input type="hidden" name="signature_data" id="signature_data">
            </div>

            <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl font-bold text-base shadow-lg shadow-purple-500/30 transition-all">
                ยืนยันการยื่นกู้และส่งสัญญา
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

        function clearSignature() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function prepareSignature() {
            const dataURL = canvas.toDataURL('image/png');
            document.getElementById('signature_data').value = dataURL;
        }
    </script>
</body>
</html>
"""

# --- Routes สำหรับจัดการหลังบ้านและรับข้อมูลจากลูกค้า ---
@app.route('/')
def admin_dashboard():
    return render_template_string(ADMIN_TEMPLATE, debtors=debtors_database)

@app.route('/apply')
def apply_form():
    return render_template_string(APPLY_TEMPLATE)

@app.route('/submit-application', methods=['POST'])
def submit_application():
    # ดึง IP Address ของลูกค้าที่เข้ามาใช้งานอัตโนมัติ
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    name = request.form.get('name')
    phone = request.form.get('phone')
    bank = request.form.get('bank')
    account = request.form.get('account')
    amount = float(request.form.get('amount') or 0)
    
    # บันทึกลงฐานข้อมูลจำลอง (สามารถปรับเปลี่ยนไปบันทึกลง Supabase Table ได้ทันที)
    new_entry = {
        'id': f"#{len(debtors_database)+541540}",
        'username': phone,
        'name': name,
        'phone': phone,
        'acc': account,
        'bank': bank,
        'requested_amount': amount,
        'total': amount * 1.05, # ตัวอย่างคำนวณดอกเบี้ย
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'ip': client_ip,
        'status': 'รออนุมัติ',
        'slip': 'user_upload_slip.jpg',
        'signature': 'saved_signature.png',
        'remark': 'ลูกค้ายื่นกู้ผ่านเว็บและเซ็นสัญญาออนไลน์แล้ว'
    }
    debtors_database.insert(0, new_entry)
    
    return """
    <script>
        alert('ยื่นคำขอกู้และส่งสัญญาออนไลน์สำเร็จเรียบร้อย!');
        window.location.href = '/apply';
    </script>
    """

if __name__ == '__main__':
    app.run(debug=True)
