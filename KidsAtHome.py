'''
Created on 25 aug 2015

@author: puhlmari
'''
import sched
import time
from datetime import datetime as dt
import datetime
import smtplib
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys

runCounter=0
kid1Home = False
kid2Home = False
parent1Home = False

#retry interval in minutes
retryInterval=5
    
numberOfRetries = 24


def main():

    
    def searchForWlanDevices():
        home = [False,False,False]
        global kid1Home
        global kid2Home
        global parent1Home
        
        #create virtual display
        driver.get("http://dlinkrouter/login.asp")
        elem = driver.find_element_by_name("log_pass")
        #Replace with your router password
        elem.send_keys( ROUTER_PASSWORD )
        elem.send_keys(Keys.RETURN)
        driver.get("http://dlinkrouter/st_wireless.asp")
        e = driver.find_element_by_id("station_table")
        td = e.find_elements_by_tag_name("td")
        for option in td:
            if ":" in option.text:
                print(option.text)
                if option.text == KID1_MAC_ADDRESS:
                    home[0]=True
                elif option.text == KID2_MAC_ADDRESS:
                    home[1]=True  
                elif option.text == PARENT1_MAC_ADDRESS:
                    home[2]=True  
        
        return constructMessage(home)
    
    def constructMessage(home):
        message = ""
        #make sure status has changed
        if(kid1Home != home[0]):
            kid1Home = home[0]
            print("Kid1 status CHANGED ", kid1Home)
            if kid1Home:
                message="Kid1 home, "
            else:
                message="Kid1 NOT home, "
        if(kid2Home != home[1]):
            kid2Home = home[1]
            print("Kid2 status CHANGED ", kid2Home)
            if kid2Home:
                message=message + "Kid2 home, "
            else:
                message=message + "Kid2 NOT home, "
        if(parent1Home != home[2]):
            parent1Home = home[2]
            print("Parent1 CHANGED ", parent1Home)
            if parent1Home:
                message=message + "Parent1 home, "
            else:
                message=message + "Parent1 NOT home, "
        return message
        
    def sendMail(subject):
        gmail_user = GMAIL_ADDRESS
        gmail_pwd = GMAIL_PASSWORD
        FROM = GMAIL_ADDRESS_SENDER
        TO = GMAIL_ADDRESS_RECEIVER
        TEXT = subject

        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), subject, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")

    def scheduleCheck():
        
        global runCounter
        runCounter=runCounter+1
        subject = searchForWlanDevices()
        if subject != "":
            if not(parent1Home):
                print("Sending mail ...")
                sendMail(subject)
            else:
                print("Do nothing. Parents are at home")
        else:
            print("Status unchanged")
        #repeat every X minutes until the run coutner is reached
        if runCounter < numberOfRetries:
            t = dt.now() + datetime.timedelta(minutes=retryInterval)
            scheduler.enterabs(time.mktime(t.timetuple()), 1, scheduleCheck, ())
    
    
    scheduler = sched.scheduler(time.time, time.sleep)
    
    display = Display(visible=0, size=(800, 600))
    display.start()   
    driver = webdriver.Firefox()
    scheduleCheck()
    scheduler.run()
    
    driver.close()
    
if __name__ == '__main__':
    main()

#
