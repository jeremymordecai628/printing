from flask import Blueprint, request, render_template, redirect, url_for, flash, session, abort, send_file, make_response, render_template_string, jsonify
from io import BytesIO
from PyPDF2 import PdfReader
from xhtml2pdf import pisa
import os
import json   
from extensions import db
from models import  User, Payment, PromoCode,AssignCode,App, verify, login_required, apply_code, hash_value,Download,  assign_id
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


process_bp = Blueprint('process', __name__)
@process_bp.route("/downloadapp", methods=["GET", "POST"])
@login_required
@apply_code
def  downloadapp():
    if request.methods=="POST":
        #I will place the logic to download apps here  
        return render_template("test.html")
    return render_template("test.html")

@process_bp.route("/initialiseapp", methods=["GET", "POST"])
def initialiseapp():
    if request.method == "POST":
        try:
            payload = {
                "username": request.form.get("username"),
                "password": request.form.get("password")
            }

            appidentifier = request.form.get("appid")

            user = verify(payload)
            hashed_password = hash_value(payload["password"])

            if not user or user.password != hashed_password:
                return jsonify({"message": "invalid credentials"}), 401

            # get app package
            Data = db.session.query(App.package)\
                .filter(App.status == "Active", App.id == appidentifier)\
                .first()

            if not Data or not Data[0]:
                return jsonify({"message": "Error occurred while retrieving data"}), 401

            packages = Data[0]

            # normalize packages into list
            if isinstance(packages, str):
                packages = json.loads(packages)

            if isinstance(packages, dict):
                packages = [packages]

            if packages is None:
                packages = []

            # generate download id
            criteria = db.session.query(Download.download_id)\
                .order_by(Download.download_id.desc())\
                .first()

            latest_id = criteria.download_id if criteria else None
            down_id = assign_id(latest_id)

            if not down_id:
                return jsonify({"message": "Error generating download id"}), 500

            # save download
            new_download = Download(
                download_id=down_id,
                user_id=user.id,
                app_id=int(appidentifier)
            )

            db.session.add(new_download)
            db.session.commit()

            # append AFTER normalization (always safe now)
            packages.append({
                "client_id": user.id,
                "downloadid": down_id
            })

            return jsonify({
                "message": "Validation successful",
                "packages": packages
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

# -------------------------
# Promo
# -------------------------
@process_bp.route("/process_bply_promo", methods=["GET", "POST"])
@login_required
def process_bp_promo():
    if request.method == "POST":
        try:
            promo = request.form.get("promo")
            next_page = request.form.get("next")

            row =db.session.query(User, PromoCode).join(PromoCode, User.id == PromoCode.user_id).filter(PromoCode.code == promo, PromoCode.status.in_(["Active", "Terminated"])).first()

            if not row:
                flash("Invalid code", "danger")
                return redirect(next_page or url_for("pages.home")) 

            new_count = row.used_count +1
            user, promo_obj = row
            if PromoCode.status=="Active":
                if new_count>= row.max_uses:
                    # send email
                    send_email(
                            row.user_name,
                            "Hello this is to inform you that your promo code has expired",
                            "<h3>Promo code expired</h3>"
                            )
                    # update promo table
                    promo_obj.status="Terminated"
                    promo_obj.used_count= new_count
                    flash ("Sorry code  expired")

                else :
                    #update used_count
                    promo_obj.used_count= new_count
                    flash("Succeded Thanks for participating")
            else :
                promo_obj.used_count= new_count
                flash ("Sorry code  expired")

            return redirect(next_page or url_for("process_bply_promo"))
        

        except Exception as e:
            flash("Promo system unavailable", "danger")
            return redirect(url_for("process_bply_promo"))

        return render_template("apply.html")

# -------------------------
# Manage
# -------------------------
@process_bp.route('/manage')
def form():
    try:
        records = Billing.query.all()

        project_records = [
            r for r in records if r.binding != 0 and r.status != "printed"
        ]

        printed_records = [
            r for r in records if r.status == "printed" and r.binding != 0
        ]

        return render_template(
            'form.html',
            records=records,
            prints=printed_records,
            projects=project_records
        )

    except Exception as e:
        return f"Error loading records: {e}"


# -------------------------
# Search
# -------------------------
@process_bp.route('/search', methods=['GET'])
def search():
    student_id = request.args.get('student_id', '').strip()

    try:
        records = Billing.query.filter_by(student_id=student_id).all()
        return render_template('form.html', records=records)

    except Exception as e:
        return f"Search Error: {e}"


# -------------------------
# Upload
# -------------------------
@process_bp.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        student_id = session.get('user_id')
        file = request.files.get("file")

        try:
            if file and allowed_file(file.filename):

                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                new_work = Work(
                    student_id=student_id,
                    filepath=filepath
                )

                db.session.add(new_work)
                db.session.commit()

                flash("File uploaded successfully!", "success")
                return redirect(url_for('process.upload_page'))

            flash("Invalid file type", "danger")
            return redirect(url_for('process.upload_page'))

        except Exception as e:
            flash(f"Database Error: {e}", "danger")
            return redirect(url_for('process.upload_page'))

    return render_template('print.html')


# -------------------------
# Update + pricing
# -------------------------
@process_bp.route('/update', methods=['POST'])
def update():
    work_id = request.form.get('work_id', '').strip()
    bind = request.form.get('binding', '').strip()

    is_bind = bind == 'true'

    work = Work.query.filter_by(work_id=work_id).first()

    if not work:
        abort(404, "No file found")

    filepath = work.filepath

    if not os.path.isfile(filepath):
        abort(404, "File missing on server")

    reader = PdfReader(filepath)
    page_count = len(reader.pages)

    price = (page_count * 20) + (50 if is_bind else 0)

    work.binding = is_bind
    work.price = price

    db.session.commit()

    response = send_file(filepath, as_attachment=True)
    response.headers['X-Price'] = str(price)
    return response


# -------------------------
# Download PDF
# -------------------------
@process_bp.route('/download')
def download_pdf():
    try:
        data = Billing.query.filter_by(status="printed").all()

    except Exception as e:
        return f"PDF Error: {e}"

    html = render_template_string("""
        <h2>Billing Report</h2>
        <table border="1">
            <tr>
                <th>#</th>
                <th>Student ID</th>
                <th>Name</th>
                <th>Status</th>
            </tr>
            {% for row in data %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ row.student_id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.status }}</td>
            </tr>
            {% endfor %}
        </table>
    """, data=data)

    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer)

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response


# -------------------------
# Logout
# -------------------------
@process_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("pages.signin"))
