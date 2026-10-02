import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename

from ml.disaster_classifier import DisasterClassifier
from ml.severity_predictor import SeverityPredictor
from ml.priority import PriorityCalculator
from ml.similarity import SimilarityChecker

from backend.response_queue import ResponseQueue
from backend.rescue_team import RescueTeam, RescueTeamManager


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "disaster-response-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///disaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}


def allowed_file(filename):
    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# AI / ML COMPONENTS
# =========================================================

classifier = DisasterClassifier()
severity_predictor = SeverityPredictor()
priority_calculator = PriorityCalculator()
similarity_checker = SimilarityChecker()


# =========================================================
# RESPONSE QUEUE
# =========================================================

response_queue = ResponseQueue()


# =========================================================
# RESCUE TEAM MANAGEMENT
# =========================================================

rescue_team_manager = RescueTeamManager()


# Sample rescue teams
rescue_team_manager.add_team(
    RescueTeam(
        team_id=1,
        name="Flood Rescue Team",
        team_type="Flood",
        location="Local Emergency Center",
        capacity=5
    )
)

rescue_team_manager.add_team(
    RescueTeam(
        team_id=2,
        name="Fire Rescue Team",
        team_type="Fire",
        location="Local Fire Station",
        capacity=5
    )
)

rescue_team_manager.add_team(
    RescueTeam(
        team_id=3,
        name="Disaster Response Team",
        team_type="General",
        location="Emergency Operations Center",
        capacity=10
    )
)


# =========================================================
# REPORT MODEL
# =========================================================

class Report(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    location = db.Column(
        db.String(200),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    disaster_type = db.Column(
        db.String(100),
        nullable=False
    )

    severity = db.Column(
        db.String(50),
        nullable=False
    )

    priority = db.Column(
        db.String(50),
        nullable=False
    )

    priority_score = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Pending"
    )

    image_filename = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=True,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # -----------------------------------------------------
    # PERSISTENT RESCUE TEAM ASSIGNMENT
    # -----------------------------------------------------

    assigned_team_id = db.Column(
        db.Integer,
        nullable=True
    )


# =========================================================
# STATUS HISTORY MODEL
# =========================================================

class StatusHistory(db.Model):

    __tablename__ = "status_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    report_id = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# DATABASE COLUMN MIGRATION
# =========================================================

with app.app_context():

    existing_columns = db.session.execute(
        text(
            "PRAGMA table_info(report)"
        )
    ).fetchall()

    column_names = [
        column[1]
        for column in existing_columns
    ]

    if "assigned_team_id" not in column_names:

        db.session.execute(
            text(
                """
                ALTER TABLE report
                ADD COLUMN assigned_team_id INTEGER
                """
            )
        )

        db.session.commit()


# =========================================================
# DATABASE TIMESTAMP MIGRATION
# =========================================================

with app.app_context():

    db.session.execute(
        text(
            """
            UPDATE report
            SET
                created_at = COALESCE(
                    created_at,
                    CURRENT_TIMESTAMP
                ),
                updated_at = COALESCE(
                    updated_at,
                    CURRENT_TIMESTAMP
                )
            WHERE
                created_at IS NULL
                OR updated_at IS NULL
            """
        )
    )

    db.session.commit()


# =========================================================
# STATUS HISTORY BACKFILL
# =========================================================

with app.app_context():

    existing_reports = Report.query.all()

    for existing_report in existing_reports:

        history_exists = StatusHistory.query.filter_by(
            report_id=existing_report.id
        ).first()

        if not history_exists:

            history_time = (
                existing_report.created_at
                or datetime.utcnow()
            )

            history_entry = StatusHistory(
                report_id=existing_report.id,
                status=existing_report.status,
                updated_at=history_time
            )

            db.session.add(history_entry)

    db.session.commit()


# =========================================================
# RESTORE RESCUE TEAM ASSIGNMENT COUNTS
# =========================================================

with app.app_context():

    for team in rescue_team_manager.get_all_teams():

        active_assignment_count = Report.query.filter(
            Report.assigned_team_id == team.team_id,
            Report.status != "Resolved"
        ).count()

        team.current_assignments = (
            active_assignment_count
        )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# REPORT PAGE
# =========================================================

@app.route("/report")
def report():

    return render_template(
        "report.html"
    )


# =========================================================
# SUBMIT EMERGENCY REPORT
# =========================================================

@app.route(
    "/submit-report",
    methods=["POST"]
)
def submit_report():

    location = request.form.get(
        "location",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    latitude = request.form.get(
        "latitude"
    )

    longitude = request.form.get(
        "longitude"
    )


    # -----------------------------------------------------
    # VALIDATE DESCRIPTION
    # -----------------------------------------------------

    if not description:

        return """
        <script>
            alert("Please describe the emergency.");
            window.location.href="/report";
        </script>
        """


    # -----------------------------------------------------
    # CONVERT LATITUDE
    # -----------------------------------------------------

    if latitude:

        try:
            latitude = float(latitude)

        except ValueError:
            latitude = None

    else:
        latitude = None


    # -----------------------------------------------------
    # CONVERT LONGITUDE
    # -----------------------------------------------------

    if longitude:

        try:
            longitude = float(longitude)

        except ValueError:
            longitude = None

    else:
        longitude = None


    # -----------------------------------------------------
    # AI DISASTER CLASSIFICATION
    # -----------------------------------------------------

    disaster_type = classifier.predict(
        description
    )


    # -----------------------------------------------------
    # AI SEVERITY PREDICTION
    # -----------------------------------------------------

    severity = severity_predictor.predict(
        description
    )


    # -----------------------------------------------------
    # PRIORITY CALCULATION
    # -----------------------------------------------------

    priority, priority_score = (
        priority_calculator.calculate(
            severity,
            disaster_type
        )
    )


    # -----------------------------------------------------
    # SIMILARITY / DUPLICATE DETECTION
    # -----------------------------------------------------

    existing_reports = Report.query.all()

    (
        similar_report,
        similarity_score,
        similarity_type
    ) = similarity_checker.check_similarity(
        description,
        existing_reports
    )


    # -----------------------------------------------------
    # IMAGE UPLOAD
    # -----------------------------------------------------

    image_filename = None

    if "evidence_image" in request.files:

        image = request.files[
            "evidence_image"
        ]

        if image and image.filename:

            if allowed_file(
                image.filename
            ):

                original_filename = (
                    secure_filename(
                        image.filename
                    )
                )

                import uuid

                unique_filename = (
                    str(uuid.uuid4())
                    + "_"
                    + original_filename
                )

                image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    unique_filename
                )

                image.save(
                    image_path
                )

                image_filename = (
                    unique_filename
                )

            else:

                return """
                <script>
                    alert(
                        "Invalid image format. Please upload PNG, JPG, JPEG, GIF, or WEBP."
                    );
                    window.location.href="/report";
                </script>
                """


    # -----------------------------------------------------
    # CREATE REPORT
    # -----------------------------------------------------

    current_time = datetime.utcnow()

    new_report = Report(

        location=location,

        latitude=latitude,

        longitude=longitude,

        description=description,

        disaster_type=disaster_type,

        severity=severity,

        priority=priority,

        priority_score=priority_score,

        status="Pending",

        image_filename=image_filename,

        created_at=current_time,

        updated_at=current_time,

        assigned_team_id=None
    )


    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    db.session.add(
        new_report
    )

    db.session.commit()


    # -----------------------------------------------------
    # INITIAL STATUS HISTORY
    # -----------------------------------------------------

    initial_history = StatusHistory(

        report_id=new_report.id,

        status="Pending",

        updated_at=current_time
    )

    db.session.add(
        initial_history
    )

    db.session.commit()


    # -----------------------------------------------------
    # SUCCESS PAGE
    # -----------------------------------------------------

    return render_template(

        "report_success.html",

        report=new_report,

        priority=priority,

        priority_score=priority_score,

        similar_report=similar_report,

        similarity_score=similarity_score,

        similarity_type=similarity_type
    )


# =========================================================
# SERVE UPLOADED FILES
# =========================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename
    )


# =========================================================
# ALL REPORTS
# =========================================================

@app.route("/reports")
def reports():

    all_reports = Report.query.order_by(

        Report.id.desc()

    ).all()

    return render_template(

        "reports.html",

        reports=all_reports
    )


# =========================================================
# REPORT TRACKING PAGE
# =========================================================

@app.route("/track")
def track_report():

    return render_template(
        "track_report.html"
    )


# =========================================================
# TRACK REPORT PROCESS
# =========================================================

@app.route(
    "/track-report",
    methods=["POST"]
)
def track_report_process():

    report_id = request.form.get(
        "report_id",
        ""
    ).strip()


    if not report_id:

        return """
        <script>
            alert("Please enter a Report ID.");
            window.location.href="/track";
        </script>
        """


    try:

        report_id = int(
            report_id
        )

    except ValueError:

        return """
        <script>
            alert("Please enter a valid Report ID.");
            window.location.href="/track";
        </script>
        """


    report = Report.query.filter_by(

        id=report_id

    ).first()


    if not report:

        return """
        <script>
            alert("Report ID not found. Please check the ID and try again.");
            window.location.href="/track";
        </script>
        """


    status_history = (
        StatusHistory.query
        .filter_by(
            report_id=report.id
        )
        .order_by(
            StatusHistory.updated_at.asc(),
            StatusHistory.id.asc()
        )
        .all()
    )


    return render_template(

        "track_report_result.html",

        report=report,

        status_history=status_history
    )


# =========================================================
# AUTHORITY LOGIN
# =========================================================

@app.route(
    "/authority/login"
)
def authority_login():

    return render_template(
        "authority/login.html"
    )


# =========================================================
# AUTHORITY LOGIN PROCESS
# =========================================================

@app.route(
    "/authority-login",
    methods=["POST"]
)
def authority_login_process():

    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )


    if (
        username == "admin"
        and
        password == "admin123"
    ):

        session[
            "authority_logged_in"
        ] = True

        return redirect(
            url_for(
                "authority_dashboard"
            )
        )


    return """
    <script>
        alert("Invalid username or password");
        window.location.href="/authority/login";
    </script>
    """


# =========================================================
# AUTHORITY DASHBOARD
# =========================================================

@app.route("/authority")
def authority_dashboard():

    if not session.get(
        "authority_logged_in"
    ):

        return redirect(
            url_for(
                "authority_login"
            )
        )


    # -----------------------------------------------------
    # GET ALL REPORTS
    # -----------------------------------------------------

    all_reports = Report.query.all()


    # -----------------------------------------------------
    # BUILD EMERGENCY RESPONSE QUEUE
    # -----------------------------------------------------

    queue_items = response_queue.build_queue(
        all_reports
    )


    queued_reports = [
        item["report"]
        for item in queue_items
    ]


    queue_summary = (
        response_queue.get_queue_summary(
            all_reports
        )
    )


    # -----------------------------------------------------
    # GET RESCUE TEAMS
    # -----------------------------------------------------

    rescue_teams = (
        rescue_team_manager.get_all_teams()
    )


    rescue_team_summary = (
        rescue_team_manager.get_summary()
    )


    # -----------------------------------------------------
    # SHOW DASHBOARD
    # -----------------------------------------------------

    return render_template(

        "authority/dashboard.html",

        reports=queued_reports,

        queue_summary=queue_summary,

        rescue_teams=rescue_teams,

        rescue_team_summary=rescue_team_summary
    )


# =========================================================
# AUTHORITY REPORT DETAILS
# =========================================================

@app.route(
    "/authority/report/<int:report_id>"
)
def authority_report_details(
    report_id
):

    if not session.get(
        "authority_logged_in"
    ):

        return redirect(
            url_for(
                "authority_login"
            )
        )


    report = Report.query.get_or_404(
        report_id
    )


    status_history = (
        StatusHistory.query
        .filter_by(
            report_id=report.id
        )
        .order_by(
            StatusHistory.updated_at.asc(),
            StatusHistory.id.asc()
        )
        .all()
    )


    assigned_team = None

    if report.assigned_team_id is not None:

        assigned_team = (
            rescue_team_manager.get_team(
                report.assigned_team_id
            )
        )


    return render_template(

        "authority/report_details.html",

        report=report,

        status_history=status_history,

        assigned_team=assigned_team
    )


# =========================================================
# ASSIGN REPORT TO RESCUE TEAM
# =========================================================

@app.route(
    "/authority/assign/<int:report_id>",
    methods=["POST"]
)
def assign_report_to_team(
    report_id
):

    if not session.get(
        "authority_logged_in"
    ):

        return redirect(
            url_for(
                "authority_login"
            )
        )


    # -----------------------------------------------------
    # CHECK REPORT
    # -----------------------------------------------------

    report = Report.query.get_or_404(
        report_id
    )


    # -----------------------------------------------------
    # CHECK EXISTING ASSIGNMENT
    # -----------------------------------------------------

    if report.assigned_team_id is not None:

        existing_team = (
            rescue_team_manager.get_team(
                report.assigned_team_id
            )
        )

        existing_team_name = (
            existing_team.name
            if existing_team
            else "another rescue team"
        )

        return f"""
        <script>
            alert(
                "This report is already assigned to {existing_team_name}."
            );
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # GET TEAM ID
    # -----------------------------------------------------

    team_id = request.form.get(
        "team_id"
    )


    if not team_id:

        return """
        <script>
            alert("Please select a rescue team.");
            window.history.back();
        </script>
        """


    try:

        team_id = int(
            team_id
        )

    except ValueError:

        return """
        <script>
            alert("Invalid rescue team.");
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # FIND TEAM
    # -----------------------------------------------------

    team = rescue_team_manager.get_team(
        team_id
    )


    if team is None:

        return """
        <script>
            alert("Rescue team not found.");
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # CHECK TEAM AVAILABILITY
    # -----------------------------------------------------

    if not team.is_available():

        return """
        <script>
            alert("This rescue team is currently unavailable.");
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # ASSIGN TEAM IN MEMORY
    # -----------------------------------------------------

    assigned = (
        rescue_team_manager.assign_report_to_team(
            team_id
        )
    )


    if not assigned:

        return """
        <script>
            alert("Unable to assign report to this team.");
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # SAVE TEAM ASSIGNMENT TO DATABASE
    # -----------------------------------------------------

    report.assigned_team_id = team_id


    # -----------------------------------------------------
    # MOVE REPORT TO IN PROGRESS
    # -----------------------------------------------------

    if report.status != "In Progress":

        current_time = datetime.utcnow()

        report.status = "In Progress"

        report.updated_at = current_time


        history_entry = StatusHistory(

            report_id=report.id,

            status="In Progress",

            updated_at=current_time
        )


        db.session.add(
            history_entry
        )


    # -----------------------------------------------------
    # SAVE EVERYTHING
    # -----------------------------------------------------

    db.session.commit()


    # -----------------------------------------------------
    # SHOW SUCCESS
    # -----------------------------------------------------

    return redirect(
        url_for(
            "authority_report_details",
            report_id=report.id
        )
    )


# =========================================================
# RELEASE REPORT FROM RESCUE TEAM
# =========================================================

@app.route(
    "/authority/release/<int:team_id>",
    methods=["POST"]
)
def release_report_from_team(
    team_id
):

    if not session.get(
        "authority_logged_in"
    ):

        return redirect(
            url_for(
                "authority_login"
            )
        )


    # -----------------------------------------------------
    # FIND TEAM
    # -----------------------------------------------------

    team = rescue_team_manager.get_team(
        team_id
    )


    if team is None:

        return """
        <script>
            alert("Rescue team not found.");
            window.history.back();
        </script>
        """


    # -----------------------------------------------------
    # FIND AN ACTIVE REPORT ASSIGNED TO THIS TEAM
    # -----------------------------------------------------

    assigned_report = Report.query.filter(
        Report.assigned_team_id == team_id,
        Report.status != "Resolved"
    ).order_by(
        Report.id.asc()
    ).first()


    # -----------------------------------------------------
    # RELEASE TEAM ASSIGNMENT
    # -----------------------------------------------------

    if assigned_report:

        assigned_report.assigned_team_id = None

        assigned_report.updated_at = (
            datetime.utcnow()
        )


    released = (
        rescue_team_manager.release_report_from_team(
            team_id
        )
    )


    if not released:

        return """
        <script>
            alert("Unable to release the rescue team assignment.");
            window.history.back();
        </script>
        """


    db.session.commit()


    return redirect(
        url_for(
            "authority_dashboard"
        )
    )


# =========================================================
# UPDATE REPORT STATUS
# =========================================================

@app.route(
    "/update-status/<int:report_id>",
    methods=["POST"]
)
def update_status(
    report_id
):

    if not session.get(
        "authority_logged_in"
    ):

        return redirect(
            url_for(
                "authority_login"
            )
        )


    report = Report.query.get_or_404(
        report_id
    )


    new_status = request.form.get(
        "status"
    )


    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]


    if new_status not in allowed_statuses:

        return """
        <script>
            alert("Invalid status.");
            window.history.back();
        </script>
        """


    old_status = report.status


    if old_status != new_status:

        current_time = datetime.utcnow()

        report.status = new_status

        report.updated_at = current_time


        history_entry = StatusHistory(

            report_id=report.id,

            status=new_status,

            updated_at=current_time
        )


        db.session.add(
            history_entry
        )

        db.session.commit()


    return redirect(
        url_for(
            "authority_report_details",
            report_id=report.id
        )
    )


# =========================================================
# AUTHORITY LOGOUT
# =========================================================

@app.route(
    "/authority/logout"
)
def authority_logout():

    session.pop(
        "authority_logged_in",
        None
    )


    return redirect(
        url_for(
            "authority_login"
        )
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5050
    )