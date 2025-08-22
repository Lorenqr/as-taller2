from flask import Flask
from extensions import db
from controllers.task_controller import task_bp


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

app.secret_key = 'tu_clave_secreta_aqui'

app.register_blueprint(task_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

