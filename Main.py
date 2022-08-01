from datetime import datetime , timedelta, date
from itertools import count
import re
from matplotlib import use
import mysql.connector as c
from rich.console import Console
from rich.table import Table
import bcrypt
import re
 
# Make a regular expression
# for validating an Email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


bcrypt.hashpw("password", bcrypt.gensalt( 12 ))
console = Console()

database = c.connect(host="localhost", user='root',
                     password="sepehrtavakoli80", database='ChatApp')
# defining cursor(it will be used to excute SQL commands) :-
cursor = database.cursor(buffered=True)
console.print('\nYou are connected to the server ChatApp successfully.\n',style="green")
cursor.execute('CREATE TABLE IF NOT EXISTS users(id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) UNIQUE,firstname VARCHAR(30),lastname VARCHAR(30),phone CHAR(11) NOT NULL UNIQUE,email VARCHAR(50) UNIQUE, pass VARCHAR(256) NOT NULL,deleted CHAR(1))')
cursor.execute('CREATE TABLE IF NOT EXISTS securityQuestions(username VARCHAR(50) PRIMARY KEY ,question VARCHAR(50),answer VARCHAR(50))')
cursor.execute('CREATE TABLE IF NOT EXISTS login(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL ,loginTime VARCHAR(50),logoutTime VARCHAR(50))')
cursor.execute('CREATE TABLE IF NOT EXISTS fallowRequest(id INT AUTO_INCREMENT PRIMARY KEY, destinationUsername VARCHAR(50) NOT NULL, sourceUsername VARCHAR(50) NOT NULL )')
cursor.execute('CREATE TABLE IF NOT EXISTS friends(id INT AUTO_INCREMENT PRIMARY KEY, currentUsername VARCHAR(50) NOT NULL, friendUsername VARCHAR(50) NOT NULL )')
cursor.execute('CREATE TABLE IF NOT EXISTS blockList(id INT AUTO_INCREMENT PRIMARY KEY, blockerUsername VARCHAR(50) NOT NULL, blockedUsername VARCHAR(50) NOT NULL )')
cursor.execute('CREATE TABLE IF NOT EXISTS messages(id INT AUTO_INCREMENT PRIMARY KEY, senderUsername VARCHAR(50) NOT NULL, reciverUsername VARCHAR(50) NOT NULL, sentTime VARCHAR(30), text VARCHAR(70),seen CHAR(1) )')
cursor.execute('CREATE TABLE IF NOT EXISTS likes(id INT AUTO_INCREMENT PRIMARY KEY, messageID INT(4) NOT NULL ,likerUsername VARCHAR(50))')
cursor.execute('CREATE TABLE IF NOT EXISTS recoverPassword(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL ,failedRecoverCount INT(4) NOT NULL)')
cursor.execute('CREATE TABLE IF NOT EXISTS failedLogin(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL ,failedLoginCount INT(4) NOT NULL,startTime VARCHAR(10), endTime VARCHAR(10))')
cursor.execute('CREATE TABLE IF NOT EXISTS systemLog(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL ,loginTime VARCHAR(50) NOT NULL,incorrectPassCount INT(4) NOT NULL,passChangeCount INT(4) NOT NULL)')

# MAKING THE MENU(USER INTERFACE) FOR FRONT END


def menu():
    console.print("\n     Menu ",style="Yellow")
    console.print(" ----------------- ",style="Red")
    console.print("| 1) Login        |")
    console.print("| 2) SignUp       |")
    console.print("| 3) System Log   |")
    console.print("| 4) Exit         |")
    console.print(" ----------------- ",style="Red")
    console.print("\nResponse : ",style="blue")
    a = int(input())
    if (a == 2):
        signUpUser()
    elif(a == 1):
        loginUser()
    elif(a == 3):
        systemLog()
    elif(a == 4):
        console.print('Thank You! for using this program',style="green")
    else:
        console.print('please enter a valid response',style="red")
        menu()

# DEFINING FUNCTIONS FOR FEEDING DATA IN THE TABLES OF THE SERVER

def systemLog():
    sql = "SELECT * FROM systemLog"
    cursor.execute(sql)
    results = cursor.fetchall()

    if(results is None):
        print("No logs found !")
    else :
        table = Table(title="Logs")

        table.add_column("Number", justify="center", style="red Bold", no_wrap=True)
        table.add_column("Username", justify="left", style="cyan", no_wrap=True)
        table.add_column("Login Time", style="yellow")
        table.add_column("Wrong Password Count", justify="left bold", style="blue")
        table.add_column("Password Change Count", justify="left bold", style="blue")

        for data in results:
            table.add_row(str(data[0]),data[1], data[2], str(data[3]), str(data[4]))

        console.print(table)

def submitSystemLog(uname,type):
    if(type == "login"):
        data = (str(datetime.now()),uname)
        statement = "UPDATE systemLog SET loginTime = %s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()
        console.print('\n Log submitted for login.',style="cyan")
    if(type == "wrongPass"):
        sql = "SELECT incorrectPassCount FROM systemLog WHERE username = %s"
        cursor.execute(sql,(uname,))
        result = cursor.fetchone()
        count = result[0]
        if(count == 0 ):
            count = 1
        else :
            count += 1

        data = (count,uname)
        statement = "UPDATE systemLog SET incorrectPassCount = %s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()
        console.print('\n Log submitted for wrong password.',style="cyan")

    if(type == "passChange"):
        sql = "SELECT passChangeCount FROM systemLog WHERE username = %s"
        cursor.execute(sql,(uname,))
        result = cursor.fetchone()
        count = result[0]
        if(count == 0 ):
            count = 1
        else :
            count += 1
        
        data = (count,uname)
        statement = "UPDATE systemLog SET passChangeCount = %s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()

        console.print('\n Log submitted for password chnage .',style="cyan")

def signUpUser():
    # validate username
    sql = "SELECT username,email,phone FROM users"
    cursor.execute(sql)
    results = cursor.fetchall()

    usernames = []
    for data in results:
        usernames.append(data[0])
    emails = []
    for data in results:
        emails.append(data[1])
    phones = []
    for data in results:
        phones.append(data[2])

    uname=" "
    while True:
        uname = input('enter your username : ')
        if(uname in usernames):
            console.print('this username has already taken ! try another one.',style="red")
        else :
            break
    
    fname = input('enter your firstname : ')
    lname = input('enter your lastname : ')

    phone = " "
    # validate phone
    while True:
        phone = input('enter your phone number : ')
        if(phone.isnumeric() and len(phone) == 11):
            if(phone in phones):
                console.print('this phone has already been taken',style="red")
            else:
                break
        else :
            if(phone in phones):
                console.print('this phone has already been taken',style="red")
            else :
                console.print('please enter a valid phone number',style="red")

    #validate email
    while True:
        email = input('enter your email ID : ')
        if(re.fullmatch(regex, email)):
            if(email in emails):
                console.print('this email has already been taken',style="red")
            else :
                break
        else :
            if(email in emails):
                console.print('this email has already been taken',style="red")
            else :
                console.print('please enter a valid email',style="red")

    while True:
        password = input('enter your chosen password : ')
        if len(password) < 8:
            console.print("Make sure your password is at lest 8 letters",style="red")
        elif re.search('[0-9]',password) is None:
            console.print("Make sure your password has a number in it",style="red")
        elif re.search('[A-Z]',password) is None: 
            console.print("Make sure your password has a capital letter in it",style="red")
        else:
            print("Your password seems fine")
            break

    hashedPass = get_hashed_password(password)

    data = (uname, fname, lname, phone, email, hashedPass,"0")

    statement = "INSERT INTO users(username,firstname,lastname,phone,email,pass,deleted) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(statement, data)
    database.commit()

    setSequirityQuestion(uname)

    # for logs at start
    data = (uname,str(datetime.now()),0,0)
    statement = "INSERT INTO systemLog(username,logintime,incorrectPassCount,passChangeCount) VALUES(%s,%s,%s,%s)"
    cursor.execute(statement, data)
    database.commit()

    console.print('\ndata inserted to table users successfully!\n',style="green")

def loginUser():
    uname = input('enter your username : ')

    # check has a active panel or not 
    sql = "SELECT logoutTime FROM login WHERE username=%s"
    val = (uname,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if( result is not None and result[0] == "null"):
        console.print('User dosent log out yet ! please logout first and then login',style="red")
        return

    sql = "SELECT username , pass FROM users WHERE username=%s"
    val = (uname,)
    cursor.execute(sql, val)

    result = cursor.fetchone()
    if(result is None or checkDeleteAccount(uname)== True):
        console.print('User dosent exists !',style="red")

    else:
        password = input('enter your password : ')
        sql = "SELECT id , username , pass FROM users WHERE username=%s"
        val = (uname,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if(check_password(password,result[2]) == False):
            submitSystemLog(uname,"wrongPass")
            checkFailedCount(uname)
            sql = "SELECT * FROM failedLogin WHERE username=%s"
            val = (uname,)
            cursor.execute(sql, val)
            result = cursor.fetchone()

            if(result[2] == 1 or result[2] == 2):
                submitEnterOrNot(uname)
            else :
                if(result[3] > result[4]):
                    print("Your account is now active !")
                else:
                    console.print('\nYour account has not been active yet ! please wait.\n',style="red")
        else:
            console.print('\nLogged in succesfully.\n',style="green")
            submitSystemLog(uname,"login")
            data = (uname, str(datetime.now()), "null")
            statement = "INSERT INTO login(username,loginTime,logoutTime) VALUES(%s,%s,%s)"
            cursor.execute(statement, data)
            database.commit()
            loggedInUser(result[1])

def submitEnterOrNot(uname):
            console.print('Incorrect password , Do you want to recover password ? y/n ',style="red")
            if(str(input()) == 'y'):
                sql = "SELECT failedRecoverCount FROM recoverPassword WHERE username=%s"
                val = (uname, )
                cursor.execute(sql, val)
                result = cursor.fetchone()
                if(result is None or result[0] != 5):
                    recoverPassWithSecurity(uname)
                else :
                    recoverPassWithEmail(uname)

def checkFailedCount(uname):
    sql = "SELECT failedLoginCount,startTime FROM failedLogin WHERE username=%s"
    val = (uname,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    count = 0
    if(result is None):
        data = (uname,0,"null")
        statement = "INSERT INTO failedLogin(username,failedLoginCount,startTime) VALUES(%s,%s,%s)"
        cursor.execute(statement, data)
        database.commit()
    else : 
        count = result[0]

    if(count != 3 ):
        count += 1 
    if(count == 3 and result[1] == "null"):
        currentTime =  date.today()
        untilTime = currentTime + timedelta(days=1)

        data = (3,currentTime,untilTime,uname)
        statement = "UPDATE failedLogin SET failedLoginCount=%s, startTime = %s,endTime = %s WHERE username = %s" 
        cursor.execute(statement, data)
        database.commit()

        console.print('\nYour account has been blocked until '+ str(untilTime) ,style="red bold")
        
    else :
        data = (count,uname)
        statement = "UPDATE failedLogin SET failedLoginCount=%s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()
        console.print('\nIncorrect password attempt : '+ str(count) ,style="yellow")

def recoverPassWithEmail(uname):
    email = input('\nEnter your Email : ')
    phone = input('\nEnter your Phone : ')
    sql = "SELECT phone , email , pass FROM users WHERE username=%s"
    val = (uname,)
    cursor.execute(sql, val)
    result = cursor.fetchone()

    if(result[0] == phone and result[1] == email):
        console.print('\n Please change your password.',style="yellow bold")
        changePassword(uname)
    else:
        console.print('\n Incorrect email or password ',style="red bold")

def recoverPassWithSecurity(uname):
    sql = "SELECT question , answer FROM securityQuestions WHERE username=%s"
    val = (uname,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    question = input('\nEnter your security question : \n')
    answer = input('\nEnter your security question answer : \n')

    if(result[0] == question and result[1] == answer):
        # sql = "SELECT pass FROM users WHERE username=%s"
        # val = (uname, )
        # cursor.execute(sql, val)
        # result = cursor.fetchone()
        # console.print('\n Your password is : '+result[0],style="yellow bold")
        console.print('\n Please change your password.',style="yellow bold")
        changePassword(uname)
    else :
        console.print('\nYour security question or password is incorrect !',style="red bold")

        sql = "SELECT failedRecoverCount FROM recoverPassword WHERE username=%s"
        val = (uname, )
        cursor.execute(sql, val)
        result = cursor.fetchone()

        if(result is not None):
            count = int(result[0])
        else :
            count = 0
            data = (uname,0)
            statement = "INSERT INTO recoverPassword(username,failedRecoverCount) VALUES(%s,%s)"
            cursor.execute(statement, data)
            database.commit()

        count += 1

        if(count == 5):
            console.print('\nYour are blocked from using security question recovering !',style="red") 
            recoverPassWithEmail(uname)
        else:
            console.print('\nFailed recover attempts : ' + str(count),style="blue")

        data = (count,uname)
        statement = "UPDATE recoverPassword SET failedRecoverCount=%s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()

def loggedInUser(username):
    while True :
        console.print("\n         User Menu ",style="Yellow")
        console.print(" ------------------------- ",style="Red")
        console.print("| 1) Send Friend Request  |",style="cyan bold")
        console.print("| 2) Block a User         |",style="cyan bold")
        console.print("| 3) Send Message         |",style="cyan bold")
        console.print("| 4) Inbox                |",style="cyan bold")
        console.print("| 5) Show Liked Messages  |",style="cyan bold")
        console.print("| 6) Fallow requests      |",style="cyan bold")
        console.print("| 7) Delete Account       |",style="cyan bold")
        console.print("| 8) Unblock a User       |",style="cyan bold")
        console.print("| 9) Remove friend        |",style="cyan bold")
        console.print("| 10) Recover Password    |",style="cyan bold")
        console.print("| 11) Logout              |",style="cyan bold")
        console.print(" ------------------------- ",style="Red")
        console.print("\nResponse : ",style="blue")
        a = int(input())
        if(a==1):
            sendFriendRequest(username)
        if(a==2):
            blockUser(username)
        if(a==3):
            sendMessage(username)
        if(a==4):
            showInbox(username)
        if(a==5):
            showLikedMessage(username)
        if(a==6):
            showFallowRequests(username)
        if(a==7):
            deleteAccount(username)
        if(a==8):
            unblockUser(username)
        if(a==9):
            removeFriend(username)
        if(a==10):
            recoverPassWithSecurity(username)
        if(a==11):
            logoutUser(username)
            break

def removeFriend(uname):
        friendUsername = input('Enter the friend you want to remove : ')
        sql = "SELECT id FROM friends WHERE currentUsername=%s and friendUsername=%s"
        val = (uname,friendUsername)
        cursor.execute(sql, val)

        result = cursor.fetchone()
        if(result is None):
            console.print('User dosent exists in your friend list !',style="red")
        else:
            statement = "DELETE FROM friends WHERE currentUsername=%s and friendUsername=%s"
            cursor.execute(statement,val)
            database.commit()
            console.print('\nFriend Removed !',style="green")

def logoutUser(uname):
    data = (str(datetime.now()),uname)
    statement = "UPDATE login SET logoutTime = %s WHERE username = %s"
    cursor.execute(statement, data)
    database.commit()

def deleteAccount(uname):
    inpute = input("Are you sure ? y/n")
    if(inpute == 'y'):
        data = ("1",uname)
        statement = "UPDATE users SET deleted = %s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()

        # delete security questions
        statement = "DELETE FROM securityQuestions WHERE username = %s"
        cursor.execute(statement,(uname,))
        database.commit()
        console.print('\nUser deleted !',style="green")

        # delete friends
        statement = "DELETE FROM friends WHERE currentUsername=%s"
        cursor.execute(statement,(uname,))
        database.commit()
        console.print('\nFriends Removed !',style="green")
    else :
        return

def checkDeleteAccount(uname):
    sql = "SELECT deleted FROM users WHERE username =%s "
    val = (uname,)
    cursor.execute(sql, val)
    results = cursor.fetchone()
    if(results[0] == "1"):
        return True
    else :
        return False

def showLikedMessage(username):
    sql = "SELECT * FROM likes,messages WHERE likes.messageID = messages.id and likerUsername =%s "
    val = (username,)
    cursor.execute(sql, val)
    results = cursor.fetchall()

    if len(results) == 0:
        console.print("You have no liked message ! try like them from your inbox.",style="cyan")
        return
    else:
        num = 1
        table = Table(title="My Inbox")

        table.add_column("Number", justify="center", style="red Bold", no_wrap=True)
        table.add_column("Sender", justify="left", style="cyan", no_wrap=True)
        table.add_column("Text", style="yellow")
        table.add_column("Date & Time", justify="left bold", style="blue")

        for data in results:
    
            table.add_row(str(num),data[4], data[7], data[6])
            num = num + 1

        console.print(table)

def showInbox(username):
    sql = "SELECT * FROM messages WHERE reciverUsername = %s ORDER BY sentTime desc"
    val = (username,)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    if len(results) == 0:
        console.print("You have no messages !",style="red")
        return
    else:
        num = 1
        for data in results:
            seenText = "NO"
            if(data[5]=='0'):
                updateSeenMessage(username)
            else:
                seenText = "YES"

            table = Table(title="My Inbox")

            table.add_column("Number", justify="center", style="red Bold", no_wrap=True)
            table.add_column("Sender", justify="left", style="cyan", no_wrap=True)
            table.add_column("Text", style="yellow")
            table.add_column("Date & Time", justify="left bold", style="blue")
            table.add_column("Seen", justify="left", style="green")
            table.add_column("Deleted", justify="left", style="green")

            # check user deleted
            deleted = checkDeleteAccount(username)

            table.add_row(str(num),data[2], data[4], data[3],seenText,str(deleted))

            console.print(table)

            num = num + 1

        console.print('\nDo you want to like a message ? y/n \n',style="yellow")
        like = input()
        if(like == 'y'):
            numberLike = int(input('\nEnter message number to like : '))
            likeMessage(results[numberLike-1][0],username)

def likeMessage(messageID,username):
    data = (messageID,username)
    statement = "INSERT INTO likes(messageID,likerUsername) VALUES(%s,%s)"
    cursor.execute(statement, data)
    database.commit()
    console.print('\nYou liked the message successfully.',style="green")

def updateSeenMessage(username):
    data = ("1",username)
    statement = "UPDATE messages SET seen=%s WHERE reciverUsername=%s"
    cursor.execute(statement, data)
    database.commit()
    console.print('\nMessages seen !',style="green")

def blockUser(username):
    user = input('Enter the username you want to Block : ')
    
    sql = "SELECT username FROM users WHERE username=%s"
    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if(result is None):
        console.print('User dosent exists !',style="red")
    else:
        data = (username,user)
        statement = "INSERT INTO blockList(blockerUsername,blockedUsername) VALUES(%s,%s)"
        cursor.execute(statement, data)
        database.commit()
        console.print('\nUser '+user+' Blocked ! To send message please unBlock him/her .',style="red")

def unblockUser(uname):
    user = input('Enter the username you want to unBlock : ')
    
    sql = "SELECT username FROM users WHERE username=%s"
    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if(result is None):
        console.print('User dosent exists !',style="red")
    else:
        data = (uname,user)
        statement = "DELETE FROM blockList WHERE blockerUsername =%s and blockedUsername=%s"
        cursor.execute(statement, data)
        database.commit()
        console.print('\nUser '+user+' UnBlocked .',style="red")

def sendMessage(username):
    print('Here is all of your friends:')
    sql = "SELECT friendUsername FROM friends WHERE currentUsername = %s"
    val = (username,)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    if len(results) == 0:
        console.print("You have no friend ! try fallow them.",style="cyan")
        return
    else:
        num = 1
        for data in results:
            console.print(str(num) + ") "+data[0])
            num = num + 1
        distination = int(input('\nwhich one do you want to send a message ? '))
        userDist = results[distination-1][0]
        if(checkDeleteAccount(username) == True):
            console.print('\nThis user has been deleted ! ')
            return
        checkBlocked(username,userDist)

def checkBlocked(username,userDist):
    sql = "SELECT blockerUsername FROM blockList WHERE blockedUsername = %s"
    val = (username,)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    if len(results) == 0:
        console.print("No one blocked you.",style="yellow")
    else:
        for data in results:
            if(userDist == data[0]):
                console.print('\nUser '+userDist+' Blocked you ! you cannot send message to them .\n',style="red")
                return
    textMessage = input('\nEnter your message : ')
    data = (username,userDist,str(datetime.now()),textMessage,0)
    statement = "INSERT INTO messages(senderUsername,reciverUsername,sentTime,text,seen) VALUES(%s,%s,%s,%s,%s)"
    cursor.execute(statement, data)
    database.commit()
    console.print('\nMessage sent to '+userDist+' succesfully .',style="green")

def showFallowRequests(username):
    sql = "SELECT sourceUsername FROM fallowRequest WHERE destinationUsername = %s"
    val = (username,)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    if len(results) == 0:
        console.print("There is not any fallow request for you :(",style="cyan")
        return
    else:
        console.print('Choose one fallow request : \nResponse : ')
        num = 1
        for data in results:
            console.print(str(num) + ") "+data[0])
            num = num + 1
        inputNum = int(input())
        fallowReqUser = results[inputNum-1][0]

        console.print('You have a reuqest from '+fallowReqUser+' Do you want to accept or delete ?\n1) Accept\n2) Delete\n3) Cancel\nResponse : ',style="yellow")
        inputNum2 = int(input())

        if(inputNum2 == 1):
            acceptFallowRequest(username,fallowReqUser)
        elif (inputNum2 == 2):
            deleteFallowRequest(username,fallowReqUser)
        elif(inputNum2 == 3):
            return
        else :
            showFallowRequests(username)

def acceptFallowRequest(currentUsername,friendUsername):
    data = (currentUsername,friendUsername)
    statement = "INSERT INTO friends(currentUsername,friendUsername) VALUES(%s,%s)"
    cursor.execute(statement, data)
    database.commit()
    console.print('\nUser '+friendUsername+' is now your friend !',style="green")
    deleteFallowRequest(currentUsername,friendUsername)

def deleteFallowRequest(currentUsername,friendUsername):
    data = (currentUsername,friendUsername)
    statement = "DELETE FROM fallowRequest WHERE destinationUsername=%s and sourceUsername=%s"
    cursor.execute(statement, data)
    database.commit()
    console.print('\nFallow request from '+friendUsername+' deleted .',style="green")

def sendFriendRequest(usernameSource):
    usernameToFallow = input('enter the username you want to fallow : ')
    usernameToFallow  = "%"+usernameToFallow+"%"
    sql = "SELECT username FROM users WHERE username LIKE %s"
    val = (usernameToFallow,)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    if len(results) == 0:
        console.print("There is not any user with this data !",style="red")
        return
    else:
        num = 1
        for data in results:
            console.print(str(num) + ") "+data[0])
            num = num + 1
        userNumeDist = int(input("Choose which user to fallow : "))
        val = (results[userNumeDist-1][0],usernameSource)
        statement = "INSERT INTO fallowRequest(destinationUsername,sourceUsername) VALUES(%s,%s)"
        cursor.execute(statement, val)
        database.commit()
        console.print("\nfallow request sent to "+results[userNumeDist-1][0],style="green")

def setSequirityQuestion(username):
    question = input('enter your security question : ')
    anwser = input('enter your security answer : ')
    data = (username, question, anwser)
    statement = "INSERT INTO securityQuestions VALUES(%s,%s,%s)"
    cursor.execute(statement, data)
    database.commit()

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)

def changePassword(uname):
    console.print('\nEnter your new password : ',style="blue")
    input1 = input()
    console.print('\nRepeat your new password : ',style="blue")
    input2 = input()

    if(input1 != input2):
        console.print('Password repeat dosent match !',style="red")
    else :
        data = (get_hashed_password(input1),uname)
        statement = "UPDATE users SET pass = %s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()
        console.print('\nPassword chaneged to : '+input2,style="green")
               
        submitSystemLog(uname,"passChange")

        data = (0,uname)
        statement = "UPDATE recoverPassword SET failedRecoverCount=%s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()

        data = (0,uname)
        statement = "UPDATE failedLogin SET failedLoginCount=%s WHERE username = %s"
        cursor.execute(statement, data)
        database.commit()

# FINALLY, SERVING THE PROGRAM TO USER : -
menu()
