import smtplib

server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()

server.login('karthikeya6009@gmail.com','your_API_Password')

server.sendmail('karthikeya6009@gmail.com','nagulakondakarthikeya@gmail.com','HI karthikeya')

print("mail sent")
