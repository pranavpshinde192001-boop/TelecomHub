import bcrypt
import mysql.connector
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template, request, session, redirect, flash

app = Flask(__name__)
app.secret_key = "telesupport_secret"


db = mysql.connector.connect(
    host="telesupport-db.cjog40uyo8xw.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="India11tejas",
    database="telesupport",
)

cursor = db.cursor()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = """
        INSERT INTO customers
        (name, mobile, email, password, address)
        VALUES (%s,%s,%s,%s,%s)
        """

        values = (
            name,
            mobile,
            email,
            hashed_password,
            address,
        )

        cursor.execute(query, values)
        db.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        query = """
        SELECT * FROM customers
        WHERE email=%s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user:

            stored_password = user[4] or ""
            password_ok = False

            if stored_password.startswith("$2"):
                password_ok = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            elif stored_password == password:
                password_ok = True
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "UPDATE customers SET password=%s WHERE id=%s",
                    (hashed_password, user[0]),
                )
                db.commit()

            if password_ok:
                session['customer_id'] = user[0]
                session['customer_name'] = user[1]

                return redirect('/dashboard')

        flash("Invalid credentials. Please try again.", "danger")
        return redirect('/login')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'customer_id' not in session:
        return redirect('/login')

    cursor.execute(
        "SELECT COUNT(*) FROM purchases WHERE customer_id=%s",
        (session['customer_id'],),
    )
    total_purchases = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE customer_id=%s",
        (session['customer_id'],),
    )
    total_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE customer_id=%s AND status=%s",
        (session['customer_id'], 'Open'),
    )
    open_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE customer_id=%s AND status=%s",
        (session['customer_id'], 'Resolved'),
    )
    resolved_tickets = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT id, description, plan_type, priority, status, date_raised
        FROM tickets
        WHERE customer_id=%s
        ORDER BY date_raised DESC
        LIMIT 5
        """,
        (session['customer_id'],),
    )
    recent_tickets = cursor.fetchall()

    return render_template(
        'dashboard.html',
        name=session['customer_name'],
        total_purchases=total_purchases,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        recent_tickets=recent_tickets,
    )


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


@app.route('/raise-ticket', methods=['GET', 'POST'])
def raise_ticket():

    if 'customer_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        description = request.form['description']
        plan_type = request.form['plan_type']
        priority = request.form['priority']

        query = """
        INSERT INTO tickets
        (customer_id, description, plan_type, priority)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                session['customer_id'],
                description,
                plan_type,
                priority,
            ),
        )

        db.commit()

        ticket_id = cursor.lastrowid
        flash(f"Ticket #{ticket_id} created successfully.", "success")
        return redirect('/my-tickets')

    return render_template('raise_ticket.html')


@app.route('/my-tickets')
def my_tickets():

    if 'customer_id' not in session:
        return redirect('/login')

    cursor.execute(
        "SELECT * FROM tickets WHERE customer_id=%s",
        (session['customer_id'],),
    )

    tickets = cursor.fetchall()

    return render_template(
        'my_tickets.html',
        tickets=tickets,
    )


@app.route('/buy-service', methods=['GET', 'POST'])
def buy_service():

    if 'customer_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        service_name = request.form['service_name']

        query = """
        INSERT INTO purchases
        (customer_id, service_name)
        VALUES (%s,%s)
        """

        cursor.execute(
            query,
            (
                session['customer_id'],
                service_name,
            ),
        )

        db.commit()

        purchase_id = cursor.lastrowid
        flash(f"Service purchase #{purchase_id} completed successfully.", "success")
        return redirect('/my-purchases')

    return render_template('buy_service.html')


@app.route('/my-purchases')
def my_purchases():

    if 'customer_id' not in session:
        return redirect('/login')

    cursor.execute(
        """
        SELECT * FROM purchases
        WHERE customer_id=%s
        """,
        (session['customer_id'],),
    )

    purchases = cursor.fetchall()

    return render_template(
        'my_purchases.html',
        purchases=purchases,
    )


@app.route('/agent-login', methods=['GET', 'POST'])
def agent_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            """
            SELECT * FROM agents
            WHERE email=%s
            """,
            (email,),
        )

        agent = cursor.fetchone()

        if agent:

            stored_password = agent[3] if len(agent) > 3 else ""
            password_ok = False

            if stored_password.startswith("$2"):
                password_ok = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            elif stored_password == password:
                password_ok = True
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "UPDATE agents SET password=%s WHERE id=%s",
                    (hashed_password, agent[0]),
                )
                db.commit()

            if password_ok:
                session['agent_id'] = agent[0]
                session['agent_name'] = agent[1]

                return redirect('/agent-dashboard')

        flash("Invalid agent credentials. Please try again.", "danger")
        return redirect('/agent-login')

    return render_template('agent_login.html')


@app.route('/agent-dashboard')
def agent_dashboard():

    if 'agent_id' not in session:
        return redirect('/agent-login')

    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status=%s", ('Open',))
    open_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status=%s", ('Resolved',))
    resolved_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE priority=%s AND status!=%s",
        ('High', 'Resolved'),
    )
    high_priority_tickets = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT t.id, c.name, t.description, t.priority, t.status
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        ORDER BY t.date_raised DESC
        LIMIT 5
        """,
    )
    recent_tickets = cursor.fetchall()

    cursor.execute(
        """
        SELECT t.id, c.name, t.description, t.priority, t.status
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.priority=%s AND t.status!=%s
        ORDER BY t.date_raised DESC
        LIMIT 5
        """,
        ('High', 'Resolved'),
    )
    priority_queue = cursor.fetchall()

    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    status_rows = cursor.fetchall()
    status_labels = [row[0] for row in status_rows]
    status_values = [row[1] for row in status_rows]

    cursor.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
    priority_rows = cursor.fetchall()
    priority_labels = [row[0] for row in priority_rows]
    priority_values = [row[1] for row in priority_rows]

    cursor.execute("SELECT service_name, COUNT(*) FROM purchases GROUP BY service_name")
    service_rows = cursor.fetchall()
    service_labels = [row[0] for row in service_rows]
    service_values = [row[1] for row in service_rows]

    status_chart = go.Figure(
        data=[
            go.Pie(
                labels=status_labels,
                values=status_values,
                hole=0.45,
                marker=dict(colors=['#06b6d4', '#f97316', '#22c55e', '#8b5cf6']),
            )
        ]
    )
    status_chart.update_layout(
        title="Tickets by Status",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=True,
    )

    priority_chart = go.Figure(
        data=[
            go.Pie(
                labels=priority_labels,
                values=priority_values,
                hole=0.45,
                marker=dict(colors=['#ef4444', '#f59e0b', '#22c55e']),
            )
        ]
    )
    priority_chart.update_layout(
        title="Tickets by Priority",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=True,
    )

    purchase_chart = go.Figure(
        data=[
            go.Bar(
                x=service_labels,
                y=service_values,
                marker=dict(color=['#4f46e5', '#06b6d4', '#8b5cf6', '#22c55e', '#f59e0b']),
            )
        ]
    )
    purchase_chart.update_layout(
        title="Service Purchases",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(l=20, r=10, t=50, b=40),
        xaxis_tickangle=-20,
    )

    return render_template(
        'agent_dashboard.html',
        name=session['agent_name'],
        total_customers=total_customers,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        high_priority_tickets=high_priority_tickets,
        recent_tickets=recent_tickets,
        priority_queue=priority_queue,
        tickets_status_chart=pio.to_html(status_chart, full_html=False, include_plotlyjs=False),
        tickets_priority_chart=pio.to_html(priority_chart, full_html=False, include_plotlyjs=False),
        purchases_chart=pio.to_html(purchase_chart, full_html=False, include_plotlyjs=False),
    )


@app.route('/agent-logout')
def agent_logout():

    session.clear()

    return redirect('/')


@app.route('/all-tickets')
def all_tickets():

    if 'agent_id' not in session:
        return redirect('/agent-login')

    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')

    query = """
        SELECT t.id, t.customer_id, c.name, t.description, t.plan_type, t.priority, t.status
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
    """
    conditions = []
    params = []

    if status_filter != 'all':
        conditions.append("t.status=%s")
        params.append(status_filter)

    if search:
        like_search = f"%{search}%"
        if search.isdigit():
            conditions.append("(t.id=%s OR c.name LIKE %s OR t.status LIKE %s)")
            params.extend([int(search), like_search, like_search])
        else:
            conditions.append("(c.name LIKE %s OR t.status LIKE %s)")
            params.extend([like_search, like_search])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY t.date_raised DESC"

    cursor.execute(query, tuple(params))

    tickets = cursor.fetchall()

    return render_template(
        'all_tickets.html',
        tickets=tickets,
        search=search,
        status_filter=status_filter,
    )


@app.route('/update-ticket/<int:ticket_id>', methods=['POST'])
def update_ticket(ticket_id):

    if 'agent_id' not in session:
        return redirect('/agent-login')

    status = request.form['status']

    cursor.execute(
        """
        UPDATE tickets
        SET status=%s
        WHERE id=%s
        """,
        (status, ticket_id),
    )

    db.commit()

    if status == 'Resolved':
        flash(f"Ticket #{ticket_id} has been resolved.", "success")
    else:
        flash(f"Ticket #{ticket_id} updated to {status}.", "success")
    return redirect('/all-tickets')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
