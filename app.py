from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/library'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    # category = db.relationship('BookWriter', backref='category')

    def __repr__(self):
        return f"<Category {self.name}>"
    
class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    citizenship = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    writers = db.relationship('BookWriter', backref='writer')
    def __repr__(self):
        return f"<Writer {self.name}>"

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    # writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    writer = db.relationship('BookWriter', backref='books')
    category = db.relationship('Category', backref='category')

class BookWriter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_books = db.Column(db.Integer, db.ForeignKey('books.id'))
    id_writer = db.Column(db.Integer, db.ForeignKey('writer.id'))


    def __repr__(self):
        return f"<Book {self.title}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    user_type = db.Column(db.String(255))

    def __repr__(self):
        return f"<User {self.username}>"
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_admin = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_member = db.Column(db.Integer, db.ForeignKey('user.id'))
    borrowing_date = db.Column(db.TIMESTAMP)

    admin = db.relationship('User', foreign_keys=[id_admin], backref='transactions_admin', lazy=True)
    member = db.relationship('User', foreign_keys=[id_member], backref='transactions_member', lazy=True)

    def __repr__(self):
        return f"<Transaction {self.id}>"
    
class TransactionBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_transaction = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    id_book = db.Column(db.Integer, db.ForeignKey('books.id'))
    return_date = db.Column(db.TIMESTAMP)

    transaction = db.relationship('Transaction', backref='transaction_books')
    book = db.relationship('Books', backref='transaction_books')

    def __repr__(self):
        return f"<TransactionBook {self.id}>"

    

@app.route('/books/', methods=['GET'])
def get_books():
    # data = BookWriter.query.all()
    return jsonify ([
            {'id writer': data.id,
            'title': data.books.title,
            'writer_id': data.writer.id,
            'name': data.writer.name,
            'year': data.books.year,
            'pages': data.books.pages,
            # 'category_id': data.category.name
            } for data in BookWriter.query.all()
        ])

@app.route('/writer/', methods=['GET'])
def get_writer():
    return jsonify ([
            {'id': data.id,
            'name': data.name,
            'citizenship': data.citizenship,
            'year': data.year,
            } for data in Writer.query.all()
        ])

@app.route('/category/', methods=['GET'])
def get_category():
    return jsonify([
            {'id': data.id,
            'name': data.name,
            'description': data.description,
            } for data in Category.query.all()
        ])

@app.route('/user', methods=['POST'])
def create_user():
    data = User(
        username=request.form['username'],
        password=request.form['password'],
        user_type='member'
        # user_type=request.form['user_type']
    )
    db.session.add(data)
    db.session.commit()
    return {'message': 'User Created Succesfully'}, 201





if __name__ == '__main__':
	app.run(debug=True)