from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import cgi
from http.cookies import SimpleCookie
from helpers import Database
import json
import os
import uuid


BASE_DIR = os.getcwd()

ALLOWED_HOST = ['*']

url_patterns = [
    '',
    'login/',
    'signup/',
    'logout/',
]



class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self,*args,**kwargs):
        self.is_authenticated = False
        self.db = Database()
        self.db.connect()
        super().__init__(*args,**kwargs)


    def _urlChecker(method,*args,**kwargs):
        """
        Decorator Used to check wheather the url is correct ,
        according to the url patterns
        """
        def main(self,*args,**kwargs):
            valid_host = False
            valid_path = False
            path = self.path
            for host in ALLOWED_HOST:
                if "*" in ALLOWED_HOST:
                    valid_host = True
                    break
                else:
                    """"
                    Do something Else
                    """
                    pass
            if valid_host == False:
                self.render_html("<html><body><h2>Host Not valid ! </h2></body></html>")
            else:
                return method(self,*args,**kwargs)
        return main

    def _POST(method,*args,**kwargs):
        def main(self,*args,**kwargs):
            if self.path.startswith('/api/'):
                return method(self,*args,**kwargs)
            #do something
            self.POST = {}
            ctype , pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            fields = cgi.parse_multipart(self.rfile,pdict=pdict)
            for key in fields:
                self.POST[key] = fields[key]

            return method(self,*args,**kwargs)
        return main
    

    # @_urlChecker
    def do_GET(self):
        if self.path.endswith('login') or self.path.endswith('login/'):
            if self.is_session_authenticated():
                self.remove_session()
                self.redirect('/')
            else:
                self.render('login.html')   

        elif self.path.endswith('signup') or self.path.endswith('signup/'):
            self.render('signup.html')
        
        elif self.path == "/":
            if self.is_session_authenticated():
                context = self.db.get_all_user_data(self.is_session_authenticated())
                self.render('index.html',context=context)
            else:self.redirect('/login/')

        elif self.path.startswith('/prophile-uploads/') or self.path.startswith('/login/prophile-uploads/'):
            self.render_image(self.path)
        
        elif self.path in ['/update','/update/'] :
            self.render('update.html')
        elif self.path in ['/admin','/admin/'] :
            with open('templates/adminpanel.html','r') as file:
                adminpanel_html = file.read()
            with open('templates/adminpanel_context_html.html','r') as file:
                context_html = file.read() 
            final_context_html = ""
            for user_tuple in self.db.get_all_for_admin():
                    print(user_tuple)
                    user_html = context_html
                    user_html = user_html.replace("""{{ id }}""",str(user_tuple[0]))
                    user_html = user_html.replace("""{{ prophile }}""",str(user_tuple[1]))
                    user_html = user_html.replace("""{{ firstname }}""",user_tuple[2])
                    user_html = user_html.replace("""{{ lastname }}""",user_tuple[3])
                    user_html = user_html.replace("""{{ email }}""",user_tuple[4])
                    user_html = user_html.replace("""{{ state }}""",user_tuple[5])
                    user_html = user_html.replace("""{{ skills }}""",user_tuple[6])
                    user_html = user_html.replace("""{{ degree }}""",user_tuple[7])
                    user_html = user_html.replace("""{{ project }}""",user_tuple[8])
                    user_html = user_html.replace("""{{ position }}""",user_tuple[9])
                    user_html = user_html.replace("""{{ certificate }}""",str(user_tuple[10]))
                    final_context_html += user_html
            adminpanel_html = adminpanel_html.replace("""{% fields %}""",final_context_html)
            self.render_html(adminpanel_html)
        elif self.path.startswith('/admin/update/'):
            id = self.path.split("/")[3]
            self.render('admin_update.html',context=self.db.get_all_user_data(id=str(id)))
        else:
            self.render_html('<html><body><h1>Please enter valid url</h1></body></html>')


    @_POST
    @_urlChecker    
    def do_POST(self):
        if self.path.endswith('login') or self.path.endswith('login/'):
            email = self.POST.get('email')[0]
            password = self.POST.get('password')[0]
            if self.db.authenticate(email=email,password=password):    
                sessionid = str(uuid.uuid4())
                cookies = {
                    'sessionid' : sessionid
                }
                self.add_session(email=email,sessionid=sessionid)
                self.redirect('/',cookies=cookies)
            else:
                self.render('login.html',alert=f'User Not Authenticated')
        
        elif self.path.endswith('signup') or self.path.endswith('signup/'):
            email = self.POST.get('email')[0]

            #  table = user_data
            firstname = self.POST.get('firstname')[0]
            lastname = self.POST.get('lastname')[0]
            password = self.POST.get('password')[0]
            prophile = self.POST.get('prophile')[0]
            filename = email + ".jpg" 
            prophile_path = "prophile-uploads/" + filename
            with open(prophile_path,'wb') as file:
                file.write(prophile)
            self.db.insert_user_data(firstname=firstname,lastname=lastname,email=email,password=password,prophile = prophile_path)

            #  table = user_addresses
            street = self.POST.get('street')[0]
            city = self.POST.get('city')[0]
            state = self.POST.get('state')[0]
            zipcode = int(self.POST.get('zipcode')[0])
            self.db.insert_into(table = 'user_addresses',
                                street = street,
                                city = city,
                                state = state,
                                zipcode = zipcode,
                                user_id = email
                            )
            # table = user_skills
            skill_name = self.POST.get('skill-name')[0]
            proficiency = self.POST.get('proficiency')[0]
            self.db.insert_into(
                table='user_skills',
                skill_name = skill_name,
                proficiency = proficiency,
                user_id = email
            )

            # table = user_education
            degree = self.POST.get('degree')[0]
            major = self.POST.get('major')[0]
            university = self.POST.get('university')[0]
            graduation_year = self.POST.get('graduation-year')[0]
            self.db.insert_into(
                table = 'user_education',
                degree = degree,
                major = major,
                university = university,
                graduation_year = graduation_year,
                user_id = email
            )

            # table = user_projects
            name = self.POST.get('project-name')[0]
            description = self.POST.get('project-description')[0]
            technology_used = self.POST.get('technology-used')[0]
            self.db.insert_into(
                table = 'user_projects',
                name = name,
                description = description,
                technology_used = technology_used,
                user_id = email
            )

            # table = user_experience
            name = self.POST.get('experience-name')[0]
            position = self.POST.get('position')[0]
            responsibilities = self.POST.get('responsibilities')[0]
            start_date = self.POST.get('start-date')[0]
            end_date = self.POST.get('end-date')[0]
            self.db.insert_into(
                table = 'user_experience',
                name = name,
                position = position,
                responsibilities = responsibilities,
                start_date = start_date,
                end_date = end_date,
                user_id = email
            )

            # table = user_certifications
            name = self.POST.get('certificate-name')[0]
            issuing_organization = self.POST.get('organization-name')[0]
            date = self.POST.get('issuing-date')[0]
            self.db.insert_into(
                table = 'user_certifications',
                issuing_organization = issuing_organization,
                date = date,
                user_id = email
            )
            
            # self.add_session(email=email)
            self.redirect('/login/')
            # self.render('signup.html')
        elif self.path.startswith('/api/update') or self.path.endswith('/api/update/'):
            if self.is_session_authenticated():
                user_email = self.is_session_authenticated()
            else:self.send_response_only(400);return
            ctype , pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == "multipart/form-data":
                image_bytes = self.rfile.read(int(self.headers.get('Content-Length')))
                image_path = "prophile-uploads/" + user_email
                with open(image_path,'wb') as file:
                    file.write(image_bytes)
                self.db.update_prophile_path(user_email,image_path)
                self.send_json_response({"updated":"successfully","status":"ok"})
            elif ctype == "application/json":
                updated_data = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
                updated_data['user_id'] = user_email
                try:
                    self.db.update_field(updated_data)
                    print(updated_data)
                    self.send_json_response({"updated":"successfully","status":"ok"})
                except Exception as e:
                    self.send_json_response({"status":"notok","Error":e})
            else:
                self.send_response_only(400)
                self.end_headers()
    def do_DELETE(self):
        if self.path in ['/api/delete','/api/delete/']:
            json_data = self.rfile.read(int(self.headers.get('Content-Length'))).decode()
            json_data = json.loads(json_data)
            self.db.delete_user(json_data["id"],database_password="root")
            self.send_json_response({"status":"ok"})
        else:
            self.send_response_only(400)
            self.end_headers()
    def do_UPDATE(self):
        print(self.path)
        if self.path.startswith("/api/admin/update"):pass
        else: self.send_response_only(400);return 
        ctype , pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == "multipart/form-data":
            user_email = self.headers.get('email')
            image_bytes = self.rfile.read(int(self.headers.get('Content-Length')))
            image_path = "prophile-uploads/" + user_email
            with open(image_path,'wb') as file:
                file.write(image_bytes)
            self.db.update_prophile_path(user_email,image_path)
            self.send_json_response({"updated":"successfully","status":"ok"})
        elif ctype == "application/json":
            updated_data = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
            try:
                self.db.update_field(updated_data)
                print(updated_data)
                self.send_json_response({"updated":"successfully","status":"ok"})
            except Exception as e:
                self.send_json_response({"status":"notok","Error":e})
        else:
                self.send_response_only(400)
                self.end_headers()
    def send_json_response(self,response_dict:dict=None):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_dict).encode())
    def render(self,template:str,alert:str=False,status:int=None,context:dict=None,cookies=None):
        with open(f'templates/{template}','r') as template:
            htmlresponse = template.read()
        if context:
            for key in context:
                tag = "{% " + key + " %}"
                htmlresponse = htmlresponse.replace(tag,str(context[key]))
        if alert: htmlresponse += f"<script>alert('{alert}');</script>"
        if status:self.send_response(status)
        else:self.send_response(200)
        self.send_header('Content-type','text/html')
        if cookies:
            cookie_obj = SimpleCookie()
            for cookie_name , cookie_value in cookies.items():
                cookie_obj[cookie_name] = cookie_value
            for morsel in cookie_obj.values():
                morsel['path'] = '/'
                self.send_header("Set-Cookie", morsel.OutputString())
        self.end_headers()
        self.wfile.write(htmlresponse.encode())
    def render_html(self,html_response,status=None):
        if status == None:self.send_response(200)
        else : self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html_response.encode())
    def redirect(self,url:str,cookies:dict=None):
        self.send_response(301)
        if cookies:
            cookie_obj = SimpleCookie()
            for cookie_name , cookie_value in cookies.items():
                cookie_obj[cookie_name] = cookie_value
            for morsel in cookie_obj.values():
                morsel['path'] = '/'
                self.send_header("Set-Cookie", morsel.OutputString())
        self.send_header('Location',url)
        self.end_headers()
    def add_session(self,email,sessionid):
        with open('session_auth.txt','r') as session_auth_file:
            auth_sessions = session_auth_file.read()
            auth_sessions = json.loads(auth_sessions)
        if email in auth_sessions:
            auth_sessions[email].append(sessionid)
        else: auth_sessions[email] = [sessionid]
        with open('session_auth.txt','w') as session_auth_file:
            session_auth_file.write(json.dumps(auth_sessions))
    def get_user_data(self,email):
        context = {'email':email}

        # firstname = 
        # context['firstname'] = firstname
        return context
    def is_session_authenticated(self):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        if cookies.get('sessionid') == None:
            return False
        sessionid = cookies['sessionid'].value
        with open('session_auth.txt','r') as session_auth_file:
            auth_sessions = session_auth_file.read()
            auth_sessions = json.loads(auth_sessions)
        for email in auth_sessions.keys():
            if sessionid in auth_sessions[email]:
                return  email
        return False
    def render_image(self,path):
        self.send_response(200)
        self.send_header('Content-type','image/png')
        self.end_headers()
        if path.startswith('/login'):
            path = path.replace("/login","")
        if os.path.exists((BASE_DIR+path)):
            if path.startswith('/'):path = path[1:]
            with open(path,'rb') as image:
                self.wfile.write(image.read())
        else:
            with open('prophile-uploads/sample.png','rb') as image:
                self.wfile.write(image.read())
    def remove_session(self):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        if cookies.get('sessionid'):
            session_id = cookies['sessionid'].value
            with open('session_auth.txt','r') as file:
                auth_sessions = file.read()
                auth_sessions = json.loads(auth_sessions)
                for email in auth_sessions:
                    for present_id in auth_sessions[email]:
                        if present_id == session_id:
                            auth_sessions[email].remove(session_id)
            with open('session_auth.txt','w') as file:
                file.write(json.dumps(auth_sessions))   




def main():
    port = 8000
    server_addr = ('127.0.0.1',port)
    server = HTTPServer(server_address=server_addr,RequestHandlerClass=RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n Server Closed bye. \n\n')

if __name__ == '__main__':
    main()
    