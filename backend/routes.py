from flask import Blueprint, jsonify, request
from backend.extensions import db, bcrypt
from backend.models import User, Account, Transaction
from backend.schemas import RegisterSchema, LoginSchema, AccountSchema, TransactionSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

# Initialize schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()
account_schema = AccountSchema()
transaction_schema = TransactionSchema()

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

# User Registration Route
@api_bp.route('/register', methods=['POST'])
def register_user():
    errors = register_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 409

    # Hash password
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], email=data['email'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User Login Route
@api_bp.route('/login', methods=['POST'])
def login_user():
    errors = login_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate JWT token
    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Login successful", "access_token": token}), 200

# Get User Details (Requires JWT)
@api_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })

# Create Account Route (Requires JWT)
@api_bp.route('/account', methods=['POST'])
@jwt_required()
def create_account():
    errors = account_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404

    if Account.query.filter_by(account_number=data['account_number']).first():
        return jsonify({"message": "Account number already exists"}), 409

    account = Account(
        account_number=data['account_number'],
        account_type=data['account_type'],
        balance=data.get('balance', 0.0),
        user_id=user.id
    )
    db.session.add(account)
    db.session.commit()

    return jsonify({"message": "Account created successfully"}), 201

# Money Transfer Route (Requires JWT)
@api_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    errors = transaction_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    user = User.query.get(get_jwt_identity())

    # Get accounts for transfer
    from_account = Account.query.filter_by(id=data['from_account_id'], user_id=user.id).first()
    to_account = Account.query.filter_by(id=data['to_account_id']).first()

    if not from_account or not to_account:
        return jsonify({"message": "Account(s) not found"}), 404

    if from_account.balance < data['amount']:
        return jsonify({"message": "Insufficient funds"}), 400

    # Calculate fee: $1 per $200 transferred
    fee = data['amount'] // 200
    total_deduction = data['amount'] + fee
    from_account.balance -= total_deduction
    to_account.balance += data['amount']

    transaction = Transaction(
        account_id=from_account.id,
        amount=data['amount'],
        transaction_type='transfer'
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": f"Transferred {data['amount']} successfully.",
        "transaction_fee": fee
    }), 200

# Get Transaction History with Search/Filter (by date or amount)
@api_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get filter parameters
    amount_filter = request.args.get('amount', type=float)
    date_filter = request.args.get('date', type=str)

    # Query transactions
    query = Transaction.query.join(Account).filter(Account.user_id == user.id)

    # Apply filters if they exist
    if amount_filter:
        query = query.filter(Transaction.amount == amount_filter)
    
    if date_filter:
        try:
            date_object = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(Transaction.timestamp.like(date_object.strftime('%Y-%m-%d') + '%'))
        except ValueError:
            return jsonify({"message": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Pagination
    transactions = query.order_by(Transaction.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for t in transactions.items:
        results.append({
            "id": t.id,
            "account_id": t.account_id,
            "amount": t.amount,
            "type": t.transaction_type,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "transactions": results,
        "total": transactions.total,
        "page": transactions.page,
        "pages": transactions.pages
    }), 200

# Register Blueprint with the main app
def register_routes(app):
    app.register_blueprint(api_bp, url_prefix='/api')
