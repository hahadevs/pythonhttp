import mysql.connector as connector


class Database:

    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.__password = 'root' 
        self.database = 'module1'
        self.__conn = False
        self.__cursor = False

    def connect(self):
        try:
            self.__conn = connector.connect(
                host=self.host,
                user=self.user,
                password=self.__password,
                database=self.database,
            )
            self.__cursor = self.__conn.cursor()
        except Exception as e :
            raise ConnectionRefusedError(str(e))

    def insert_user_data(self,firstname,lastname,email,password,prophile):
        self.check_connection()
        try:
            """
            Inserting the data into user_data table using following command
            """
            command = f"""INSERT INTO `user_data` ( `firstname`, `lastname`, `email`, `password` , `prophile` ) VALUES ( '{firstname}', '{lastname}', '{email}', "{password}" , "{prophile}");"""

            self.__cursor.execute(command)
            self.__conn.commit()            
        except Exception as e :
            raise EOFError(str(e))
    
    def insert_into(self,**kwargs): 
        self.check_connection()
        kwargs['user_id'] = self.get_pk_id(kwargs['user_id'])
        try:
            """
            Inserting the data into user_data table using following command
            """
            command = f"""INSERT INTO `{kwargs['table']}` ( """
            print(command)
            for key,value in kwargs.items():
                if key == 'table':
                    continue
                command = command + " `" + key + "` " + ","
            if command.endswith(","):command = command.removesuffix(",")
            command += ") VALUES ( "
            for key,value in kwargs.items():
                if key == 'table':
                    continue
                command += f"'{value}' ,"
            if command.endswith(","):command = command.removesuffix(",")
            command += ");"
            self.__cursor.execute(command)
            self.__conn.commit()     


        except Exception as e :
            raise EOFError(str(e))
    
    def get_pk_id(self,email):
        command = f"""SELECT user_id FROM user_data WHERE email='{email}'"""
        self.__cursor.execute(command)
        fetched_rows = self.__cursor.fetchall()
        return fetched_rows[0][0]

    def authenticate(self,email,password):
        """
        Return true if the email and password is valid.
        """
        self.check_connection()
        # Following command is going to be execute in mysql command line
        command = f"""SELECT * FROM user_data WHERE email='{email}'"""
        # Executing the command in database
        self.__cursor.execute(command)
        # fetchall returns a list with respect to command
        fetched_rows = self.__cursor.fetchall()
        if len(fetched_rows) == 1 and fetched_rows[0][4] == password:
            # if email and password found in database
            return True
        else:
            return False
        
    def delete_user(self,email,database_password):
        if database_password == self.__password:
            command = """DELETE FROM user_data WHERE email='{email}';"""
            # Executing the command in database
            self.__cursor.execute(command)
            self.__conn.commit()
            print(self.__cursor.rowcount)
        else:
            raise Exception("Wrong Database Password ")

    def get_all_user_data(self,email):
        all_data = {
            'email':email,
        } 
        # user data
        command = f"""SELECT user_id , firstname ,lastname ,prophile from user_data WHERE `email` = '{email}' ;"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        foreign_key = row[0][0]
        all_data['firstname'] = row[0][1]
        all_data['lastname'] = row[0][2]
        all_data['prophile'] = row[0][3]

        # user_skills
        command = f"""SELECT skill_name , proficiency from user_skills WHERE `user_id` = '{foreign_key}' ;"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['skill_name'] = row[0][0]
        all_data['proficiency'] = row[0][1]

        # user_addresses
        command = f"""select street , city , state , zipcode from user_addresses where user_id = {foreign_key} ;"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['street'] = row[0][0]
        all_data['city'] = row[0][1]
        all_data['state'] = row[0][2]
        all_data['zipcode'] = row[0][3]

        # user_education
        command = f"""select degree , major , university , graduation_year from user_education where user_id = {foreign_key};"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['degree'] = row[0][0]
        all_data['major'] = row[0][1]
        all_data['university'] = row[0][2]
        all_data['graduation_year'] = row[0][3]

        #uer_experience
        command = f"""select name , position , responsibilities , start_date , end_date from user_experience where user_id = {foreign_key};"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['exp_name'] = row[0][0]
        all_data['position'] = row[0][1]
        all_data['responsibilities'] = row[0][2]
        all_data['start_date'] = row[0][3]
        all_data['end_date'] = row[0][4]

        #user_certificates
        command = f"""select name , issuing_organization , date from user_certifications where user_id = {foreign_key};"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['certificate_name'] = row[0][0]
        all_data['issuing_organization'] = row[0][1]
        all_data['date'] = row[0][2]

        #user_projects
        command = f"""select name , description , technology_used from user_projects where user_id = {foreign_key} ;"""
        self.__cursor.execute(command)
        row = self.__cursor.fetchall()
        all_data['project_name'] = row[0][0]
        all_data['description'] = row[0][1]
        all_data['technology_used'] = row[0][2]
        return all_data

    def get_row(self,table_name:str,**kwargs)->list:
        self.check_connection()
        command = f"""SELECT * from {table_name} WHERE """
        for key in kwargs:
            command += f"{key} = {kwargs[key]} "
        command += " ) ;"
        self.__cursor.execute(command)
        return self.__cursor.fetchall()
    def check_connection(self):
        """
        checking if connection is established of not 
        """
        if self.__cursor:pass
        else:raise ConnectionError("Connection not established , try connect() first")

    def close_connection(self):
        self.__conn.close()
        print("Connection is closed.")
        print("Use connect() method to work with database.")
    def __del__(self):
        if self.__conn:
            self.__conn.close()
    def __str__(self):
        print_ = f"""\nHOST : {self.host}\nUSER : {self.user}\nDATABASE : {self.database}\n"""
        return print_


if __name__ == '__main__':
    import random
    db = Database()
    db.connect()
    print(db.get_all_user_data('unique@gmail.com'))
    # db.insert_user_data(
    #     firstname='amrit',
    #     lastname='singh',
    #     email=f'amrit{random.randint(1000,9999)}@gmail.com',
    #     password='123'
    #     )

    #Exists
    # print(db.authenticate(email='amrit8536@gamil.com',password='123'))

    #not Exists
    # print(db.authenticate(email='random@gami.com',password='random'))


    # db.delete_user(email='live@gmail.com',database_password='admin1')


