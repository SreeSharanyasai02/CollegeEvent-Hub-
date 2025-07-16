from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

# Add this with your other global variables at the top
registrations = {}  # {event_id: [{'name': 'John', 'email': 'john@example.com'}, ...]}

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Static admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "iamadmin"

# Static organizer credentials
ORGANIZER_EMAIL = "organizer@gmail.com"
ORGANIZER_PASSWORD = "organizerpass"

# In-memory storage for events (in a real app, use a database)
events = [
    {
        'id': 1,
        'title': 'Coding Competition',
        'category': 'Technical',
        'dateTime': '2025-03-30T10:00',
        'venue': 'Main Auditorium',
        'maxParticipants': 100,
        'current_participants': 45,
        'regFee': 50,
        'description': 'Annual coding competition for all students',
        'status': 'Approved',
        'organizer': 'Organizer User',
        'banner': None
    },
    {
        'id': 2,
        'title': 'Design Workshop',
        'category': 'Workshop',
        'dateTime': '2025-04-15T14:00',
        'venue': 'Room 101',
        'maxParticipants': 50,
        'current_participants': 0,
        'regFee': 20,
        'description': 'Learn design principles from industry experts',
        'status': 'Pending',
        'organizer': 'Organizer User',
        'banner': None
    }
]

@app.route('/')
def home():
    return render_template("home1.html")

@app.route('/new')
def new_page():
    return render_template("new.html")

@app.route('/old')
def old_page():
    return render_template("old.html")

# Admin Login Route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email.strip() == ADMIN_EMAIL and password.strip() == ADMIN_PASSWORD:
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid email or password"

    return render_template("login1.html", error=error)

# Organizer Login Route
@app.route('/organizer-login', methods=['GET', 'POST'])
def organizer_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email.strip().lower() == ORGANIZER_EMAIL and password.strip() == ORGANIZER_PASSWORD:
            session['user'] = 'organizer'
            return redirect(url_for('organizer_dashboard'))
        
        error = "Invalid email or password"
    
    return render_template("login2.html", error=error)

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        # Accept ANY credentials and log the student in
        session['user'] = 'student'
        session['student_email'] = request.form.get('email', 'student@example.com')
        session['student_name'] = request.form.get('email', 'Student').split('@')[0]
        return redirect(url_for('student_dashboard'))
    
    return render_template("login3.html")

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('user') == 'admin':
        pending_events = [event for event in events if event['status'] == 'Pending']
        approved_events = [event for event in events if event['status'] == 'Approved']
        return render_template('admindashboard.html', 
                            pending_events=pending_events,
                            approved_events=approved_events)
    return redirect(url_for('admin_login'))

# Organizer Dashboard
@app.route('/organizer-dashboard')
def organizer_dashboard():
    if 'user' in session and session['user'] == 'organizer':
        organizer_events = [event for event in events if event['organizer'] == 'Organizer User']
        return render_template('organizerdashboard.html', events=organizer_events)
    print("🚨 Unauthorized access to organizer dashboard!")
    return redirect(url_for('organizer_login'))

# Handle event submission from organizer
@app.route('/submit-event', methods=['POST'])
def submit_event():
    if 'user' not in session or session['user'] != 'organizer':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Create new event
        new_event = {
            'id': len(events) + 1,
            'title': data['title'],
            'category': data['category'],
            'dateTime': data['dateTime'],
            'venue': data['venue'],
            'maxParticipants': int(data['maxParticipants']),
            'current_participants': 0,
            'regFee': float(data['regFee']),
            'description': data['description'],
            'status': data['status'],  # 'Pending' or 'Draft'
            'organizer': 'Organizer User',
            'banner': data.get('banner')  # Using get() as it might be optional
        }

        events.append(new_event)
        return jsonify({'success': True, 'message': 'Event submitted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get organizer's events
@app.route('/get-organizer-events')
def get_organizer_events():
    if 'user' not in session or session['user'] != 'organizer':
        return jsonify({'error': 'Unauthorized'}), 401

    organizer_events = [event for event in events if event['organizer'] == 'Organizer User']
    return jsonify(organizer_events)

# Approve/reject event from admin
@app.route('/update-event-status/<int:event_id>', methods=['POST'])
def update_event_status(event_id):
    if 'user' not in session or session['user'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        status = request.form.get('status')
        for event in events:
            if event['id'] == event_id:
                event['status'] = status
                return jsonify({'success': True, 'message': f'Event status updated to {status}'})
        
        return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Delete event (works for both admin and organizer)
@app.route('/delete-event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user' not in session or session['user'] not in ['admin', 'organizer']:
        return jsonify({'error': 'Unauthorized'}), 401

    global events
    initial_length = len(events)
    events = [event for event in events if event['id'] != event_id]
    
    if len(events) < initial_length:
        return jsonify({'success': True, 'message': 'Event deleted successfully'})
    else:
        return jsonify({'error': 'Event not found'}), 404

# ... (keep all your existing imports and configurations the same)

@app.route('/student-dashboard')
def student_dashboard():
    if 'user' not in session or session.get('user') != 'student':
        return redirect(url_for('student_login'))
    
    # Get all approved events
    approved_events = [event for event in events if event['status'] == 'Approved']
    
    # Format events for student dashboard display
    student_events = []
    for event in approved_events:
        try:
            event_date = datetime.strptime(event['dateTime'], '%Y-%m-%dT%H:%M')
            formatted_date = event_date.strftime('%b %d, %Y - %I:%M %p')
        except:
            formatted_date = event['dateTime']  # Fallback if parsing fails
            
        student_events.append({
            'id': event['id'],  # Added this line - CRUCIAL for registration
            'title': event['title'],
            'date': formatted_date,
            'description': event['description'],
            'category': event['category'],
            'current_participants': event['current_participants'],
            'max_participants': event['maxParticipants'],
            'fee': event['regFee'],
            'venue': event['venue']
        })
    
    return render_template('studentdashboard.html',
                         student_name=session.get('student_name', 'Student'),
                         student_email=session.get('student_email', 'student@example.com'),
                         events=student_events)
@app.route('/get-registrations/<int:event_id>')
def get_registrations(event_id):
    if 'user' not in session or session['user'] not in ['admin', 'organizer']:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(registrations.get(event_id, []))
# Remove ALL existing @app.route('/get-event') definitions
# Keep only this SINGLE version:

@app.route('/get-event/<int:event_id>')
def get_event(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if event:
        return jsonify({
            'id': event['id'],
            'title': event['title'],
            'current_participants': event['current_participants'],
            'max_participants': event['maxParticipants'],
            'status': event['status'],
            'fee': event['regFee']
        })
    return jsonify({'error': 'Event not found'}), 404

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))
@app.route('/stureg')
def stureg():
    if 'user' not in session or session['user'] != 'student':
        return redirect(url_for('student_login'))

    student_email = session.get('student_email')
    student_registrations = []

    for event_id, regs in registrations.items():
        for reg in regs:
            if reg['email'] == student_email:
                event = next((e for e in events if e['id'] == event_id), None)
                if event:
                    student_registrations.append({
                        'event_title': event['title'],
                        'event_date': event['dateTime'],
                        'venue': event['venue'],
                        'reg_time': reg['timestamp']
                    })

    return render_template('stureg.html', registrations=student_registrations)

@app.route('/register-event', methods=['POST'])
def register_event():
    if 'user' not in session or session['user'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    event_id = int(data.get('event_id'))
    student_name = data.get('name')
    student_email = data.get('email')
    student_phone = data.get('phone')
    roll_no = data.get('roll_no')
    branch = data.get('branch')
    section = data.get('section')

    if not all([event_id, student_name, student_email, roll_no, branch, section]):
        return jsonify({'error': 'Missing required fields'}), 400

    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if event['status'] != 'Approved':
        return jsonify({'error': 'Event is not approved for registration'}), 400
    if event['current_participants'] >= event['maxParticipants']:
        return jsonify({'error': 'Event is already full'}), 400

    if event_id not in registrations:
        registrations[event_id] = []

    if any(reg['email'] == student_email for reg in registrations[event_id]):
        return jsonify({'error': 'You are already registered for this event'}), 400

    registrations[event_id].append({
        'name': student_name,
        'email': student_email,
        'phone': student_phone,
        'roll_no': roll_no,
        'branch': branch,
        'section': section,
        'timestamp': datetime.now().isoformat(),
        'status': 'Paid',
        'amount': event['regFee'],
        'event': event['title']
    })

    event['current_participants'] += 1

    return redirect(url_for('stureg'))
# ... existing routes ...
@app.route('/display')
def display():
    return render_template('display.html')
    
@app.route('/about')
def about():
    return render_template('about.html')
     
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/organizer/registrations')
def organizer_registrations():
    if 'user' not in session or session['user'] != 'organizer':
        return redirect(url_for('organizer_login'))

    # Flatten all registrations with event info
    all_regs = []
    for event_id, regs in registrations.items():
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            continue
        for reg in regs:
            all_regs.append({
                'name': reg['name'],
                'email': reg['email'],
                'roll_no': reg['roll_no'],
                'branch': reg['branch'],
                'section': reg['section'],
                'event': reg['event'],
                'regDate': reg['timestamp'],
                'amount': reg['amount']
            })

    return render_template('registrations.html', all_regs=all_regs)

if __name__ == '__main__':
    app.run(debug=True)