import os
import json
import stripe
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tech_global_store.db'
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
        db.session.bulk_insert_mappings(Product, lux_products)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_database()

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)