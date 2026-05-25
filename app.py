from flask import Flask, render_template, request, redirect, session
import pymysql

print("Starting app...")
print("Trying PyMySQL connection...")

try:
    conn = pymysql.connect(
        host="mysql.railway.internal",
        user="root",
        password="SjZEByEemVZZONYqUjSPsUrRnrwxqoMA",
        database="railway",
        port=3306
    )
    cursor = conn.cursor()
    print("PyMySQL connected successfully")

except Exception as e:
    print("Database connection failed")
    print(e)

app = Flask(__name__)
app.secret_key = "secret123"   # 🔐 required for session


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    # 🔁 auto redirect if already logged in
    if "user_id" in session:
        if session["role"] == "donor":
            return redirect("/donor/dashboard")
        else:
            return redirect("/collector/dashboard")

    return render_template("index.html")


# ---------------- REGISTER PAGES ---------------- #

@app.route("/collector/register")
def collector_register():
    return render_template("collector_register.html")


@app.route("/donor/register")
def donor_register():
    return render_template("donor_register.html")


# ---------------- REGISTER LOGIC ---------------- #

@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name")
    phone = request.form.get("phone")
    role = request.form.get("role")

    # donor fields
    location = request.form.get("location")
    food_details = request.form.get("food_details")

    # collector fields
    area = request.form.get("area")
    user_type = request.form.get("type")

    # handle donor vs collector
    final_location = location if role == "donor" else area

    query = """
    INSERT INTO users (name, phone, location, food_details, type, role)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        phone,
        final_location,
        food_details,
        user_type,
        role
    )

    cursor.execute(query, values)
    conn.commit()

    # ✅ STORE SESSION (important)
    session["user_id"] = cursor.lastrowid
    session["role"] = role
    session["name"] = name

    print("User Registered Successfully")

    # ✅ REDIRECT BASED ON ROLE
    if role == "donor":
        return redirect("/donor/dashboard")
    else:
        return redirect("/collector/dashboard")


# ---------------- DASHBOARDS ---------------- #

@app.route("/donor/dashboard")
def donor_dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("donor_dashboard.html", name=session["name"])


@app.route("/collector/dashboard")
def collector_dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("collector_dashboard.html", name=session["name"])


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)