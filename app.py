#!/usr/bin/python3
"""
Flask app to submit and retrieve student billing data from MySQL using PyMySQL
"""
from flask import Flask, render_template, request, redirect, jsonify, render_template_string, make_response
from io import BytesIO
from xhtml2pdf import pisa
import pymysql

app = Flask(__name__)

# MySQL connection setup
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1412",
    database="school_db",
    cursorclass=pymysql.cursors.DictCursor,
    charset='utf8mb4'
)

@app.route('/')
def form():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM billing ")
            records = cursor.fetchall()
        return render_template('form.html', records=records)
    except Exception as e:
        return f"Error loading records: {e}"

@app.route('/search', methods=['GET'])
def search():
    student_id = request.args.get('student_id', '').strip()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM billing WHERE student_id = %s", (student_id,))
            records = cursor.fetchall()
        return render_template('form.html', records=records)
    except Exception as e:
        return f"Search Error: {e}"

@app.route('/submit', methods=['POST'])
def submit():
    student_id = request.form.get('student_id', '').strip()
    name = request.form.get('name', '').strip()
    amount = request.form.get('amount', '').strip()
    binding = request.form.get('binding', '').strip()
    status = request.form.get('status', '').strip()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO billing (student_id, name, amount, binding, status) VALUES (%s, %s, %s, %s, %s)",
                (student_id, name, amount, binding, status)
            )
        conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Database Error: {e}"

@app.route('/update', methods=['POST'])
def update():
    student_id = request.form.get('student_id', '').strip()
    name = request.form.get('name', '').strip()
    amount = request.form.get('amount', '').strip()
    binding = request.form.get('binding', '').strip()
    status = request.form.get('status', '').strip()

    fields = []
    values = []

    if name:
        fields.append("name = %s")
        values.append(name)
    if amount:
        fields.append("amount = %s")
        values.append(amount)
    if binding:
        fields.append("binding = %s")
        values.append(binding)
    if status:
        fields.append("status = %s")
        values.append(status)

    if not fields:
        return "No fields to update."

    values.append(student_id)

    try:
        with conn.cursor() as cursor:
            query = f"UPDATE billing SET {', '.join(fields)} WHERE student_id = %s"
            cursor.execute(query, values)
        conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Update Error: {e}"

@app.route('/download')
def download_pdf():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, student_id, name, status FROM billing")
            data = cursor.fetchall()
    except Exception as e:
        return f"PDF Generation Error: {e}"

    html = render_template_string("""
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
        <h2>Billing Report</h2>
        <table border="1" cellspacing="0" cellpadding="4">
            <tr><th>ID</th><th>Student ID</th><th>Name</th><th>Status</th></tr>
            {% for row in data %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.student_id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.status }}</td>
            </tr>
            {% endfor %}
        </table>
        </body>
        </html>
    """, data=data)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    if pisa_status.err:
        return "Error generating PDF"

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True)

