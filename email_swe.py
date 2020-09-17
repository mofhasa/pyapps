import csv
import sqlite3
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


USERNAME = "<your gmail username>"
SENDER = "yadavkartik.work@gmail.com"
PASSWORD = "<your_password>"
SKILLS = """Java, JavaScript, Python, Solutions Architecture, AWS/Azure, SDLC, Microservices, SOA 
"""
EMAIL_BODY = """Dear {0},

I am excited to be applying for this engineering position at {1}! This letter is to express my interest in software engineering/development roles. Equipped with a self-motivating persistent attitude, seamless communication skills and driven work ethic I comfortably fit in any dev/research environment and strive towards being a catalyst during every iteration of work on a product or project. I am delighted at the opportunity to showcase my skillset and possibly contribute in order to deliver a great product or make existing ones ever better.

My skillset and experience match with the following opportunities:
{2}

I have expertise in the following programming languages, frameworks and tools:
{3}

I am actively interviewing at the moment and would love to get the opportunities to attempt at interviewing for the aforementioned roles. I have attached my resume to this email.

I eagerly look forward to your response.

Thanks!

Sincerely,

Kartik Yadav
(585) 317-5712
yadavkartik.work@gmail.com

"""

def sendColdEmails(db):
    cur = db.cursor()
    port = 465
    context = ssl.create_default_context()
    smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)


    smtpObj.login(user=USERNAME, password=PASSWORD)
    receivers = ['yadavkartik.work@gmail.com']

    cmd_getcoms = """SELECT * FROM Companies """
    cur.execute(cmd_getcoms)
    matching_coms = cur.fetchall()
    com_d = {}
    for c in matching_coms:
        com_d[c[0]] = c[1]

    cmd_getRecs = """SELECT name, company, email, last_communicated FROM Recruiters WHERE last_communicated is NULL """
    cur.execute(cmd_getRecs)
    matching_recs = cur.fetchall()

    for rec in matching_recs:
        if rec[3] is None:
            receiver_name = rec[0]
            company = rec[1]
            receiver_email = rec[2]

            cmd_getPositions= """SELECT title, link FROM Positions WHERE company_id = ?"""
            cur.execute(cmd_getPositions, (str(company)))
            matching_positions = cur.fetchall()
            positions = ""

            for position in matching_positions:
                positions += str(position[0]) + " [" + str(position[1]) + "]\n"

            msg = MIMEMultipart()
            msg['From'] = "Kartik Yadav <yadavkartik.work@gmail.com>"
            msg['To'] = rec[0] +" "+ receiver_email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "Interest in Software Engineering opportunities at " + com_d[company]
            msg.attach(MIMEText(EMAIL_BODY.format(receiver_name, com_d[company], positions, SKILLS)))
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open("resume.docx", "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="resume.docx"')
            msg.attach(part)

            smtpObj.sendmail(SENDER, receivers, msg.as_string())
            print("Successfully sent email to {0}".format(receiver_email))


def refreshingPositions(db):
    cur = db.cursor()
    cmd_getcoms = """SELECT * FROM Companies """
    cur.execute(cmd_getcoms)
    matching_coms = cur.fetchall()

    com_d = {}
    for c in matching_coms:
        com_d[c[1]] = c[0]

    csv_file = open('resources/positions.csv', mode='r')
    csv_reader = csv.DictReader(csv_file)

    for row in csv_reader:
        company_id = row["ï»¿company"]
        title = row["title"]
        link = row["link"]
        keywords = row["keywords"]

        try:
            cmd_ins = """INSERT INTO Positions(company_id, title, link, keywords) VALUES(?,?,?,?)"""
            cur.execute(cmd_ins, (com_d[company_id], title, link, keywords))
            db.commit()
        except Exception as e:
            print("Failed to insert new position {0} at {1}".format(title, company_id))
            print(e)

    cur.close()

def checkForNewRecruitersAndCompanies(db):
    cur = db.cursor()

    csv_file = open('resources/recruiters.csv', mode='r')
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        name = row["name"]
        company = row["ï»¿company"].strip()
        email = row["email"]
        domain = row["email"].split("@")[1]

        cmd_coms = """SELECT * FROM Companies """
        cur.execute(cmd_coms)
        coms = cur.fetchall()
        com_d = {}
        for c in coms:
            com_d[c[1]] = c[0]

        try:
            cmd_getRecs = "SELECT COUNT(*) FROM Recruiters WHERE name = '"+name+"' AND company="+str(com_d[company])+" AND email='"+str(email)+"'"
            cur.execute(cmd_getRecs)
            matching_recs = cur.fetchall()[0][0]
        except KeyError:
            matching_recs = 0

        cmd_getComs = """SELECT COUNT(*) FROM Companies WHERE name = ?"""
        cur.execute(cmd_getComs, (company, ))
        matching_coms = cur.fetchall()[0][0]


        company_id = None
        if matching_coms == 0:
            cmd_coms = """INSERT INTO Companies(name) VALUES(?)"""
            cur.execute(cmd_coms, (company, ))
            db.commit()
            company_id = cur.lastrowid

        if matching_recs == 0:
            cmd_ins = """INSERT INTO Recruiters(name, company, email, domain) VALUES(?,?,?,?)"""
            cur.execute(cmd_ins, (name, company_id, email, domain))
            db.commit()


    cur.close()


def init_dbConnection():
    conn = None
    try:
        conn = sqlite3.connect("apps.sqlite")
    except Exception as e:
        print(e)
    return conn


def main():
    db = init_dbConnection()
    checkForNewRecruitersAndCompanies(db)
    refreshingPositions(db)
    sendColdEmails(db)
    db.close()

if __name__ == '__main__':
    main()