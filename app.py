from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from passlib.context import CryptContext
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/library'
db = SQLAlchemy(app)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    categories = db.relationship('Books', backref='category')

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

    books = db.relationship('BookWriter', backref='book')
    # category = db.relationship('Category', backref='category')

class BookWriter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_books = db.Column(db.Integer, db.ForeignKey('books.id'))
    id_writer = db.Column(db.Integer, db.ForeignKey('writer.id'))
    # book = db.relationship('Books', backref=db.backref('book_authors', lazy=True)) 

    def __repr__(self):
        return f"<Book {self.title}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    user_type = db.Column(db.String(255))

    def __repr__(self):
        return f"<User {self.username}>"
    def is_active(self):
        return True
    def get_id(self):
        return self.id
    def is_authenticated(self):
        return True

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


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#login
@app.route('/login/', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return {'message':'Anda perlu logout dahulu'}
    username = request.form['username']
    password = request.form['password']

    # username = request.headers.get('username')
    # password = request.headers.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and (user.password, password):
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Login failed'}), 401


# logout
@app.route('/logout/', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200



@app.route('/user/', methods=['GET'])
def get_user():
    return jsonify([
            {'id': data.id,
            'username': data.username,
            'user_type': data.user_type,
            'password': data.password
            } for data in User.query.order_by(User.id.desc()).all()
        ])


@app.route('/user/', methods=['POST'])
def create_user():
    data = User(
        username=request.form['username'],
        password = generate_password_hash(request.form['password']),
        # password=request.form['password'],
        
        # user_type='member'
        user_type=request.form['user_type']

    )
    db.session.add(data)
    db.session.commit()
    return {'message': 'User Created Succesfully'}, 201


@app.route('/user/<id>', methods=['PUT'])
def update_users(id):
    data = User.query.get(id)
    if data:
        data.username=request.form['username']
        data.password=request.form['password'],
        data.user_type=request.form['user_type']
        db.session.commit()
        return {' ':'Update Complete'}

@app.route('/user/<id>', methods=['DELETE'])
def delete_users(id):
    data = User.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message': 'Delete Completed'}
    else:
        return{'message': 'Delete Not Completed'}

@app.route('/category/', methods=['GET'])
def get_category():
    return jsonify([
            {'id': data.id,
            'name': data.name,
            'description': data.description,
            } for data in Category.query.all()
        ])


##################----------------#################
# @app.route('/category/', methods=['GET']) ###sama saja tapi dengan logic yang berbeda###
# def get_category():
#     data = [
#             {'id': data.id,
#             'name': data.name,
#             'description': data.description,
#             } for data in Category.query.all()
#         ]
#     return jsonify(data)
##############------------------------------#################


@app.route('/category/', methods=['POST'])
def create_category():
    data = Category(
        name=request.form['name'],
        description=request.form['description'],
    )
    db.session.add(data)
    db.session.commit()
    return {'message': 'Successfully added data'}, 201

@app.route('/category/<id>', methods=['PUT'])
def update_category(id):
    data = Category.query.get(id)
    if data:
        data.name=request.form['name'],
        data.description=request.form['description']
        db.session.commit()
        return {'message':'Update Completed'}
    else:
        return {'message':'Update Not Completed'}

@app.route('/category/<id>', methods=['DELETE'])
def category_delete(id):
    data= Category.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message':'Delete Completed'}
    else:
        return {'message':'Delete Not Completed'}

@app.route('/books/', methods=['GET'])
@login_required
def get_books():
    if current_user.user_type == 'admin':
        return jsonify([
            {'id': data.id,
            'title':data.title,
            'category_id':data.category_id,
            'year':data.year,
            'pages':data.pages
            } for data in Books.query.all()
        ])
    else:
        return {'Message': "Access denied"}

@app.route('/books/', methods=['POST'])
@login_required
def create_books():
    data = Books(
        title=request.form['title'],
        # writer_id=request.form['writer_id'],
        category_id=request.form['category_id'],
        year=request.form['year'],
        pages=request.form['pages'],
    )
    db.session.add(data)
    db.session.commit()
    return {'message' : 'Create Book Successfully'}

@app.route('/books/<id>', methods=['PUT'])
def update_books(id):
    data = Books.query.get(id)
    if data:
        data.title=request.form['title'],
        data.category_id=request.form['category_id'],
        data.year=request.form['year'],
        data.pages=request.form['pages']
        db.session.commit()
        return {'message' : 'Update Book Successfully'}
    else:
        return {'message' : 'Update Book Failure'}

@app.route('/books/<id>', methods=['DELETE'])
def delete_books(id):
    data = Books.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message' : 'Delete Book Successfully'}
    else:
        return {'message' : 'Delete Book Failure'}

@app.route('/writer/', methods=['GET'])
def get_writer():
    return jsonify ([
            {'id': data.id,
            'name': data.name,
            'citizenship': data.citizenship,
            'year': data.year,
            } for data in Writer.query.all()
        ])

@app.route('/writer/', methods=['POST'])
def create_writer():
    data = Writer(
        name=request.form['name'],
        citizenship=request.form['citizenship'],
        year=request.form['year']
    )
    db.session.add(data)
    db.session.commit()
    return {'message' : 'Create Writer Success'}

@app.route('/writer/<id>', methods=['PUT'])
def update_writer(id):
    data = Writer.query.get(id)
    if data : 
        data.name=request.form['name'],
        data.citizenship=request.form['citizenship'],
        data.year=request.form['year']
        db.session.commit()
        return {'message' : 'Update Writer Success'}
    
@app.route('/writer/<id>', methods=['DELETE'])
def delete_writer(id):
    data = Writer.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message' : 'Delete Writer Success'}
    else:
        return {'message' : 'Delete Writer Failure'}
    

@app.route('/bookwriter/', methods=['GET'])
def get_bookwriter():
    # data = BookWriter.query.all()
    return jsonify ([
            {'id': data.id,
            'id_books': data.id_books,
            'id_writer': data.id_writer,
            'writer':{
                'writer_id': data.writer.id,
                'name': data.writer.name
            },
            'books': {
                'title': data.book.title,
                'year': data.book.year if data.book else None,
                'pages': data.book.pages,
                'category_id': data.book.category_id,
                'category' : {
                    'name': data.book.category.name,
                }
            }
            } for data in BookWriter.query.all()
        ])

@app.route('/bookwriters/', methods=['GET'])
def get_bookwriters():
    return jsonify([
        {
            'id': data.id,
            'id_books': data.id_books,
            'id_writer': data.id_writer
        } for data in BookWriter.query.all()
    ])

@app.route('/bookwriters/', methods=['POST'])
def create_bookwriters():
    data = BookWriter(
        # id=request.form['id'], ####tidak perlu menampilkan id
        id_books=request.form['id_books'] ,
        id_writer=request.form['id_writer'] 
    )
    db.session.add(data)
    db.session.commit()
    return {'message':'Book Writer Created Successfully'}

####Sama tapi dengan pola logic yang berbeda#########
# @app.route('/bookwriters/', methods=['POST'])
# def create_bookwriters():
#     db.session.add(BookWriter(
#         id_books=request.form.get('id_books'),
#         id_writer=request.form.get('id_writer')
#     ))
#     db.session.commit()
#     return {'message': 'BookWriter created successfully!'}, 201
#######---------------------------------##################

@app.route('/bookwriters/<id>', methods=['PUT'])
def update_bookwrites(id):
    data = BookWriter.query.get(id)
    if data :
        data.id_books=request.form['id_books'],
        data.id_writer=request.form['id_writer']
        db.session.commit()
        return {'message' :'Update Completed'}
    else:
        return {'message':'Update Not Completed'}

@app.route('/bookwriters/<id>', methods=['DELETE'])
def delete_bookwriters(id):
    data=BookWriter.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message' :'Delete Completed'}
    else:
        return {'message':'Delete Not Completed'}
    
@app.route('/transaction/', methods=['GET'])
def get_transaction():
    data = [{
            'id': data.id,
            'id_admin': data.id_admin,
            'id_member': data.id_member,
            'borrowing_date': data.borrowing_date
            } for data in Transaction.query.all()
    ]
    return jsonify(data)

@app.route('/transaction/', methods=['POST'])
def create_transaction():
    data= Transaction(
        id_admin=request.form['id_admin'],
        id_member=request.form['id_member'],
        borrowing_date=request.form['borrowing_date']
    )
    db.session.add(data)
    db.session.commit()
    return {'message':'Transaction Succesfully'}

@app.route('/transaction/<id>', methods=['PUT'])
def update_transaction(id):
    data = Transaction.query.get(id)
    if data:
        data.id_admin=request.form['id_admin'],
        data.id_member=request.form['id_member'],
        data.borrowing_date=request.form['borrowing_date']
        db.session.commit()
        return {'message':'Update Completed'}
    else:
        return {'message':'Update Not Completed'}

@app.route('/transaction/<id>', methods=['DELETE'])
def delete_transaction(id):
    data = Transaction.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return{'message':'Delete Completed'}
    else:
        return{'message':'Delete Not Completed'}

@app.route('/transactionbook/', methods=['GET'])
def get_transactionbook():
    data = [{
            'id': data.id,
            'id_transaction' : data.id_transaction,
            'id_book': data.id_book,
            'return_date': data.return_date

            } for data in TransactionBook.query.all()
    ]
    return jsonify(data)

@app.route('/transactionbook/', methods=['POST'])
def create_transactionbook():
    data = TransactionBook(
        id_transaction=request.form['id_transaction'],
        id_book=request.form['id_book'],
        return_date=request.form['return_date']
    )
    db.session.add(data)
    db.session.commit()
    return{'message': 'Succesfully Transaction Book'}

@app.route('/transactionbook/<id>', methods=['PUT'])
def update_transactionbook(id):
    data = TransactionBook.query.get(id)
    if data:
        data.id_transaction=request.form['id_transaction'],
        data.id_book=request.form['id_book'],
        data.return_date=request.form['return_date']
        db.session.commit()
        return {'message':'Update Completed'}
    else:
        return {'message':'Update Not Completed'}

@app.route('/transactionbook/<id>', methods=['DELETE'])
def delete_transactionbook(id):
    data = TransactionBook.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return {'message':'Delete Completed'}
    else:
        return {'message':'Delete Not Completed'}
    



    
if __name__ == '__main__':
	app.run(debug=True)