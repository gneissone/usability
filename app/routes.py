from flask import Flask, render_template, request, flash, redirect, url_for, g
#from forms import ContactForm, Likert, getTask, agreeLikert, adminTaskForm
from forms import *
from flask.ext.wtf import Form
from wtforms.validators import InputRequired
from datetime import datetime
import json
import gspread
import sys
import os
import sqlite3
from app import app
from contextlib import closing


#set up client key and open the spreadsheet
from oauth2client.client import GoogleCredentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "app/static/google.json"

json_key = json.load(open('app/static/google.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = GoogleCredentials.get_application_default()
credentials = credentials.create_scoped(['https://spreadsheets.google.com/feeds'])

#Test if we are online and can connect to Google Sheets
def connection_test():
    try:
        gspread.authorize(credentials)
        return True
    except: pass
    return False

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
    
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
def query_db(query, args=(), one=False):
    cur = connect_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
        
@app.before_request
def before_request():
    g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
 
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
@app.route('/', methods=['GET', 'POST'], defaults={'online': True})
def home(online):
    form = ContactForm()
    online = connection_test()
    online=False
    
    if request.method == 'POST':
        if form.validate_on_submit():
            time = str(datetime.now())
            name = form.name.data
            email = form.email.data
            position = form.position.data
            years = form.years.data
            
            if online==False:
                new_row = [(time,name,email,position,str(years),'','','','','','','')]
                g.db.executemany('insert into entries values (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',new_row)
                g.db.commit()

                return('Success?')
                
            else:    
                gc = gspread.authorize(credentials) #TODO Make this an if statement and alternatively post it an internal database
                wks = gc.open("Usability Testing").sheet1
                wks.append_row([time,name,email,position])
                gid=wks.row_count
                return redirect(url_for('task', task_num=1, gid=gid)) 

        else:
            return render_template('home.html', form=form)
    
    elif request.method == 'GET':
        if online==False:
            flash('Cannot connect to database. Running in OFFLINE MODE.')
            return render_template('home.html', form=form)
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

@app.route('/test_db')
def test_db():
    new_row = [('col1','col2','col3','col4','col5','col6','col7','col8','col9','col10', 'col11','col12')]
    g.db.executemany('insert into entries values (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',new_row)
    g.db.commit()

    user = query_db('select * from entries')
    print 'doing something!!!'
    print user
    
    if user is None:
        return('No such user')
    else:
        return(user[0][1])

if __name__ == '__main__':
    init_db()
    app.run()
