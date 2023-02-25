from flask import Flask, redirect, request, session
from replit import db
import os, datetime,random
#db.clear()
#session.clear()
#lista_posts = db.prefix("post")
#for i in lista_posts:
#  del db[i]
user = os.environ['user']
app = Flask(__name__)
app.secret_key = os.environ["sessionKey"]
app.config['UPLOAD_FOLDER'] = './static/blog/images'

def showComment(post):
  with open("comment.html","r") as file:
    entry = file.read()
  #db[post][comentarios] = {}
  comentarios = db[post]['comentarios']
  content = ""
  num = len(comentarios)
  count=1
  while count <= num:
    for coment in comentarios:
      thisComment = entry
      thisComment = thisComment.replace("{nombre}", db[post]["comentarios"][str(count)]["nombre"])
      thisComment = thisComment.replace("{comentario}", db[post]["comentarios"][str(count)]["comment"])
      count+=1
      content += thisComment
  return content
def getPosts():
  with open("entry.html","r") as file:
    entry = file.read()
  
  keys = db.keys()
  keys = list(keys)
  keys = sorted(keys)
  #print(keys)
  content = ""
  for key in reversed(keys):
     thisEntry = entry
     if key != 'quiquemonroy':
        thisEntry = thisEntry.replace("{title}", db[key]["titulo"])
        thisEntry = thisEntry.replace("{date}", db[key]["date"])
        thisEntry = thisEntry.replace("{img}", db[key]["imgPath"])
        thisEntry = thisEntry.replace("{body}", db[key]["post"])
        thisEntry = thisEntry.replace("{num}", str(db[key]["orden"]))
        thisEntry = thisEntry.replace("{comentarios}", str(len(db[key]["comentarios"])))
        content += thisEntry
  return content
def footer():
  with open("footer.html", "r") as file:
    page = file.read()
  return page
@app.route('/')
def landing():
    with open("landing.html", "r") as f:
      page = f.read()
    page = page.replace("{content}", getPosts())
    page = page.replace("{footer}", footer())
    return page


@app.route('/<pageNumber>', methods=["GET","POST"])
def index(pageNumber):
    global num, lista_posts
    #print(f"{pageNumber}---PageNumber")
    if int(pageNumber) < 1:
      return redirect("/1")
    lista_posts = db.prefix("post")
    entry = f"post{pageNumber}"
    titulo = db[entry]["titulo"]
    fecha = db[entry]["date"]
    post = db[entry]["post"]
    img = db[entry]["imgPath"]
    num_com = int(pageNumber)
      
    prev = str(int(pageNumber) - 1)

    prev = str(int(pageNumber) - 1)
    if int(pageNumber) < len(lista_posts):
        next = str(int(pageNumber) + 1)
    elif int(pageNumber) == len(lista_posts):
        next = pageNumber
    
    with open("home.html", "r") as file:
        page = file.read()
    page = page.replace("{titulo}", titulo)
    page = page.replace("{fecha}", fecha)
    page = page.replace("{post}", post)
    page = page.replace("{img}", img)
    page = page.replace("{prev}", prev)
    page = page.replace("{next}", next)
    page = page.replace("{num}", str(num_com))
    page = page.replace("{comentarios}", showComment(entry))
    page = page.replace("{footer}", footer())
    if request.form: 
      data = request.form
      fecha = datetime.datetime.now()
      numeroDeComent = len(db[entry]["comentarios"])
      
      db[entry]["comentarios"][f"{numeroDeComent+1}"]=data
      
      print(f"Comentario añadido: db:{ db[entry]}")
      #print(f"{db[entry]['comentarios'][fecha]}")
      return redirect(f"/{pageNumber}")

  
    return page


@app.route('/newpost')
def newPost():
  try:
    if session["myName"] == "quiquemonroy":
      pass
  except:
      return redirect("/login")
  with open("newpost.html", "r") as file:
        page = file.read()
  page = page.replace("{footer}", footer())
  return page
@app.route('/addpost', methods=["POST"])
def addpost():
    try:
      if session["myName"] == "quiquemonroy":
        pass
    except:
      return redirect("/login")
    data = request.form
    img = request.files["img"]
    lista_posts = db.prefix("post")
    filename = f"img{len(lista_posts)+1}.png"
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    img = filename
    date = datetime.datetime.now()
    #db[date]["time"] = date.day
    date = f"{date.day}.{date.month}.{date.year} - {date.hour}:{date.minute}"
    post = f"post{len(lista_posts)+1}"
    db[post] = data
    #db[date]["time"] = date.day
    db[post]["date"] = date
    db[post]["imgPath"] = filename
    db[post]["orden"] = len(lista_posts) + 1
    db[post]["comentarios"] = {}

    with open("publicado.html", "r") as file:
        page = file.read()

    titulo = db[post]["titulo"]
    fecha = db[post]["date"]
    post = db[post]["post"]
    #imagen = db[post]["imgPath"]

    page = page.replace("{titulo}", titulo)
    page = page.replace("{fecha}", fecha)
    page = page.replace("{post}", post)
    page = page.replace("{img}", img)
    page = page.replace("{footer}", footer())
    return page


@app.route('/borrar')
def borrar():
    try:
      if session["myName"] == "quiquemonroy":
        pass
    except:
      return redirect("/login")
    lista_posts = db.prefix("post")
    post = f"post{len(lista_posts)}"
    del db[post]
    return redirect("/menu")


@app.route('/menu')#,methods=["GET"])
def menu():
    global lista_posts
    try:
      if session["myName"] == user:
        pass
    except:
      return redirect("/login")
    

    with open("menu.html", "r") as file:
        page = file.read()
    page = page.replace("{content}", getPosts())
    page = page.replace("{footer}", footer())
    return page



@app.route("/login", methods=["GET","POST"]) 
def login():
  try:
    if session["myName"] == user:
      return redirect("/menu")
  except:
      with open("login.html", "r") as file:
        page = file.read()
      page = page.replace("{footer}", footer())
      return page

@app.route("/signup", methods=["GET"]) 
def signup():
  with open("signup.html","r") as file:
    page = file.read()
  page = page.replace("{footer}", footer())
  return page

@app.route("/succes", methods=["POST"]) 
def signUpSucces():
  data = request.form
  username = data["username"]
  db[username] = data
  password = db[username]['password']
  passwordCheck= db[username]['password_check']
  salt = random.randint(10000,99999)
  passwordSalted = hash(f"{password}{salt}")
  if password == passwordCheck:
    username = data["username"]
    db[username] = data
    db[username]["password"] = passwordSalted
    db[username]["salt"] = salt
    with open("success.html", "r") as file:
      page=file.read()
    page = page.replace("{footer}", footer())
    return page
  else:
    with open("dontmatch.html", "r") as file:
        page=file.read()
    page = page.replace("{footer}", footer())
    return page
  

    
    #page=f"""passwords dont mach
    
    #{password} --- {passwordCheck}"""
    #return page
    
    
  
      
      
      






@app.route("/logged", methods=["POST","GET"]) 
def logged():
  try:
    if session["myName"] == user:

      return redirect("/menu")
  except: 
    pass
  try:
    data = request.form
    session["myName"] = request.form["username"]
    username = data["username"]
    password = hash(f"{data['password']}{db[username]['salt']}")
    passwordCheck= db[username]['password']
    if password == passwordCheck:
      return redirect("/menu")
    else:
      with open("nope.html", "r") as file:
        page = file.read()
      page = page.replace("{footer}", footer())
      return page
  except:
    with open("nope.html", "r") as file:
        page = file.read()
    page = page.replace("{footer}", footer())
    return page
  

    

    
  
      
      
      








@app.route("/change", methods=["GET"]) 
def change():
  with open("change.html", "r") as file:
    page = file.read()
  page = page.replace("{footer}", footer())
  return page
@app.route("/changePass", methods=["POST"]) 
def changePass():
  data = request.form
  username = data["username"]
  #db[username] = data
  n_password = data['newPassword']
  n_passwordCheck= data['newPassword_check']
  if n_password == n_passwordCheck:
    if username in db and data["email"] == db[username]["email"]:
      db[username]["password"] = hash(f"{n_password}{db[username]['salt']}")
      with open("success.html", "r") as file:
        page=file.read()
      page = page.replace("{footer}", footer())
      return page
  else:
    with open("dontmatch.html", "r") as file:
        page=file.read()
    return page
  
@app.route("/logout",methods=["GET"]) 
def logout():
    session.clear()
    return redirect("/")
@app.route("/borrarpost1",methods=["GET"]) 
def borrarPost():
    try:
        if session["myName"] == "quiquemonroy":
          pass
    except:
        return redirect("/login")
    lista_posts = db.prefix("post")
    lista_posts= sorted(lista_posts)
    
    if len(lista_posts) > 0:  
      post = lista_posts[0]
      del db[post]
      return redirect("/menu")
    else:
      return redirect("/menu")
@app.route("/borrarpost2",methods=["GET"]) 
def borrarPost2():
    try:
      if session["myName"] == "quiquemonroy":
        pass
    except:
        return redirect("/login")
    lista_posts = db.prefix("post")
    lista_posts= sorted(lista_posts)
    if len(lista_posts) > 1:  
      post = lista_posts[1]
      del db[post]
      return redirect("/menu")
    else:
      return redirect("/menu")
@app.route("/borrarpost3",methods=["GET"]) 
def borrarPost3():
    try:
      if session["myName"] == "quiquemonroy":
        pass
    except:
        return redirect("/login")
    lista_posts = db.prefix("post")
    lista_posts= sorted(lista_posts)
    if len(lista_posts) > 2:  
      post = lista_posts[2]
      del db[post]
      return redirect("/menu")
    else:
      return redirect("/menu")

app.run(host='0.0.0.0', port=81)

  