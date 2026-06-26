import os
import json
import urllib.request
from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# إعداد التطبيق وقاعدة البيانات بشكل آمن
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# نماذج قاعدة البيانات (Database Models)
# ==========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True) # يمكن أن يكون فارغاً لمستخدمي جوجل
    profile_pic = db.Column(db.String(500), default='https://api.dicebear.com/7.x/avataaars/svg?seed=fallback')
    auth_provider = db.Column(db.String(20), default='local') # 'google' أو 'local'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء الجداول إذا لم تكن موجودة
with app.app_context():
    db.create_all()

# ==========================================
# مسارات العرض والـ API (Routes & API)
# ==========================================

# تم إضافة هذا المسار لحل مشكلة الـ 404 وعرض الموقع تلقائياً
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "البريد الإلكتروني مسجل بالفعل!"})
    
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    avatar_url = f"https://api.dicebear.com/7.x/initials/svg?seed={name}"
    
    new_user = User(email=email, name=name, password_hash=hashed_pw, profile_pic=avatar_url)
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    return jsonify({"success": True, "user": {"name": name, "pic": avatar_url}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and user.password_hash and check_password_hash(user.password_hash, data.get('password')):
        session['user_id'] = user.id
        return jsonify({"success": True, "user": {"name": user.name, "pic": user.profile_pic}})
    
    return jsonify({"success": False, "message": "بيانات الدخول غير صحيحة."}), 401

# مسار تسجيل الدخول التلقائي عبر جوجل وحفظ البيانات
@app.route('/api/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"success": False, "message": "التوكن مفقود"}), 400

    try:
        # التحقق من صحة التوكن عبر خوادم جوجل الرسمية
        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = urllib.request.urlopen(google_verify_url)
        user_info = json.loads(response.read().decode('utf-8'))
        
        if 'email' not in user_info:
            return jsonify({"success": False, "message": "فشل التحقق من الحساب عبر جوجل."}), 400
            
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture', f"https://api.dicebear.com/7.x/initials/svg?seed={name}")
        
        # البحث عن المستخدم للتعرف عليه
        user = User.query.filter_by(email=email).first()
        
        # إذا كان مستخدم جديد، يتم تسجيله وحفظه تلقائياً في قاعدة البيانات
        if not user:
            user = User(
                email=email,
                name=name,
                profile_pic=picture,
                auth_provider='google'
            )
            db.session.add(user)
            db.session.commit()
            
        # تسجيل الدخول تلقائياً في الجلسة (Session)
        session['user_id'] = user.id
        
        return jsonify({
            "success": True, 
            "user": {"name": user.name, "pic": user.profile_pic}
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"حدث خطأ أثناء الاتصال بجوجل: {str(e)}"}), 500

@app.route('/api/checkout', methods=['POST'])
def checkout():
    return jsonify({"success": True, "message": "تمت عملية الدفع بنجاح وأمان!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)