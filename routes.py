from flask import Flask, render_template, request, flash, redirect, url_for
#from forms import ContactForm, Likert, getTask, agreeLikert, adminTaskForm
from forms import *
from flask.ext.wtf import Form
from wtforms.validators import InputRequired
from datetime import datetime
import json
import gspread
import sys
import os
 
app = Flask(__name__) 
app.config.from_pyfile('config.cfg', silent=True)

#set up client key and open the spreadsheet
from oauth2client.client import GoogleCredentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "static/google.json"

json_key = json.load(open('static/google.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = GoogleCredentials.get_application_default()
credentials = credentials.create_scoped(['https://spreadsheets.google.com/feeds'])
 
#Subject-facing questions, one per page
@app.route('/<task_num>', methods=['GET', 'POST'])
def task(task_num):
  subtitle = "Task #"+task_num
  gid=request.args.get('gid') #Spreadsheet row we're working in
  if not gid:
      time = str(datetime.now())
      gc = gspread.authorize(credentials)
      wks = gc.open("Usability Testing").sheet1
      wks.append_row([time])
      gid=wks.row_count
      flash('No user ID detected. Results will be added to a new row.')
      
  form = Likert()
  task_num=int(task_num)
  (task,method,total_tasks) = getTask(task_num)

  if request.method == 'POST':
    if form.validate_on_submit() and task_num<total_tasks:
      task_num+=1
      gc = gspread.authorize(credentials)
      wks = gc.open("Usability Testing").sheet1
      ease = form.likert.data
      wks.update_cell(gid,task_num+3, ease)
      return redirect(url_for('task', task_num=task_num, gid=gid)) 
         
    elif form.validate_on_submit():
      task_num+=1
      gc = gspread.authorize(credentials)
      wks = gc.open("Usability Testing").sheet1
      ease = form.likert.data
      wks.update_cell(gid,task_num+3, ease)
      return redirect(url_for('exitSurvey', gid=gid))
      
    else:
      return render_template('task.html', form=form, task_num=task_num, task=task, gid=gid, subtitle=subtitle) 
    
  elif request.method == 'GET':
    (task,method,total_tasks) = getTask(task_num)
    return render_template('task.html', form=form, task=task, task_num=task_num, gid=gid, subtitle=subtitle)
    
#Exit survey, all questions on one page    
@app.route('/survey', methods=['GET', 'POST'])
def exitSurvey():
  subtitle = "Exit Survey"
  gid=request.args.get('gid')
  if not gid:
      time = str(datetime.now())
      gc = gspread.authorize(credentials)
      wks = gc.open("Usability Testing").sheet1
      wks.append_row([time])
      gid=wks.row_count
      flash('No user ID detected. Results will be added to a new row.')
          
  form = agreeLikert()

  if request.method == 'POST':
    if form.validate_on_submit():
      gc = gspread.authorize(credentials)
      wks = gc.open("Usability Testing").sheet1
    
      for idx,field in enumerate(form):
          if field.name !='submit' and field.type != 'HiddenField' and field.type !='CSRFTokenField':
            wks.update_cell(gid,idx+7, field.data)
      
      return redirect(url_for('thankyou'))
      
    else:
      return render_template('survey.html', form=form, gid=gid, subtitle=subtitle) 
    
  elif request.method == 'GET':
    return render_template('survey.html', form=form, gid=gid, subtitle=subtitle)

@app.route('/thankyou')
def thankyou():
    subtitle="Thank You"
    return render_template('thankyou.html', subtitle=subtitle)

#Home page, collect contact information
@app.route('/', methods=['GET', 'POST'])
def home():
    form = ContactForm()
 
    if request.method == 'POST':
 
        if form.validate_on_submit():
            time = str(datetime.now())
            gc = gspread.authorize(credentials)
            wks = gc.open("Usability Testing").sheet1
            name = form.name.data
            email = form.email.data
            position = form.position.data
            wks.append_row([time,name,email,position])
            gid=wks.row_count
            return redirect(url_for('task', task_num=1, gid=gid)) 

        else:
            return render_template('home.html', form=form)
    
    elif request.method == 'GET':
        return render_template('home.html', form=form)
        
#Test administrator landing page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = Administrator()
 
    if request.method == 'POST':
 
        if form.validate_on_submit():
            time = str(datetime.now())
            gc = gspread.authorize(credentials)
            works = gc.open("Usability Testing")
            wks = works.worksheet('Sheet2')
            name = form.name.data
            wks.append_row([time,name])
            gid=wks.row_count
            return redirect(url_for('adminIntro', name=name, gid=gid)) 

        else:
            return render_template('admin.html', form=form)
    
    elif request.method == 'GET':
        return render_template('admin.html', form=form)   

#Test administrator script
@app.route('/admin/intro')
def adminIntro():
    subtitle="Intro"
    gid=request.args.get('gid')
    if not gid:
      dtime = str(datetime.now())
      gc = gspread.authorize(credentials)
      works = gc.open("Usability Testing")
      wks = works.worksheet('Sheet2')
      wks.append_row([dtime])
      gid=wks.row_count
      flash('No user ID detected. Results will be added to a new row.')
    name=request.args.get('name')
    return render_template('admin_intro.html', gid=gid, name=name, subtitle=subtitle)     
        
#Test administrator task observations, one task per page
@app.route('/admin/<task_num>', methods=['GET', 'POST'])
def adminTask(task_num):
  subtitle = "Task #"+task_num
  gid=request.args.get('gid')
  time=request.args.get('time')
  if not gid:
      dtime = str(datetime.now())
      gc = gspread.authorize(credentials)
      works = gc.open("Usability Testing")
      wks = works.worksheet('Sheet2')
      wks.append_row([dtime])
      gid=wks.row_count
      flash('No user ID detected. Results will be added to a new row.')
          
  form = adminTaskForm()
  task_num=int(task_num)
  (task,method,total_tasks) = getTask(task_num)

  if request.method == 'POST':
    if form.validate_on_submit() and task_num<total_tasks:
      task_num+=1
      gc = gspread.authorize(credentials)
      works = gc.open("Usability Testing")
      wks = works.worksheet('Sheet2')
      completed = form.completed.data
      comments = form.comments.data
      method = form.method.data
      if method:
          wks.update_cell(gid,3+(task_num-2)*4, method)
      if comments:
          wks.update_cell(gid,4+(task_num-2)*4, comments)
      if completed:
          wks.update_cell(gid,5+(task_num-2)*4, completed)
      if time !="00":
          wks.update_cell(gid,6+(task_num-2)*4, time)
      return redirect(url_for('adminTask', task_num=task_num, gid=gid)) 
         
    elif form.validate_on_submit():
      task_num+=1
      gc = gspread.authorize(credentials)
      works = gc.open("Usability Testing")
      wks = works.worksheet('Sheet2')
      completed = form.completed.data
      comments = form.comments.data
      method = form.method.data
      if method:
          wks.update_cell(gid,3+(task_num-2)*4, method)
      if comments:
          wks.update_cell(gid,4+(task_num-2)*4, comments)
      if completed:
          wks.update_cell(gid,5+(task_num-2)*4, completed)
      if time !="00":
          wks.update_cell(gid,6+(task_num-2)*4, time)
      return redirect(url_for('adminThankYou', gid=gid))
      
    else:
      return render_template('admin_task.html', form=form, task_num=task_num, task=task, gid=gid, method=method, subtitle=subtitle) 
    
  elif request.method == 'GET':
    (task,method,total_tasks) = getTask(task_num)
    return render_template('admin_task.html', form=form, task=task, task_num=task_num, gid=gid, method=method, subtitle=subtitle)

@app.route('/admin_thankyou')
def adminThankYou():
    subtitle = "Thank You"
    return render_template('admin_thankyou.html', subtitle=subtitle)

if __name__ == '__main__':
  app.run()
