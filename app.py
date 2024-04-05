from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from passlib.context import CryptContext
# from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/library'
db = SQLAlchemy(app)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# bcrypt = Bcrypt(app)

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
    transaction = db.relationship('TransactionBook', backref='books')
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
    is_the_book_back = db.Column(db.Boolean, default=False)
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
@login_required
def get_user():
    if current_user.user_type == 'admin':
        return jsonify([
                {'id': data.id,
                'username': data.username,
                'user_type': data.user_type,
                'password': data.password
                } for data in User.query.order_by(User.id.desc()).all()
            ])


@app.route('/user/', methods=['POST'])
@login_required
def create_user():
    if current_user.user_type == 'admin':
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
@login_required
def update_users(id):
    if current_user.user_type == 'admin':
        data = User.query.get(id)
        if data:
            data.username=request.form['username']
            data.password=request.form['password'],
            data.user_type=request.form['user_type']
            db.session.commit()
            return {' ':'Update Complete'}

@app.route('/user/<id>', methods=['DELETE'])
@login_required
def delete_users(id):
    if current_user.user_type == 'admin':
        data = User.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return {'message': 'Delete Completed'}
        else:
            return{'message': 'Delete Not Completed'}

@app.route('/category/', methods=['GET'])
@login_required
def get_category():
    if current_user.user_type == 'admin':
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
@login_required
def create_category():
    if current_user.user.type == 'admin':
        data = Category(
            name=request.form['name'],
            description=request.form['description'],
        )
        db.session.add(data)
        db.session.commit()
        return {'message': 'Successfully added data'}, 201

@app.route('/category/<id>', methods=['PUT'])
@login_required
def update_category(id):
    if current_user.user.type == 'admin':
        data = Category.query.get(id)
        if data:
            data.name=request.form['name'],
            data.description=request.form['description']
            db.session.commit()
            return {'message':'Update Completed'}
        else:
            return {'message':'Update Not Completed'}

@app.route('/category/<id>', methods=['DELETE'])
@login_required
def category_delete(id):
    if current_user.user_type == 'admin':
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
            'titl':data.title,
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
    if current_user.user_type == 'admin':
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
@login_required
def update_books(id):
    if current_user.user_type == 'admin':
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
@login_required
def delete_books(id):
    if current_user.user_type == 'admin':
        data = Books.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return {'message' : 'Delete Book Successfully'}
        else:
            return {'message' : 'Delete Book Failure'}

@app.route('/writer/', methods=['GET'])
@login_required
def get_writer():
    if current_user.user_type == 'admin':
        return jsonify ([
                {'id': data.id,
                'name': data.name,
                'citizenship': data.citizenship,
                'year': data.year,
                } for data in Writer.query.all()
            ])

@app.route('/writer/', methods=['POST'])
@login_required
def create_writer():
    if current_user.user_type == 'admin':
        data = Writer(
            name=request.form['name'],
            citizenship=request.form['citizenship'],
            year=request.form['year']
        )
        db.session.add(data)
        db.session.commit()
        return {'message' : 'Create Writer Success'}

@app.route('/writer/<id>', methods=['PUT'])
@login_required
def update_writer(id):
    if current_user.user_type == 'admin':
        data = Writer.query.get(id)
        if data : 
            data.name=request.form['name'],
            data.citizenship=request.form['citizenship'],
            data.year=request.form['year']
            db.session.commit()
            return {'message' : 'Update Writer Success'}
    
@app.route('/writer/<id>', methods=['DELETE'])
@login_required
def delete_writer(id):
    if current_user.user_type == 'admin':
        data = Writer.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return {'message' : 'Delete Writer Success'}
        else:
            return {'message' : 'Delete Writer Failure'}
    

@app.route('/bookwriter/', methods=['GET'])
@login_required
def get_bookwriter():
    # data = BookWriter.query.all()
    if current_user.user_type == 'admin':
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
@login_required
def get_bookwriters():
    if current_user.user_type == 'admin':
        return jsonify([
            {
                'id': data.id,
                'id_books': data.id_books,
                'id_writer': data.id_writer
            } for data in BookWriter.query.all()
    ])

@app.route('/bookwriters/', methods=['POST'])
@login_required
def create_bookwriters():
    if current_user.user_type == 'admin':
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
@login_required
def update_bookwrites(id):
    if current_user.user_type == 'admin':
        data = BookWriter.query.get(id)
        if data :
            data.id_books=request.form['id_books'],
            data.id_writer=request.form['id_writer']
            db.session.commit()
            return {'message' :'Update Completed'}
        else:
            return {'message':'Update Not Completed'}

@app.route('/bookwriters/<id>', methods=['DELETE'])
@login_required
def delete_bookwriters(id):
    if current_user.user_type == 'admin':
        data=BookWriter.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return {'message' :'Delete Completed'}
        else:
            return {'message':'Delete Not Completed'}
    
@app.route('/transaction/', methods=['GET'])
@login_required
def get_transaction():
    if current_user.user_type == 'admin':
        data = []
        for transaction in Transaction.query.all():
            try:
                id_admin = transaction.id_admin
            except AttributeError:
                id_admin = 'Error'
            
            transaction_info = {
                'id': transaction.id,
                'id_admin': id_admin,
                'id_member': transaction.id_member,
                'borrowing_date': transaction.borrowing_date
            }
            data.append(transaction_info)
        return jsonify(data)


@app.route('/transaction/', methods=['POST'])
@login_required
def create_transaction():
    if current_user.user_type == 'admin':
        data= Transaction(
            id_admin=request.form['id_admin'],
            id_member=request.form['id_member'],
            borrowing_date=request.form['borrowing_date']
        )
        db.session.add(data)
        db.session.commit()
        return {'message':'Transaction Succesfully'}

@app.route('/transaction/<id>', methods=['PUT'])
@login_required
def update_transaction(id):
    if current_user.user_type == 'admin':
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
@login_required
def delete_transaction(id):
    if current_user.user_type == 'admin':
        data = Transaction.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return{'message':'Delete Completed'}
        else:
            return{'message':'Delete Not Completed'}

@app.route('/transactionbook/', methods=['GET'])
@login_required
def get_transactionbook():
    if current_user.user_type == 'admin':
        data = [{
                'id': data.id,
                'id_transaction' : data.id_transaction,
                'id_book': data.id_book,
                'return_date': data.return_date,
                'Status': data.is_the_book_back

                } for data in TransactionBook.query.all()
        ]
        return jsonify(data)

@app.route('/transactionbook/', methods=['POST'])
@login_required
def create_transactionbook():
    if current_user.user_type == 'admin':
        data = TransactionBook(
            id_transaction=request.form['id_transaction'],
            id_book=request.form['id_book'],
            return_date=request.form['return_date']
        )
        db.session.add(data)
        db.session.commit()
        return{'message': 'Succesfully Transaction Book'}

@app.route('/transactionbook/<id>', methods=['PUT'])
@login_required
def update_transactionbook(id):
    if current_user.user_type == 'admin':
        data = TransactionBook.query.get(id)
        if data:
            data.id_transaction=request.form['id_transaction'],
            data.id_book=request.form['id_book'],
            data.return_date=request.form['return_date'],
            data.is_the_book_back=bool(request.form['status'])
            db.session.commit()
            return {'message':'Update Completed'}
        else:
            return {'message':'Update Not Completed'}

@app.route('/transactionbook/<id>', methods=['DELETE'])
@login_required
def delete_transactionbook(id):
    if current_user.user_type == 'admin':
        data = TransactionBook.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return {'message':'Delete Completed'}
        else:
            return {'message':'Delete Not Completed'}
    

@app.route('/report/', methods=['GET'])
@login_required
def list_late_loans():
    if current_user.user_type == 'admin':
        current_date = datetime.now()
        late_transactions = []

        transactions = Transaction.query.all()
        for transaction in transactions:
            for transaction_book in transaction.transaction_books:
                if not transaction_book.is_the_book_back:  # Hanya periksa keterlambatan jika buku belum dikembalikan
                    if transaction_book.return_date and transaction_book.return_date > transaction.borrowing_date:
                        days_late = (current_date - transaction_book.return_date).days
                        if days_late > 0:
                            late_transaction = {
                                'transaction_id': transaction.id,
                                'borrowing_date': transaction.borrowing_date.strftime('%Y-%m-%d'),
                                'return_date': transaction_book.return_date.strftime('%Y-%m-%d'),
                                'days_late': days_late,
                                'todays_date' :current_date.strftime('%Y-%m-%d'),
                                'books': transaction_book.books.title,
                                'status': transaction_book.is_the_book_back
                            }
                            late_transactions.append(late_transaction)
        return jsonify(late_transactions)
    
    if current_user.user_type != 'admin':
        current_date = datetime.now()
        late_transactions = []

        transactions = Transaction.query.all()
        for transaction in transactions:
            for transaction_book in transaction.transaction_books:
                if not transaction_book.is_the_book_back:  # Hanya periksa keterlambatan jika buku belum dikembalikan
                    if transaction_book.return_date and transaction_book.return_date > transaction.borrowing_date:
                        days_late = (current_date - transaction_book.return_date).days
                        if days_late > 0:
                            late_transaction = {
                                'transaction_id': transaction.id,
                                'borrowing_date': transaction.borrowing_date.strftime('%Y-%m-%d'),
                                'return_date': transaction_book.return_date.strftime('%Y-%m-%d'),
                                'days_late': days_late,
                                'todays_date' :current_date.strftime('%Y-%m-%d'),
                                'books': transaction_book.books.title,
                                # 'status': transaction_book.is_the_book_back
                            }
                            late_transactions.append(late_transaction)
        return jsonify(late_transactions)

    
if __name__ == '__main__':
	app.run(debug=True)