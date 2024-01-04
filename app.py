import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    inventory = db.relationship('Inventory', backref='product')

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    inventory = db.relationship('Inventory', backref='location')

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    quantity = db.Column(db.Integer)

@app.route('/')
def index():
    inventory = Inventory.query.all()
    return render_template('index.html', data=inventory)

@app.route('/search_products', methods=['POST'])
def search_products():
    search_term = request.form.get('searchTerm')

    search_results = Inventory.query.filter(Product.name.ilike(f'%{search_term}%')).all()

    return render_template('index.html', data=search_results)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('productName')
    description = request.form.get('productDescription')
    price = request.form.get('productPrice')
    product = Product(name=name, description=description, price=price)
    db.session.add(product)
    location = Location.query.all()
    for l in location:
        inventory = Inventory(product_id=product.id, location_id=l.id, quantity=0)
        db.session.add(inventory)
    db.session.commit()
    inventory_data = Inventory.query.all()
    return jsonify(render_template('index.html', data=inventory_data))

@app.route('/add_location', methods=['POST'])
def add_location():
    name = request.form.get('locationName')
    location = Location(name=name)
    db.session.add(location)
    product = Product.query.all()
    for p in product:
        inventory = Inventory(product_id=p.id, location_id=location.id, quantity=0)
        db.session.add(inventory)
    db.session.commit()
    return render_template('index.html', data=Inventory.query.all())


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    inventoryId = request.form.get('inventoryId')
    quantity = request.form.get('quantity')
    inventory = Inventory.query.filter_by(id=inventoryId).first()
    inventory.quantity = quantity
    db.session.commit()
    return render_template('index.html', data=Inventory.query.all())

@app.route('/delete_product', methods=['POST'])
def delete_product():
    inventoryId = request.form.get('inventoryId')
    inventory = Inventory.query.filter_by(id=inventoryId).first()
    db.session.delete(inventory)
    db.session.commit()
    return render_template('index.html', data=Inventory.query.all())

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)


