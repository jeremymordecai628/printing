@app.route("/")
def home():
    maintenance_imgs = get_images("maintainance")
    printing_imgs = get_images("cyber")
    game_imgs = get_images("games")
    library_imgs = get_images("store")
    support_imgs = get_images("customer_care")
    return render_template(
        "index.html",
        maintenance_imgs=maintenance_imgs,
        printing_imgs=printing_imgs,
        game_imgs=game_imgs,
        library_imgs=library_imgs,
        support_imgs=support_imgs
    )

@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")


@app.route("/printing")
@login_required
def printing():
    return render_template("print.html")


@app.route("/networking")
def networking():
    return render_template("networking.html")


@app.route("/apps")
@login_required
def apps():
    cursor=conn.cursor()
    cursor.execute(
            "SELECT * FROM apps WHERE active=1"
            )
    data = cursor.fetchall()
    cursor.close()
    return render_template("app.html", apps=data)
            
@app.route("/admin", methods=["GET", "POST"])
def admin():
    file_info = None  # store DB result to pass to template

    if request.method == "POST":
        repo = request.form.get("link_value")
        initiate = request.form.get("value")
        doc_id = request.form.get("doc_id")

        try:
            # 1⃣ Create Promo Code
            if initiate:
                user = session.get("user_id")
                today = datetime.now()
                future_date = today + timedelta(days=30)
                code = generate_unique_code()

                if user_exists_with_media_role(conn, user):
                    sql = """
                        INSERT INTO promo_codes (user_id, code, expires_at)
                        VALUES (%s, %s, %s)
                    """
                    values = (user, code, future_date)
                    with conn.cursor() as cursor:
                        cursor.execute(sql, values)
                        conn.commit()
                    flash("✅ Promo code created successfully")
                else:
                    flash("❌ Unauthorized: role must be media")

            # 2⃣ Clone GitHub Repo
            elif repo:
                if not destination:
                    flash("❌ Destination folder not set in .env")
                else:
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    command = ["git", "clone", repo, destination]
                    result = subprocess.run(command, capture_output=True, text=True)
                    if result.returncode != 0:
                        flash(f"❌ Git clone failed: {result.stderr}")
                    else:
                        flash(f"✅ Repository cloned into: {destination}")

            # 3⃣ Retrieve file info
            elif doc_id:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT charges, amount_paid, status, file_name, user_id FROM payments WHERE id = %s",
                        (doc_id,)
                    )
                    result = cursor.fetchone()

                if not result:
                    flash("❌ Record not found")
                else:
                    filepath = result[3]  # file_name
                    if not os.path.exists(filepath):
                        flash("❌ File not found on server")
                    else:
                        # store info to pass to template
                        file_info = {
                            "charges": result[0],
                            "amount_paid": result[1],
                            "status": result[2],
                            "file_path": filepath
                        }
                        flash("✅ File ready for download")

            else:
                flash("❌ Invalid input provided")

            return render_template("admin.html", file_info=file_info)

        except Exception as e:
            flash(f"❌ An error occurred: {e}")

    # render template with file info if available
    return render_template("admin.html", file_info=file_info)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            next_page = request.form.get("next")

            hashed_password = hash_value(password)

            cursor =conn.cursor()
            cursor.execute(
                "SELECT id, role, password FROM users WHERE user_name = %s",
                (username,)
            )
            row = cursor.fetchone()
            cursor.close()

            if not row:
                flash("Invalid credentials", "danger")
                return redirect(url_for("signin"))

            if row["password"] == hashed_password:
                session["user_id"] = row["id"]
                session["username"] = username
                session["role"] = row["role"]

                flash("Login successful!", "success")

                print("NEXT:", next_page)

                return redirect(next_page or url_for("home"))

            flash("Invalid credentials", "danger")
            return redirect(url_for("signin"))

        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")
            return redirect(url_for("signin"))

    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            recipient = request.form.get("email")
            password = request.form.get("password")

            subject = "Welcome to Ressen Technologies"
            body = """<div style="
            max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:8px;
            box-shadow:0 4px 12px rgba(0,0,0,0.1);
            font-family:Arial, Helvetica, sans-serif;">
            <div style="background-color:#0f766e;padding:20px;text-align:center;color:#ffffff;
            border-radius:8px 8px 0 0;">
            <h2>Welcome to Ressen Technologies</h2>
            </div>
            <div style="padding:25px;color:#333333;">
            <p>Dear <strong>Valued User</strong>,</p>
            <p>Your account has been successfully created.</p>
            <p>You may now sign in and begin using our services.</p>
            <p>Kind regards,<br><strong>Ressen Technologies Team</strong></p>
            </div>
            </div>"""

            hashed_password = hash_value(password)


            send_email(recipient, subject, body)

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_name , password) VALUES (%s, %s)",
                (recipient, hashed_password)
            )
            conn.commit()
            cursor.close()

            flash("Account created successfully! Kindly sign in.", "success")
            return redirect(url_for("signin"))

        except Exception as e:
            traceback.print_exc()
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for("home"))
    

    # ✅ REQUIRED: handles GET requests
    return render_template("signup.html")

