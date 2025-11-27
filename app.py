from flask import Flask, render_template, request
from flask_mail import Mail
from flask_pymongo import PyMongo #added
import config

mail = Mail()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)


    mail.init_app(app) #added
    mongo.init_app(app) #added

    @app.route("/")
    def home_page():
        return render_template("index.html")

    @app.route("/patientform")
    def patient_page():
        return render_template("patient_form.html")
    


    # Register blueprints
    from routes.appointment_routes import appointment_bp
    from routes.patient_routes import patient_bp
    from routes.admin_routes import admin_bp
    from routes.admin_auth import admin_auth_bp

    app.register_blueprint(appointment_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_auth_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
