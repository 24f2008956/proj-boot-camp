from flask import Flask, render_template, request, redirect, url_for
from website.models import db, User
from website.config import DevelopmentConfig
from flask_login import LoginManager


#creating admin
def create_admin_user():
    #admin credentials
    admin_email = "admin@email.com"
    admin_password = 'admin123'
    
    if not User.query.filter_by(email = admin_email).first():
        admin = User(username = 'admin', email = admin_email, role = 'admin')
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")
        
        
          
        
        
#application function        
def create_app():
    app = Flask(__name__) # flask initialization
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_admin_user()
        import website.views
        import website.auth
        
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    #load user through Flask-Login
    @login_manager.user_loader
    def load_user(id):
        #from website.models import User
        return User.query.get(int(id))    
    
    return app    
    
my_app = create_app()

if __name__ == "__main__":
    my_app.run(debug = True)