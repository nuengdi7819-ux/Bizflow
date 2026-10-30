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
        data = response.data if response.data else []
        for d in data:
            if 'old_arrears' not in d:
                d['old_arrears'] = 0
        return data
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
        return []

pending_otp_requests = []

system_config = {
    'company_name': 'BizFlow+ Financial Services',
    'telegram_token': '9203750510:AAFJhUvWRF4mOSozUSkz0I0I9Jca-xImuTo',
    'telegram_chat_id': '1880260879'
}

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

# ----------------- หน้าบ้านยื่นกู้ (Apply Portal) -----------------
APPLY_TEMPLATE = """
<!DOCTYPE html>
<html lang="th" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizFlow+ หน้าบ้านยื่นกู้สมาชิก & ยืนยันตัวตน OTP</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = { darkMode: 'class', theme: { extend: { colors: { darkbg: '#0f1423', cardbg: '#161d31' } } } }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Prompt', sans-serif; } </style>
</head>
<body class="bg-gray-100 dark:bg-[#0f1423] text-gray-900 dark:text-[#f3f4f6] min-h-screen flex items-center justify-center p-4">

    <div class="bg-white dark:bg-[#161d31] border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-xl max-w-xl w-full space-y-6">
        <div class="text-center space-y-2">
            <div class="w-12 h-12 bg-purple-600/20 text-purple-600 dark:text-purple-400 rounded-2xl mx-auto flex items-center justify-center font-bold text-xl">🌐</div>
            <h2 class="text-2xl font-bold">BizFlow+ หน้าบ้านยื่นกู้สมาชิก</h2>
            <p class="text-xs text-gray-500 dark:text-gray-400">กรุณายืนยันเบอร์โทรศัพท์เพื่อรับรหัส OTP ก่อนทำรายการ</p>
        </div>

        <!-- STEP 1: ขอรหัส OTP -->
        <div id="step-otp-request" class="space-y-4 text-xs">
            <div>
                <label class="block font-medium mb-1">เบอร์โทรศัพท์มือถือของคุณ *</label>
                <input type="tel" id="client-phone" required placeholder="เช่น 0929237819" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-purple-500">
            </div>
            <button type="button" onclick="requestOtp()" class="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-purple-600/30 transition text-sm">
                ขอรหัส OTP (ส่งเข้า Telegram ทันที)
            </button>
        </div>

        <!-- STEP 2: กรอกรหัส OTP -->
        <div id="step-otp-verify" class="hidden space-y-4 text-xs">
            <div class="bg-purple-50 dark:bg-purple-950/30 border border-purple-500/30 p-3 rounded-xl text-purple-700 dark:text-purple-300 text-center">
                ระบบได้สุ่มรหัส OTP ส่งเข้า Telegram ของแอดมินแล้ว<br>กรุณานำรหัส 4 หลักที่ได้รับมากรอกด้านล่าง
            </div>
            <div>
                <label class="block font-medium mb-1">กรอกรหัส OTP 4 หลัก *</label>
                <input type="text" id="client-otp-input" placeholder="XXXX" maxlength="4" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white text-center font-bold text-xl tracking-widest focus:outline-none focus:border-purple-500">
            </div>
            <button type="button" onclick="verifyOtp()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition text-sm">
                ยืนยันรหัส OTP เพื่อเข้าสู่หน้ากรอกสัญญา
            </button>
        </div>

        <!-- STEP 3: ฟอร์มกรอกขอกู้และเซ็นสัญญา -->
        <form id="step-apply-form" onsubmit="submitClientApplication(event)" class="hidden space-y-4 text-xs">
            <div class="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-500/30 p-3 rounded-xl text-emerald-600 dark:text-emerald-400 text-center font-medium">
                ✅ ยืนยันตัวตนด้วยเบอร์โทร <span id="display-phone" class="font-bold underline"></span> สำเร็จแล้ว
            </div>
            <div>
                <label class="block font-medium mb-1">ชื่อ - นามสกุลจริง *</label>
                <input type="text" id="apply-name" required placeholder="เช่น สมชาย ใจดี" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-purple-500">
            </div>
            <div>
                <label class="block font-medium mb-1">ลิงก์ Facebook ส่วนตัว *</label>
                <input type="url" id="apply-fb" required placeholder="https://facebook.com/yourname" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-purple-500">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block font-medium mb-1">จำนวนเงินต้นที่ขอกู้ (บาท) *</label>
                    <input type="number" id="apply-amount" required placeholder="5000" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-purple-500">
                </div>
                <div>
                    <label class="block font-medium mb-1">รูปแบบการผ่อนชำระ *</label>
                    <select id="apply-cycle" class="w-full bg-gray-50 dark:bg-[#0f1423] border border-gray-300 dark:border-gray-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-purple-500">
                        <option value="จ่ายทุกวัน (ดอกลอย)">จ่ายทุกวัน (ดอกลอย)</option>
                        <option value="จ่ายทุกสัปดาห์">จ่ายทุกสัปดาห์</option>
                        <option value="จ่ายทุกเดือน">จ่ายทุกเดือน</option>
                    </select>
                </div>
            </div>

            <!-- Signature Pad -->
            <div>
                <div class="flex justify-between items-center mb-1">
                    <label class="block font-medium">ลงลายเซ็นอิเล็กทรอนิกส์ (ใช้นิ้วหรือเมาส์วาด) *</label>
                    <button type="button" onclick="clearSignature()" class="text-rose-500 hover:underline">ล้างลายเซ็น</button>
                </div>
                <div class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl bg-gray-50 dark:bg-[#0f1423] h-40 relative overflow-hidden">
                    <canvas id="signatureCanvas" class="w-full h-full cursor-crosshair touch-none"></canvas>
                    <div id="signPlaceholder" class="absolute inset-0 flex items-center justify-center text-gray-400 pointer-events-none font-medium">เซ็นชื่อลงในกรอบนี้</div>
                </div>
            </div>

            <button type="submit" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-purple-600/30 transition text-sm">
                ส่งคำขอกู้ & ยืนยันสัญญา (แจ้งเตือน Telegram)
            </button>
        </form>
    </div>

    <script>
        let verifiedPhone = "";
        let generatedOtp = "";

        async function requestOtp() {
            const phone = document.getElementById('client-phone').value.trim();
            if(!phone || phone.length < 9) {
                alert('กรุณากรอกเบอร์โทรศัพท์มือถือให้ถูกต้อง');
                return;
            }
            verifiedPhone = phone;

            const formData = new URLSearchParams();
            formData.append('phone', phone);

            try {
                const res = await fetch('/api/request-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });
                const data = await res.json();
                if(data.status === 'success') {
                    generatedOtp = data.otp;
                    alert('ระบบได้ส่งรหัส OTP ไปยัง Telegram เรียบร้อยแล้ว');
                    document.getElementById('step-otp-request').classList.add('hidden');
                    document.getElementById('step-otp-verify').classList.remove('hidden');
                } else {
                    alert('เกิดข้อผิดพลาดในการส่ง OTP');
                }
            } catch(e) {
                alert('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
            }
        }

        function verifyOtp() {
            const inputOtp = document.getElementById('client-otp-input').value.trim();
            if(inputOtp !== generatedOtp) {
                alert('รหัส OTP ไม่ถูกต้อง กรุณาตรวจสอบรหัสใน Telegram อีกครั้ง');
                return;
            }
            
            document.getElementById('display-phone').innerText = verifiedPhone;
            document.getElementById('step-otp-verify').classList.add('hidden');
            document.getElementById('step-apply-form').classList.remove('hidden');
            setTimeout(initSignaturePad, 50);
        }

        let canvas, ctx, isDrawing = false, hasSigned = false;
        function initSignaturePad() {
            canvas = document.getElementById('signatureCanvas');
            if(!canvas) return;
            ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width; canvas.height = rect.height;
            ctx.strokeStyle = '#a78bfa'; ctx.lineWidth = 2.5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';

            const getPos = (e) => {
                const r = canvas.getBoundingClientRect();
                return { x: (e.clientX || e.touches[0].clientX) - r.left, y: (e.clientY || e.touches[0].clientY) - r.top };
            };
            const start = (e) => { isDrawing = true; hasSigned = true; document.getElementById('signPlaceholder').style.display = 'none'; const p = getPos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); e.preventDefault(); };
            const draw = (e) => { if(!isDrawing) return; const p = getPos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); e.preventDefault(); };
            const stop = () => { isDrawing = false; ctx.beginPath(); };

            canvas.onmousedown = start; canvas.onmousemove = draw; canvas.onmouseup = stop; canvas.onmouseleave = stop;
            canvas.ontouchstart = start; canvas.ontouchmove = draw; canvas.ontouchend = stop;
        }

        function clearSignature() {
            if(!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hasSigned = false;
            document.getElementById('signPlaceholder').style.display = 'flex';
        }

        async function submitClientApplication(e) {
            e.preventDefault();
            if(!hasSigned) { alert('กรุณาลงลายเซ็นก่อนส่งคำขอ'); return; }

            const formData = new URLSearchParams();
            formData.append('name', document.getElementById('apply-name').value);
            formData.append('phone', verifiedPhone);
            formData.append('fb', document.getElementById('apply-fb').value);
            formData.append('amount', document.getElementById('apply-amount').value);
            formData.append('cycle', document.getElementById('apply-cycle').value);

            const res = await fetch('/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if(res.ok) {
                alert('ส่งคำขอกู้และแจ้งเตือนผ่าน Telegram สำเร็จ!');
                location.reload();
            } else {
                alert('เกิดข้อผิดพลาดในการส่งข้อมูล');
            }
        }
    </script>
</body>
</html>
"""

# ----------------- Flask Routes -----------------
@app.route('/api/request-otp', methods=['POST'])
def api_request_otp():
    phone = request.form.get('phone')
    if not phone:
        return {"status": "error"}, 400
    
    otp_code = str(random.randint(1000, 9999))
    pending_otp_requests.append({'phone': phone, 'otp': otp_code})
    
    msg = f"🔑 <b>OTP คำขอกู้</b>\n📞 เบอร์: {phone}\n🔢 OTP: {otp_code}"
    send_telegram_alert(msg)
    
    return {"status": "success", "otp": otp_code}

@app.route('/apply', methods=['GET', 'POST'])
def apply_page():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        fb = request.form.get('fb')
        amount = request.form.get('amount')
        cycle = request.form.get('cycle')
        
        # บันทึกข้อมูลลงฐานข้อมูล Supabase (สถานะ: รออนุมัติ)
        try:
            supabase.table("debtors").insert({
                "name": name,
                "phone": phone,
                "facebook": fb,
                "principal": float(amount),
                "cycle": cycle,
                "status": "รออนุมัติ",
                "old_arrears": 0
            }).execute()
        except Exception as e:
            print(f"Supabase Insert Error: {e}")

        # ส่งแจ้งเตือนเข้า Telegram ทันที
        msg = f"🚨 <b>มีคำขอกู้เงินใหม่เข้ามา!</b>\n👤 ชื่อ: {name}\n📞 เบอร์: {phone}\n🔗 FB: {fb}\n💰 ยอดกู้: ฿{amount}\n📅 ผ่อน: {cycle}"
        send_telegram_alert(msg)
        
        return "Success", 200

    return render_template_string(APPLY_TEMPLATE)

@app.route('/')
def admin_dashboard():
    debtors = get_debtors_from_db()
    total_principal = sum([float(d.get('principal', 0)) for d in debtors if d.get('status') == 'ปกติ'])
    total_profit = 0
    collected_today = 0
    
    admin_html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>BizFlow+ - ระบบจัดการลูกหนี้ & บัญชีการเงิน</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style> body {{ font-family: 'Kanit', sans-serif; background-color: #f8fafc; }} </style>
    </head>
    <body class="bg-slate-50 text-slate-800 p-8">
        <div class="max-w-6xl mx-auto space-y-6">
            <div class="flex justify-between items-center bg-white p-6 rounded-2xl shadow-sm border">
                <div>
                    <h1 class="text-2xl font-black text-purple-900">BizFlow+ แดชบอร์ดหลังบ้าน</h1>
                    <p class="text-xs text-slate-500">ระบบบริหารสินเชื่อและตรวจสอบคำขอกู้</p>
                </div>
                <a href="/apply" target="_blank" class="px-4 py-2 bg-purple-600 text-white rounded-xl text-sm font-bold shadow hover:bg-purple-700 transition">
                    <i class="fa-solid fa-globe mr-1.5"></i> ไปหน้าบ้านสมาชิก (/apply)
                </a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-rose-600 text-white p-6 rounded-2xl shadow">
                    <span class="text-xs font-bold uppercase opacity-80">เงินต้นคงค้างทั้งหมด</span>
                    <h3 class="text-3xl font-black mt-1">฿{total_principal:,.2f}</h3>
                </div>
                <div class="bg-blue-600 text-white p-6 rounded-2xl shadow">
                    <span class="text-xs font-bold uppercase opacity-80">ยอดเก็บได้วันนี้</span>
                    <h3 class="text-3xl font-black mt-1">฿{collected_today:,.2f}</h3>
                </div>
                <div class="bg-emerald-600 text-white p-6 rounded-2xl shadow">
                    <span class="text-xs font-bold uppercase opacity-80">กำไรสะสมรวม</span>
                    <h3 class="text-3xl font-black mt-1">฿{total_profit:,.2f}</h3>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border space-y-4">
                <h3 class="font-bold text-slate-800 text-base">⌛ คำขอกู้ใหม่จากหน้าบ้านที่รออนุมัติ</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border rounded-xl overflow-hidden">
                        <thead class="bg-slate-100 text-slate-600">
                            <tr><th class="p-3">ชื่อ-นามสกุล</th><th class="p-3">เบอร์โทร</th><th class="p-3">Facebook</th><th class="p-3 text-right">วงเงินขอกู้</th><th class="p-3 text-center">รูปแบบผ่อน</th><th class="p-3 text-center">สถานะ</th></tr>
                        </thead>
                        <tbody class="divide-y">
    """
    
    pending_list = [d for d in debtors if d.get('status') == 'รออนุมัติ']
    if pending_list:
        for d in pending_list:
            admin_html += f"""
                            <tr>
                                <td class="p-3 font-bold">{d.get('name')}</td>
                                <td class="p-3 font-mono">{d.get('phone')}</td>
                                <td class="p-3"><a href="{d.get('facebook')}" target="_blank" class="text-blue-600 underline">ลิงก์เฟซบุ๊ก</a></td>
                                <td class="p-3 text-right font-mono font-bold text-purple-700">฿{float(d.get('principal', 0)):,.2f}</td>
                                <td class="p-3 text-center">{d.get('cycle')}</td>
                                <td class="p-3 text-center"><span class="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full font-bold text-[10px]">รอพิจารณา</span></td>
                            </tr>
            """
    else:
        admin_html += """<tr><td colspan="6" class="p-6 text-center text-slate-400">ยังไม่มีคำขอกู้ใหม่ในขณะนี้</td></tr>"""

    admin_html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(admin_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
