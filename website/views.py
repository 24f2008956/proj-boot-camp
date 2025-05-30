from flask import Flask, current_app as app, render_template, redirect,request, url_for, flash
from .models import db, User, Parking_lot, Parking_spot, Booking
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func

#admin dashboard
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))
    #app statistics
    total_users = User.query.count()
    total_parking_lots = Parking_lot.query.count()
    users = User.query.all()
    parking_lots = Parking_lot.query.all()
    parking_spots = Parking_spot.query.all()
    
    
    '''
    #for charts
    revenue_data = {
        'labels': [parking_lots.parking_lot for lot in parking_lots],
        'data': [lot.price_per_hour for lot in parking_lots]
        }
    bookings_data = {
        'labels': [user.username for user in users],
        
        'data': [user.bookings.count() for user in users]
    }
    '''
    return render_template('admin_dashboard.html', total_users=total_users, total_parking_lots=total_parking_lots, users=users, parking_lots=parking_lots, parking_spots=parking_spots)


#admin Charts
@app.route('/admin/charts', methods=['GET'])
@login_required
def admin_charts():
    # Example data for charts
    parking_lots = Parking_lot.query.all()
    users = User.query.all()
    bookings = Booking.query.all()
    
    total_parking_lots = Parking_lot.query.count()
    total_users = User.query.count()
    total_available_spots = Parking_spot.query.filter_by(is_available=True).count()
    total_bookings = Booking.query.count()
    total_revenue = sum(b.price_per_hour for b in parking_lots)
    # For charts
    parking_lot_labels = {
        'labels': [lot.name for lot in parking_lots],
        'data': [lot.price_per_hour for lot in parking_lots]
    }
    revenue_labels = {
        'labels': [user.username for user in users],
        'data': [len(user.bookings) for user in users]
    }
    
    return render_template('admin_charts.html', parking_lot_labels=parking_lot_labels, revenue_labels=revenue_labels,
                           total_parking_lots=total_parking_lots, total_available_spots=total_available_spots,
                           total_bookings=total_bookings, total_users=total_users, total_revenue=total_revenue)
 
    
        
        
        
#user dashboard
@app.route("/user_dashboard", methods=['GET'])
@login_required
def user_dashboard():
    users = [current_user]
    parking_lots = Parking_lot.query.all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()
    total_duration = sum(
        (booking.out_time - booking.in_time).total_seconds() / 3600 if booking.in_time and booking.out_time else 0
        for booking in bookings
    )
    total_cost = sum(
        (booking.out_time - booking.in_time).total_seconds() / 3600 * booking.parking_lot.price_per_hour if booking.in_time and booking.out_time and booking.parking_lot else 0
        for booking in bookings
    )
    flash(f'Total Bookings: {total_bookings}', 'info')
    flash(f'Total Duration: {total_duration:.2f} hours', 'info')    
    flash(f'Total Cost: ${total_cost:.2f}', 'info')
    # Format user history for display
    # Ensure bookings are sorted by timestamp
    bookings.sort(key=lambda x: x.timestamp, reverse=True)  # Sort by timestamp, most recent first
    # Format booking details for display

    
    user_history = [{
        'date': booking.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'parking_lot': booking.parking_lot.name if booking.parking_lot else 'N/A',
        'spot_number': booking.parking_spot.spot_number if booking.parking_spot else 'N/A',
        'vehicle_no': booking.vehicle_number if booking.vehicle_number else 'N/A',
        'in_time': booking.in_time.strftime('%Y-%m-%d %H:%M:%S') if booking.in_time else 'N/A',
        'out_time': booking.out_time.strftime('%Y-%m-%d %H:%M:%S') if booking.out_time else 'N/A',
        'cost': booking.parking_lot.price_per_hour if booking.parking_lot else 'N/A'
        } for booking in bookings]
    active_bookings = dict(
        db.session.query(Booking.parking_lot_id,
            func.count(Booking.id)).filter(
            Booking.spot_no.isnot(None),
            Booking.out_time == None).group_by(Booking.parking_lot_id).all())

    # Attach available_spaces to each parking lot
    for lot in parking_lots:
        booked = active_bookings.get(lot.id, 0)
        lot.available_spaces = lot.max_no_spots - booked
        
    return render_template('user_dashboard.html', users=users, total_bookings=total_bookings, total_duration=total_duration,total_cost=total_cost, parking_lots=parking_lots, bookings=bookings, user_history=user_history)


#user profile
@app.route('/user_profile', methods=['GET'])
@login_required
def user_profile():
    user = User.query.get(current_user.id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('home'))
    return render_template('user_profile.html', user=user)
    
#edit user profile
@app.route('/edit_user_profile', methods=['GET', 'POST'])
@login_required
def edit_user_profile():
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        new_password = request.form.get('password')
        if new_password:
            user.password = generate_password_hash(new_password)
        
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))
    return render_template('edit_user_profile.html', user=user) 

#delete user profile
@app.route('/delete_user_profile', methods=['POST'])
@login_required
def delete_user_profile():
    user = User.query.get(current_user.id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User profile deleted successfully!', 'success')
        return redirect(url_for('home'))
    else:
        flash('User not found.', 'error')
        return redirect(url_for('home'))
    
    
    return render_template('user_profile.html', user=user)

#user charts
@app.route('/user_charts', methods=['GET'])
@login_required
def user_charts():
    # Example data for charts
    parking_lots = Parking_lot.query.all()
    users = User.query.all()
    bookings = Booking.query.all()
    # For charts
    parking_lot = {
        'labels': [lot.name for lot in parking_lots],
        'data': [lot.price_per_hour for lot in parking_lots]
    }
    bookings_data = {
        'labels': [user.username for user in users],
        'data': [bookings.booking.count() for user in users]
    }
    
    return render_template('user_charts.html', parking_lot=parking_lot, bookings_data=bookings_data)
    
#search
@app.route('/admin_search', methods=['GET'])
@login_required
def admin_search():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Please enter a search term.', 'error')
    if query:
        parking_lots = Parking_lot.query.filter(Parking_lot.name.ilike(f'%{query}%')).all()
        parking_spots = Parking_spot.query.filter(Parking_spot.spot_number.ilike(f'%{query}%')).all()
        bookings = Booking.query.filter(Booking.vehicle_no.ilike(f'%{query}%')).all()
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    else:
        parking_lots = []
        parking_spots = []
        bookings = []
    return render_template('search.html', parking_lots=parking_lots, parking_spots=parking_spots, bookings=bookings)



# user search
@app.route('/user_search', methods=['GET'])
@login_required
def user_search():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Please enter a search term.', 'error')
    if query:
        parking_lots = Parking_lot.query.filter(Parking_lot.name.ilike(f'%{query}%')).all()
        parking_spots = Parking_spot.query.filter(Parking_spot.spot_number.ilike(f'%{query}%')).all()
        bookings = Booking.query.filter(Booking.vehicle_no.ilike(f'%{query}%')).all()
    else:
        parking_lots = []
        parking_spots = []
        bookings = []
    return render_template('user_search.html', parking_lots=parking_lots, parking_spots=parking_spots, bookings=bookings)

    
    
    
# view all parking lots
@app.route('/admin/view_all_parking_lots', methods=['GET'])
@login_required
def view_all_parking_lots():
    parking_lots = Parking_lot.query.all()
    active_bookings = dict(
        db.session.query(
            Booking.parking_lot_id,
            func.count(Booking.id)
        ).filter(
            Booking.spot_no.isnot(None),
            Booking.end_time > datetime.now()  # Or Booking.is_active == True
        ).group_by(Booking.parking_lot_id).all()
    )

    # Step 3: Annotate each lot with available_spaces
    for lot in parking_lots:
        booked = active_bookings.get(lot.id, 0)
        lot.available_spaces = lot.max_no_spots - booked
        
    return render_template('view_all_parking_lot.html', parking_lots=parking_lots)



# view all parking spots
@app.route('/view_parking_spots', methods=['GET'])
@login_required
def view_parking_spots():
    parking_spots = Parking_spot.query.all()
    return render_template('view_parking_spots.html', parking_spots=parking_spots)


# view all bookings
@app.route('/view_bookings', methods=['GET'])
@login_required
def view_bookings():
    bookings = Booking.query.all()
    return render_template('view_bookings.html', bookings=bookings)



# view all users
@app.route('/admin/view_users', methods=['GET'])
@login_required
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)


@app.route("/")
def home():
    Parking_lots = Parking_lot.query.all()
    return render_template('start.html', Parking_lots=Parking_lots)

@app.route('/admin/create_parking_lot', methods=['GET', 'POST'])
@login_required
def create_parking_lot():
    if request.method == 'POST':
      
        name = request.form['name']
        prime_location = request.form['prime_location']
        address = request.form['address']
        price_per_hour = float(request.form['price_per_hour'])
        max_no_spots = int(request.form['max_no_spots'])

        # Check if the parking lot already exists
        existing_parking_lot = Parking_lot.query.filter_by(name=name).first()
        if existing_parking_lot:
            flash('Parking lot with this name already exists.', 'error')
            return redirect(url_for('create_parking_lot'))

        # Create a new parking lot
        parking_lot = Parking_lot(
            name=name,
            prime_location=prime_location,
            address=address,
            price_per_hour=price_per_hour,
            max_no_spots=max_no_spots,
            user_id=current_user.id
        )
        
        db.session.add(parking_lot)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
        flash('Parking lot created successfully!', 'success')
    return render_template('create_parking_lot.html')


#Edit parking lot
@app.route('/edit_parking_lot/<int:parking_lot_id>', methods=['GET', 'POST'])
@login_required
def edit_parking_lot(parking_lot_id):
    parking_lot = Parking_lot.query.get_or_404(parking_lot_id)
    if request.method == 'POST':
        parking_lot.name = request.form.get('name')
        parking_lot.prime_location = request.form.get('prime_location')
        parking_lot.address = request.form.get('address')
        parking_lot.max_no_spots = int(request.form.get('max_no_spots'))
        parking_lot.price_per_hour = float(request.form.get('price_per_hour'))
        
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        #return redirect(url_for('admin_dashboard'))
    return render_template('edit_parking_lot.html', parking_lot=parking_lot)


#delete parking lot
@app.route('/delete_parking_lot/<int:parking_lot_id>', methods=['GET', 'POST'])
@login_required
def delete_parking_lot(parking_lot_id):
    parking_lot = Parking_lot.query.get_or_404(parking_lot_id)
    db.session.delete(parking_lot)
    db.session.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))



#Reserve parking spot
@app.route('/reserve_parking_spot/<int:parking_lot_id>', methods=['GET', 'POST'])
@login_required
def reserve_parking_spot(parking_lot_id):
    parking_lot = Parking_lot.query.get_or_404(parking_lot_id)
    available_spots = Parking_spot.query.filter_by(parking_lot_id=parking_lot.id, is_available=True).all()
    if request.method == 'POST':
        spot_number = request.form.get('spot_number')
        in_time = request.form.get('in_time')
        vehicle_number = request.form.get('vehicle_number')
        parking_spot = Parking_spot.query.filter_by(parking_lot_id=parking_lot.id, spot_number=spot_number).first()
        if parking_spot and parking_spot.is_available:
            booking = Booking(
                user_id=current_user.id,
                parking_lot_id=parking_lot.id,
                parking_spot_id=parking_spot.id,
                #in_time=in_time
                vehicle_number=vehicle_number
            )
            db.session.add(booking)
            parking_spot.is_available = False
            db.session.commit()
            flash('Parking spot reserved successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Parking spot is not available.', 'error')
    return render_template('booking.html', parking_lot=parking_lot, available_spots=available_spots)


#Release parking spot
@app.route('/release_parking_spot/<int:booking_id>', methods=['POST'])
@login_required
def release_parking_spot(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    parking_spot = Parking_spot.query.get(booking.parking_spot_id)
    if parking_spot:
        parking_spot.is_available = True
        db.session.delete(booking)
        db.session.commit()
        flash('Parking spot released successfully!', 'success')
    else:
        flash('Parking spot not found.', 'error')
    return redirect(url_for('home'))


#delete parking spot
@app.route('/admin/delete_parking_spot/<int:parking_spot_id>', methods=['POST'])
@login_required
def delete_parking_spot(parking_spot_id):
    parking_spot = Parking_spot.query.get_or_404(parking_spot_id)
    if not parking_spot.is_available:
        flash('Cannot delete a reserved parking spot.', 'error')
        return redirect(url_for('home'))
    else:
        db.session.delete(parking_spot)
        db.session.commit()
        flash('Parking spot deleted successfully!', 'success')
        return redirect(url_for('home'))
 
#search parking spot
@app.route('/admin/search_parking_spot', methods=['GET'])
@login_required
def search_parking_spot():
    query = request.args.get('query', '').strip()
    filter_by = request.args.get('filter_by', 'spot_number')

    parking_spots = []

    if query:
        if filter_by == 'spot_number':
            parking_spots = Parking_spot.query.filter(
                Parking_spot.spot_number.ilike(f'%{query}%')
            ).all()
        elif filter_by == 'user_id':
            parking_spots = Parking_spot.query.filter(
                Parking_spot.user_id.ilike(f'%{query}%')
            ).all()
        elif filter_by == 'location':
            parking_spots = Parking_spot.query.filter(
                Parking_spot.location.ilike(f'%{query}%')
            ).all()
    else:
        flash('Please enter a search term.', 'error')

    return render_template('admin_dashboard.html', parking_spots=parking_spots)
