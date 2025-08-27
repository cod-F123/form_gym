from flask import Flask , render_template , request , redirect , url_for , session , flash
from markupsafe import escape
from datetime import datetime

# data base
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column , Integer , String ,Text , Boolean , ForeignKey , DateTime ,Time
import random

# form
from flask_wtf import FlaskForm
from wtforms import StringField , IntegerField , TextAreaField , TimeField 
from wtforms.validators import Length , InputRequired , NumberRange , Email , Optional

from flask_admin import Admin , AdminIndexView , expose
from flask_admin.contrib.sqla import ModelView

from werkzeug.security import generate_password_hash , check_password_hash
from wtforms.fields import PasswordField


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///sqlite.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config["SECRET_KEY"] = "b816e0180c60243e0d0fee49f43acc2ad2435bb2c6a985a1ffd7db9ab3127478"
db = SQLAlchemy(app=app)


class User(db.Model):
    id = Column(Integer(), primary_key=True)
    
    username = Column(String(50),unique=True,nullable=False)
    _password = Column("password",String(255),nullable=False)
    email = Column(String(100),nullable=True)
    is_admin = Column(Boolean(),default=False)
    
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self,text_plaint_password):
        self._password = generate_password_hash(text_plaint_password)
    
    
    def check_password(self,password):
        return check_password_hash(self._password,password)
    

class ProgramRequest(db.Model):
    id = Column(Integer(),primary_key=True)
    full_name = Column(String(100))
    phone = Column(String(11))
    email = Column(String(100))
    age = Column(Integer())
    height = Column(Integer())
    weight = Column(Integer())
    goal = Column(String(50))
    
    medical_conditions = Column(Text(),nullable=True)
    medication_use = Column(String(50))
    food_allergies = Column(Text(),nullable=True)
    
    gym_start = Column(Time(),nullable=True)
    gym_end = Column(Time(),nullable=True)
    activity_level =  Column(String(50))
    job_title = Column(String(200),nullable=True)
    job_activity = Column(String(50),nullable=True)
    
    sleep_time = Column(Time())
    wake_time = Column(Time())
    breakfast_time = Column(Time())
    lunch_time = Column(Time())
    dinner_time = Column(Time())
    snack_morning_time = Column(Time(),nullable=True)
    snack_evening_time = Column(Time(),nullable=True)
    
    previous_diet = Column(String(50))
    supplement_used = Column(String(50))
    willing_supplement = Column(String(50))
    
    breakfast_items = Column(Text())
    lunch_items = Column(Text())
    dinner_items = Column(Text())
    snack_items = Column(Text(), nullable=True)
    
    is_payed = Column(Boolean(False))
    authority = Column(String(255),nullable=True,unique=True)
    date_payed = Column(DateTime(timezone=True),nullable=True)
    
    slug = Column(String(50),unique=True)

    def __init__(self,**kwrags):
        super().__init__(**kwrags)
    

with app.app_context():
    db.create_all()
    


# form 
class ProgramRequestForm(FlaskForm):
    # اطلاعات شخصی
    full_name = StringField("نام و نام خانوادگی", 
                            validators=[Length(min=2, max=100, message="نام و نام خانوادگی درست نیست")])
    phone = StringField("شماره همراه", 
                     validators=[Length(min=11, max=11, message="شماره را به درستی وارد کنید")])
    email = StringField("ایمیل شخصی", validators=[Email(message="ایمیل معتبر نیست")])

    # مشخصات بدنی و هدف
    age = IntegerField("سن", 
                       validators=[NumberRange(min=10, max=85, message="سن باید بین 10 تا 85 باشد")])
    height = IntegerField("قد (سانتی‌متر)", 
                          validators=[NumberRange(min=100, max=230, message="قد باید بین 100 تا 230 سانتی متر باشد")])
    weight = IntegerField("وزن (کیلوگرم)", 
                          validators=[NumberRange(min=35, max=220, message="وزن باید بین 35 تا 220 کیلوگرم باشد")])
    goal = StringField("هدف از رژیم غذایی", validators=[Length(max=200)])

    # وضعیت پزشکی
    medical_conditions = TextAreaField("بیماری خاص (کم‌کاری یا پرکاری تیروئید، دیابت، چربی خون و ...)", validators=[Optional()])
    medication_use = StringField("استفاده از دارو", validators=[Optional()])
    food_allergies = TextAreaField("حساسیت غذایی", validators=[Optional()])

    # فعالیت ورزشی و شغلی
    gym_start = TimeField("ساعت شروع تمرین", validators=[Optional()])
    gym_end = TimeField("ساعت پایان تمرین", validators=[Optional()])
    activity_level = StringField("میزان فعالیت ورزشی")
    job_title = StringField("شغل و میزان فعالیت کاری", validators=[Optional()])
    job_activity = StringField("شغل و میزان فعالیت کاری", validators=[Optional()])
    # سبک زندگی
    sleep_time = TimeField("ساعت خواب")
    wake_time = TimeField(None)
    breakfast_time = TimeField("ساعت مصرف صبحانه")
    lunch_time = TimeField("ساعت مصرف ناهار")
    dinner_time = TimeField("ساعت مصرف شام")
    snack_morning_time = TimeField(None, validators=[Optional()])
    snack_evening_time = TimeField(None, validators=[Optional()])

    # سوابق رژیم و مکمل
    previous_diet = StringField("تا حالا رژیم گرفته‌اید؟")
    supplement_used = StringField("مکمل مصرف کرده‌اید؟")
    willing_supplement = StringField("تمایل به مصرف مکمل دارید؟")

    # جزئیات رژیم غذایی
    breakfast_items = TextAreaField("معمولاً چه چیزهایی برای صبحانه میل می‌کنید و چقدر")
    lunch_items = TextAreaField("معمولاً چه چیزهایی برای ناهار میل می‌کنید و چقدر")
    dinner_items = TextAreaField("معمولاً چه چیزهایی برای شام میل می‌کنید و چقدر")
    snack_items = TextAreaField("از چه چیزهایی برای میان‌وعده‌ها استفاده می‌کنید و چقدر")

class UserAdmin(ModelView):
    column_list = ('id', 'username', 'email','is_admin')
    
    form_columns = ('username', 'email', 'password','is_admin')
    
    column_searchable_list = ['username']
    
    form_extra_fields = {
        "password" : PasswordField("Password") 
    }



class ProgramRequestAdmin(ModelView):
    def on_model_change(self, form, model, is_created):
        if not model.slug :
            model.slug =  f"program{random.randint(1000000,9999999)}"
        
        if model.is_payed and not model.date_payed:
            model.date_payed = datetime.now()
        
    
        super().on_model_change(form, model, is_created)
    
    column_filters = ["is_payed"]
    
    column_searchable_list = ["full_name"]
    
    column_list = ('id', 'full_name', 'phone', 'email', 'age', 'height', 'weight', 'goal', 'is_payed','date_payed','slug')


class MyAdminIndexView(AdminIndexView):
    
    @expose("/")
    def index(self):
        
        if "user_id" in session:
            user = User.query.get(session.get("user_id"))
            
            if user and user.is_admin:
                return super(MyAdminIndexView, self).index()
        
        flash("اجازه دسترسی به پنل مدیریت ندارید!", "danger")
        return redirect(url_for('login_admin'))
    
    def is_accessible(self):
        if "user_id" in session:
            user = User.query.get(session.get("user_id"))
            
            return user and user.is_admin
        
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        flash("ابتدا باید به عنوان سوپر یوزر وارد شوید", "danger")
        return redirect(url_for('login_admin'))


admin = Admin(app,name="Gym form",template_mode="bootstrap4", index_view=MyAdminIndexView())

admin.add_view(UserAdmin(User,db.session,"کاربر"))
admin.add_view(ProgramRequestAdmin(ProgramRequest,db.session,"درخواست برنامه"))


@app.route("/",methods=["GET","POST"])
def index():
    form = ProgramRequestForm()
    if request.method == 'POST':
        form = ProgramRequestForm(request.form)
        
        if form.validate():
            
            slug = f"program{random.randint(1000000,9999999)}"
            
            new_program = ProgramRequest(
                full_name=form.full_name.data,
                phone=form.phone.data,
                email=form.email.data,
                age=form.age.data,
                height=form.height.data,
                weight=form.weight.data,
                goal=form.goal.data,
                medical_conditions=form.medical_conditions.data,
                medication_use=form.medication_use.data,
                food_allergies=form.food_allergies.data,
                
                gym_start=form.gym_start.data,
                gym_end=form.gym_end.data,
                activity_level=form.activity_level.data,
                job_title=form.job_title.data,
                job_activity=form.job_activity.data,
                sleep_time=form.sleep_time.data,
                wake_time=form.wake_time.data,
                breakfast_time=form.breakfast_time.data,
                lunch_time=form.lunch_time.data,
                dinner_time=form.dinner_time.data,
                snack_morning_time=form.snack_morning_time.data,
                snack_evening_time=form.snack_evening_time.data,
                previous_diet=form.previous_diet.data,
                supplement_used=form.supplement_used.data,
                willing_supplement=form.willing_supplement.data,
                breakfast_items=form.breakfast_items.data,
                lunch_items=form.lunch_items.data,
                dinner_items=form.dinner_items.data,
                snack_items=form.snack_items.data,
                
                slug=slug
            )
            
            db.session.add(new_program)
            
            db.session.commit()
            
            return render_template("result.html",data = new_program)
        
        for err in form.errors.values():
            flash(err,category="danger")
         
    return render_template("index.html",name = "mohammad",form = form)



@app.route("/login-admin",methods=["POST","GET"])
def login_admin():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username = username).first()
        
        if user and user.check_password(password):
            
            session["user_id"] = user.id
            
            flash("با موفقیت وارد شدید", category="success")
            return redirect(url_for("admin.index"))
        else:
            
            flash("نام کاربری یا رمز عبور نادرست است", category="danger")
    
    return render_template("primary_login.html")

if __name__ == '__main__':
    app.run(debug = True)