from flask import Flask, render_template, request, url_for, redirect 
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, DecimalField
from wtforms.validators import DataRequired
from datetime import datetime, timezone

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_receipt = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    price = db.Column(db.Float, nullable=False)

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    date_receipt = DateField('Date Receipt', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])


@app.route('/', methods=['POST', 'GET'])
def index():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        quantity = form.quantity.data
        date_receipt = form.date_receipt.data
        price = form.price.data

        product = Product(name=name, description=description, 
                          quantity=quantity, date_receipt=date_receipt, price=price)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('index'))

    products = Product.query.all()
    return render_template('index.html', form=form, products=products)


@app.route('/products/<int:id>')
def product_detail(id):
    product =Product.query.get(id)   
    return render_template("product_detail.html", product=product)


@app.route('/products/<int:id>/delete')
def product_delete(id):
    product = Product.query.get_or_404(id)

    try:
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return "При удалении товара произошла ошибка!!!"


@app.route('/products/<int:id>/update', methods=['POST', 'GET'])
def product_update(id):    
    product = Product.query.get(id)
    form = ProductForm(obj=product)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.quantity = request.form['quantity']
        product.date_receipt = datetime.strptime(request.form['date_receipt'], '%Y-%m-%d')
        product.price = request.form['price']
        try:            
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
           return f"При изменении товара произошла ошибка: {str(e)}"
    else:
        
        return render_template("product_update.html", product=product, form=form)



if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)