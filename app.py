from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_mail import Mail
import config

# Register blueprints
from routes.admin_auth import admin_auth_bp
from routes.admin_routes import admin_bp
from routes.appointment_routes import appointment_bp
from routes.patient_routes import patient_bp

mail = Mail()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    mail.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(patient_bp) 

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/services")
    def services():
        return render_template("services.html")
    
    @app.route("/test")
    def test_route():
        return "API OK"

    return app

from jobs.scheduler_jobs import send_daily_reminders, cancel_expired_appointments

scheduler.add_job(
    id="daily_reminder_job",
    func=send_daily_reminders,
    trigger="cron",
    hour=8, minute=0
)

scheduler.add_job(
    id="auto_cancel_expired",
    func=cancel_expired_appointments,
    trigger="cron",
    hour=0, minute=5
)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
