from flask import render_template, redirect, url_for, session, json, request
from flask_login import login_required, logout_user
from gta.main import bp as mbp
from gta.model.models import Users, Jobs, Roles, Courses, Applications
from gta.extensions import login_manager
from flask_bootstrap import Bootstrap5
from flask import current_app as app
from gta.extensions import db

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@mbp.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for("main.Home"))

@mbp.route('/')
def Home():
    with app.app_context():
        resj = db.session.execute(db.select(Courses.course_name, Jobs.certification_required, Roles.role_name, Courses.course_level, Courses.course_id).where(Jobs.role_id == Roles.role_id).where(Jobs.course_required == Courses.course_id)).all()
        resc = db.session.execute(db.select(Courses.course_id, Courses.course_name, Courses.course_level)).all()
        resr = db.session.execute(db.select(Roles.role_id, Roles.role_name).where(Roles.role_id > 2).where(Roles.role_id < 5)).all()
    roles = [(r[0], r[1]) for r in resr]
    roles.insert(0, ("", "---"))
    courses = [(r[0], f"{r[1]} - {r[2]}") for r in resc]
    courses.insert(0, ("", "---"))
    jobs = [r for r in resj]
    jobs2 = [list(r) for r in resj]
    for j in jobs2:
        for i in j:
            if i is True or i == "True":
                j[1] = 1
            elif i is False or i == "False":
                j[1] = 0
    jobs2 = [tuple(j) for j in jobs2]
    return render_template("index.html", jobs=jobs, jobs2=jobs2, courses=courses, roles=roles)

@mbp.route('/getjobs', methods=["POST"])
def GetJobs():
    if request.method == "POST":
        j = request.json
        with app.app_context():
            print(j["course"])
            if j["course"] == "":
                j["course"] = Jobs.course_required
            if j["role"] == "":
                j["role"] = Jobs.role_id
            if j["cert"] == "" or j["cert"] == "false" or j["cert"] is False:
                j["cert"] = Jobs.certification_required
            resj = db.session.execute(db.select(Jobs.job_id, Courses.course_id, Courses.course_name, Courses.course_level, Jobs.certification_required, Roles.role_id, Roles.role_name).where(Jobs.role_id == Roles.role_id).where(Jobs.course_required == Courses.course_id).where(Jobs.course_required == j["course"]).where(Jobs.role_id == j["role"]).where(Jobs.certification_required == j["cert"])).all()
        jobs = [tuple(j) for j in resj]
        jobsd = {}
        for i,j in enumerate(jobs):
            jobsd[i] = {
                "job_id": j[0],
                "course_id": j[1], 
                "course_name": j[2],
                "course_level": j[3],
                "course_full": j[2] + " - " + j[3] + " ",
                "cert": j[4],
                "role_id": j[5],
                "role_name": j[6]
            }
        return json.dumps(jobsd)

@mbp.route('/jobs', methods=['GET'])
@login_required
def JobsPage():
    with app.app_context():
        resj = db.session.execute(db.select(Courses.course_name, Jobs.certification_required, Roles.role_name).where(Jobs.user_id == session["_user_id"]).where(Jobs.role_id == Roles.role_id).where(Jobs.course_required == Courses.course_id)).all()
    for r in resj:
        print(r)
    jobs = [r for r in resj]
    
    return render_template('jobs.html', jobs = resj)

@mbp.route('/applications', methods=['GET'])
@login_required
def ApplicationsPage():
    return render_template('applications.html')

@mbp.route('/admin')
@login_required
def AdminPage():
    with app.app_context():
        resj = db.session.execute(db.select(Courses.course_name, Courses.course_level, Jobs.certification_required, Roles.role_name).where(Jobs.role_id == Roles.role_id).where(Jobs.course_required == Courses.course_id)).all()
        resa = db.session.execute(db.select(Users.user_id, Courses.course_name, Courses.course_level, Applications.status, Applications.status, Applications.gta_cert, Applications.transcript, Roles.role_name, Jobs.job_id).where(Applications.user_id == Users.user_id).where(Applications.course_id == Courses.course_id).where(Applications.job_id == Jobs.job_id).where(Jobs.role_id == Roles.role_id)).all()
        all_users = Users.query.all()

    jobs = [{"course": r[0]+" - "+r[1], "cert_required": r[2], "role_name": r[3]} for r in resj]
    apps = [{"user_id": a[0], "course": a[1]+" - "+a[2], "status": a[3], "gta_cert": a[4], "transcript": a[5], "role": a[7], "job_id": a[8]} for a in resa]
    users = [{
        "user_id": user.user_id,
        "fname": user.user_fname,
        "lname": user.user_lname,
        "email": user.user_email,
        "role": user.role,
        "major": user.major,
        # ... add or remove other attributes as needed
    } for user in all_users]
    return render_template('admin.html',jobs=jobs, apps=apps, users=users)

