from flask_wtf import Form 
from wtforms import TextField, TextAreaField, SubmitField, RadioField, StringField, SelectField, BooleanField, DecimalField
from wtforms.validators import InputRequired, Email

class ContactForm(Form):
      name = StringField("Name", validators=[InputRequired('Please enter your name.')])
      email = StringField("Email", validators=[Email('Please enter a valid email address.')])
      position = RadioField("Current position", choices=[('student','student'),('post-doc','post-doc'),('assistant professor','assistant professor'),('associate professor','associate professor'),('professor','professor'),('research faculty','research faculty'),('technical staff','technical staff'),('other','other')], validators=[InputRequired('Please provide your current position.')])
      years = DecimalField("Years in current position", validators=[InputRequired('Please enter years in current position.')])
      submit = SubmitField("Begin survey")    
  
class Likert(Form):
      likert = RadioField("How easy or difficult was this task?", choices=[('very easy','very easy'),('easy','easy'),('neutral','neutral'),('difficult','difficult'),('very difficult','very difficult')], validators=[InputRequired('This question is required.')])
      submit = SubmitField("Next")
      
class agreeLikert(Form):
    def getQuestions():
        questions=['The website design is visually appealing.','Site navigation was logically organized','Site pages load quickly']
        return questions
        
    questions = getQuestions()
    
    for idx, val in enumerate(questions):
        locals()['likert'+str(idx)] = RadioField(str(idx+1)+'.) '+val, choices=[('strongly agree','strongly agree'),('agree','agree'),('neutral','neutral'),('disagree','disagree'),('strongly agree','strongly disagree')], validators=[InputRequired('This question is required.')])
    comments = TextAreaField("Additional comments")
    submit = SubmitField("Finish")

def getTask(task_num):
    tasks=['Find the full list of UNAVCO member institutions.','Find a list of people with expertise in metadata standards.','Find a grant associated with POLENET. How many total POLENET grants are in the system?']
    methods=["Either click 'View all' link on home page or go to UNAVCO page by clicking link beneath photo or clicking Organizations > Consortium > UNAVCO","Search for metadata standards or click on Research > Concepts > Metadata Standards","Search for PoleNet, optionally limit search to 'Research' and 'Grants' to get number"]
    task_num-=1
    return (tasks[task_num],methods[task_num],len(tasks))
    
class Administrator(Form):
    name=RadioField('Select the test administrator', choices=[('Benjamin','Benjamin'),('Beth Bartel','Beth Bartel'),('Aisha','Aisha'),('Beth Pratt-Sitaula','Beth Pratt-Sitaula'),('Shelley','Shelley'),('Other','Other')])
    submit = SubmitField("Next")

class adminTaskForm(Form):
    method = TextAreaField("Actual method")
    completed = BooleanField("Task completed sucessfully")
    comments = TextAreaField("Problems experienced, comments, recommendations")
    submit = SubmitField("Next")
    
