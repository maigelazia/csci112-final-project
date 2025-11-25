from flask import Flask, render_template
from flask_mail import Mail
import config

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    mail.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/test")
    def test_route():
        return "API OK"

    # register blueprints
    from routes.appointment_routes import appointment_bp
    from routes.patient_routes import patient_bp
    from routes.admin_routes import admin_bp
    from routes.admin_auth import admin_auth_bp

    app.register_blueprint(appointment_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_auth_bp)

    @app.route("/test")
    def test_route():
        return "API OK"
    
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)