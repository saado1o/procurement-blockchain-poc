import os
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db, login_manager, csrf
from model import User, Tender, Bid, Query
from blockchain import deploy_contract
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secure-and-constant-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Linkin.123@localhost/purchase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    tenders = Tender.query.order_by(Tender.id.desc()).all()
    return render_template('index.html', tenders=tenders)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data
        role = form.role.data

        if User.query.filter_by(username=username).first():
            flash('Username already registered.')
            return redirect(url_for('register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome, {user.username}!')
            return redirect(url_for('index'))

        flash('Invalid username or password.')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))


@app.route('/create_tender', methods=['GET', 'POST'])
@login_required
def create_tender():
    if current_user.role != 'admin':
        flash('Only admins can create tenders.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('document')

        if not title or not description:
            flash('Title and description are required.')
            return redirect(url_for('create_tender'))

        if not file or file.filename == '':
            flash('Tender document (PDF) is required.')
            return redirect(url_for('create_tender'))

        if not file.filename.lower().endswith('.pdf'):
            flash('Only PDF files are allowed.')
            return redirect(url_for('create_tender'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            _, tx_hash, contract_address = deploy_contract(title)
        except Exception as e:
            flash(f'Blockchain deployment error: {e}')
            return redirect(url_for('create_tender'))

        new_tender = Tender(
            title=title,
            description=description,
            document=filename,
            contract_address=contract_address,
            status='active',
            po_awarded=False
        )
        db.session.add(new_tender)
        db.session.commit()

        flash(f'Tender created successfully. Contract address: {contract_address}')
        return redirect(url_for('index'))

    return render_template('create_tender.html')


@app.route('/tender/<int:tender_id>')
@login_required
def view_tender(tender_id):
    tender = Tender.query.get_or_404(tender_id)
    bids = Bid.query.filter_by(tender_id=tender.id).order_by(Bid.amount.asc()).all()
    queries = Query.query.filter_by(tender_id=tender.id).order_by(Query.timestamp.desc()).all()
    return render_template('tender_detail.html', tender=tender, bids=bids, queries=queries)


@app.route('/bid/<int:tender_id>', methods=['POST'])
@login_required
def bid(tender_id):
    if current_user.role != 'bidder':
        flash('Only bidders can place bids.')
        return redirect(url_for('index'))

    tender = Tender.query.get_or_404(tender_id)
    if tender.status != 'active':
        flash('Bidding is closed for this tender.')
        return redirect(url_for('view_tender', tender_id=tender_id))

    amount_str = request.form.get('amount', '').strip()
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        flash('Please enter a valid positive bid amount.')
        return redirect(url_for('view_tender', tender_id=tender_id))

    existing_bid = Bid.query.filter_by(user_id=current_user.id, tender_id=tender_id).first()
    if existing_bid:
        existing_bid.amount = amount
        existing_bid.status = 'pending'
        flash('Your bid was updated and is pending approval.')
    else:
        new_bid = Bid(user_id=current_user.id, tender_id=tender_id, amount=amount, status='pending')
        db.session.add(new_bid)
        flash('Bid submitted and pending approval.')

    db.session.commit()
    return redirect(url_for('view_tender', tender_id=tender_id))


@app.route('/approve_bid/<int:bid_id>', methods=['POST'])
@login_required
def approve_bid(bid_id):
    if current_user.role != 'admin':
        abort(403)

    bid = Bid.query.get_or_404(bid_id)
    if bid.status == 'pending':
        bid.status = 'approved'
        db.session.commit()
        flash(f'Bid by {bid.user.username} approved.')
    else:
        flash('Bid already processed.')

    return redirect(url_for('view_tender', tender_id=bid.tender_id))


@app.route('/reject_bid/<int:bid_id>', methods=['POST'])
@login_required
def reject_bid(bid_id):
    if current_user.role != 'admin':
        abort(403)

    bid = Bid.query.get_or_404(bid_id)
    if bid.status == 'pending':
        bid.status = 'rejected'
        db.session.commit()
        flash(f'Bid by {bid.user.username} rejected.')
    else:
        flash('Bid already processed.')

    return redirect(url_for('view_tender', tender_id=bid.tender_id))


@app.route('/ppra/award_po/<int:tender_id>', methods=['GET', 'POST'])
@login_required
def ppra_award_po(tender_id):
    if current_user.role != 'ppra':
        abort(403)

    tender = Tender.query.get_or_404(tender_id)
    if tender.status != 'active':
        flash('Cannot award PO for this tender.')
        return redirect(url_for('index'))

    approved_bids = Bid.query.filter_by(tender_id=tender_id, status='approved').order_by(Bid.amount.asc()).all()

    if request.method == 'POST':
        po_bid_id = request.form.get('po_bid_id')

        try:
            po_bid_id = int(po_bid_id)
        except (ValueError, TypeError):
            flash('Invalid bid selected.')
            return redirect(url_for('ppra_award_po', tender_id=tender_id))

        po_bid = Bid.query.get(po_bid_id)

        if not po_bid or po_bid.tender_id != tender.id or po_bid.status != 'approved':
            flash('Selected bid is invalid.')
            return redirect(url_for('ppra_award_po', tender_id=tender_id))

        tender.po_awarded = True
        tender.status = 'closed'
        db.session.commit()

        flash(f'Purchase Order awarded to {po_bid.user.username} for tender "{tender.title}"')
        return redirect(url_for('index'))

    return render_template('ppra_approve_po.html', tender=tender, approved_bids=approved_bids)


@app.route('/tender/<int:tender_id>/ppra_query', methods=['POST'])
@login_required
def ppra_send_query(tender_id):
    if current_user.role != 'ppra':
        abort(403)

    tender = Tender.query.get_or_404(tender_id)
    message = request.form.get('query_message', '').strip()

    if not message:
        flash('Query message cannot be empty.')
        return redirect(url_for('view_tender', tender_id=tender_id))

    new_query = Query(
        tender_id=tender.id,
        user_id=current_user.id,
        message=message
    )
    db.session.add(new_query)
    db.session.commit()

    flash('Your query has been sent to the admin.')
    return redirect(url_for('view_tender', tender_id=tender_id))


@app.route('/admin/queries')
@login_required
def admin_view_queries():
    if current_user.role != 'admin':
        abort(403)

    queries = Query.query.order_by(Query.timestamp.desc()).all()
    return render_template('admin_queries.html', queries=queries)


@app.route('/admin/queries/respond/<int:query_id>', methods=['POST'])
@login_required
def admin_respond_query(query_id):
    if current_user.role != 'admin':
        abort(403)

    query = Query.query.get_or_404(query_id)
    response = request.form.get('response_message', '').strip()

    if not response:
        flash('Response message cannot be empty.')
        return redirect(url_for('admin_view_queries'))

    query.response = response
    db.session.commit()
    flash('Response sent successfully.')
    return redirect(url_for('admin_view_queries'))


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.errorhandler(413)
def file_too_large(error):
    flash('File too large. Maximum allowed size is 10MB.')
    return redirect(request.referrer or url_for('index')), 413


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
