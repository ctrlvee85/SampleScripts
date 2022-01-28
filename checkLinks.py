# ----------------------------------------------------------------------------
# Broken Link Check: checkLinks.py
# Written by: Jennifer McCall
# Description: Checks the data source links in an aprx file
# texts and emails if link is broken
# ----------------------------------------------------------------------------


import arcpy,os, email, smtplib, ssl
from datetime import date, datetime, timedelta
# Import the email modules we'll need
from email import encoders
from email.mime.base import MIMEBase
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

wd = "Sample Drive"
times1 = list()
times1.append(time.time())
def timestamp():
    #Timestamp for printing on output, formatted as m/d h:m:s e.g. 3/4 13:58:24 
    times1.append(time.time())  # float format; datetime.now() is datetime format
    return " ["+"{dt.month}/{dt.day} {dt:%H}:{dt:%M}:{dt:%S}".format(dt=datetime.now())+"] "



def addMsg(msg, ts=True, warning=False): 
    """Print time-stamped message to results and to log file. """
    """(Can use 2nd parameter to optionally turn off timestamp.)"""
    
    if ts: msg = timestamp() + msg
    # arcpy.AddMessage(msg) for running as a Python Toolbox; print(msg) for standalone
    
    arcpy.AddWarning(msg) if warning else arcpy.AddMessage(msg)
     # Print to logFile also if it exists
     # Set log folder to contain log files
    logFldr = wd
    logFile = logFldr + "\\checkLinksLog_"+time.strftime("%Y%m")+".log"
    if not os.path.exists(logFldr):  
        addMsg("Creating folder to contain script results logs,\n  {0}...".format(logFldr))
        os.makedirs(logFldr)
        
    try: logFile
    except NameError: logFile_exists = False
    else: logFile_exists = True
    if logFile_exists:
        with open(logFile, "a") as myFile: myFile.write (msg+"\n")

# Define project location and check for broken links
aprx = arcpy.mp.ArcGISProject("\\PWQCM_LinkCheck.aprx")  
brknLinkSrc = aprx.listBrokenDataSources()  
brknLayer = []
# Information for logging into gmail sender account
me = "email@gmail.com"
pas = "emailpass"
# Address for sending text message
sms_roberto = "email"
sms_jen = "email"
sms_gerry = "email"
robertoEmail= "email"
jenEmail= "ctrl.vee@gmail.com"
gerryEmail= "email"
#gmail connection information
smtp = "smtp.gmail.com" 
port = 465
# Create a secure SSL context
context = ssl.create_default_context()
addMsg("looking for broken links")

#Function checks ArcGIS Pro project for broken links
def linkCheck():
    for item in brknLinkSrc:  
        brknLayer.append(item.name)
        addMsg("looking for broken links")
        #if no broken links found, do nothing  
        #if broken data source found, send name of the layer to email and text    
        if brknLayer:
            for item in brknLayer:
                #create the message to be sent
                subject = "Broken Data Source Link Found"
                body = item + " layer data source link is broken"
                message = MIMEMultipart()
                message["From"] = me
                message["To"] = robertoEmail
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))
                
                email = message.as_string()        
                #send the email and text
                addMsg("broken links found, sending email and text")
                with smtplib.SMTP_SSL(smtp, port, context=context) as server:
                    server.login(me, pas)
                    server.sendmail(me,sms_roberto,email)                    
                    server.sendmail(me,sms_jen,email)                    
                    server.sendmail(me,sms_gerry,email)
                    server.sendmail(me, robertoEmail, email)                    
                    server.sendmail(me, jenEmail, email)
                    server.sendmail(me, gerryEmail, email)
        else:
            print("no broken links found")            

# Function to create database connection, and alert if connection is not able to be made
def dbPath():
        #parameters for database
        Folder = wd
        databasename = "10.35.11.19"
        platform = "SQL_Server"
        instance = "10.35.11.19"
        authentication = "DATABASE_AUTH"
        dbname = "dbname"
        user = "dbuser"
        pword = "password"        
        #Connect to database
        arcpy.CreateDatabaseConnection_management(Folder, databasename, platform, instance, authentication, user,pword,"",dbname)
        #print("Done!!")

        times1 = list()
        times1.append(time.time())

        # ArcPro PROD SDE connection file to target DB
        dbPath = Folder +  "\\" + databasename + ".sde" 

        if os.path.exists(dbPath):
            addMsg("Database connection created")
            
        else:
            subject = "Database Connection to DTDGIS Failed"
            body = "Failed to make connection to Production database"
            message = MIMEMultipart()
            message["From"] = me
            message["To"] = robertoEmail
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            email = message.as_string()        
            #send the email and text
            addMsg("Database connection broken, sending email and text")
            with smtplib.SMTP_SSL(smtp, port, context=context) as server:
                server.login(me, pas)
                server.sendmail(me,sms_roberto,email)                    
                server.sendmail(me,sms_jen,email)                    
                server.sendmail(me,sms_gerry,email)
                server.sendmail(me, robertoEmail, email)                    
                server.sendmail(me, jenEmail, email)
                server.sendmail(me, gerryEmail, email)
        arcpy.Delete_management(dbPath)        

linkCheck()
dbPath()                


addMsg("finished at " + time.strftime("%Y%m%d"))
