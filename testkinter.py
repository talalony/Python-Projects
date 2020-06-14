from tkinter import *
import os

balance1 = 1852.99
incorrectLabel = Label
notFoundLabel = Label
def delete2():
    screen3.destroy()

def delete3():
    screen4.destroy()

def delete4():
    screen5.destroy()

def logOut():
    screen8.destroy()

def depositing():
    global balance1
    global screen11
    deposited = float(toDeposit.get())
    balance1 += deposited
    toDeposit.delete(0, END)
    Label(screen11, text='deposit completed', fg='green', font=('calibri', 11)).pack()

def transfered():
    global balance1
    check = float(transfer.get())
    balance1 -= check
    transfer.delete(0, END)
    Label(screen10, text='transfer completed', fg='green', font=('calibri', 11)).pack()

def deposit():
    global toDeposit
    global screen11
    screen11 = Toplevel(screen)
    screen11.title('info')
    screen11.geometry('300x250')
    Label(screen11, text= 'how much would you like to deposit?')
    toDeposit = Entry(screen11)
    toDeposit.pack()
    Button(screen11, text= 'deposit', command= depositing).pack()


def checkBalance():
    screen9 = Toplevel(screen)
    screen9.title('info')
    screen9.geometry('300x250')
    Label(screen9, text= f'your balance is {balance1} $').pack()

def wireTransfer():
    global transfer
    global screen10
    screen10 = Toplevel(screen)
    screen10.title('info')
    screen10.geometry('300x250')
    Label(screen10, text= 'how much do you want to transfer?').pack()
    transfer = Entry(screen10)
    transfer.pack()
    Button(screen10, text= 'transfer', command= transfered).pack()



def session():
    global screen8
    screen8 = Toplevel(screen)
    screen8.title('dashboard')
    screen8.geometry('400x400')
    Label(screen8, text ='Welcome, what would you like to do?', bg= 'grey', width= '300', height= '2',  font= ('calibri', 13)).pack()
    Button(screen8, text= 'check account balance', width= 20, height= 1, command= checkBalance).pack()
    Button(screen8, text= 'wire transfer', width= 20, height= 1, command=wireTransfer).pack()
    Button(screen8, text= 'deposit', width= 20, height= 1, command=deposit).pack()
    Label(screen8, text='').pack()
    Label(screen8, text='').pack()
    Label(screen8, text='').pack()
    Label(screen8, text='').pack()
    Button(screen8, text= 'log out', width= 20, height= 1, command= logOut).pack()

def loginSuccess():
    session()

def passwordIncorrect():
    global incorrectLabel
    incorrectLabel = Label(screen2, text='incorrect password', fg='red', font=('calibri', 11))
    incorrectLabel.pack()
    userNameEntry1.delete(0, END)
    passwordEntry1.delete(0, END)
    notFoundLabel.destroy()

def userNotFound():
    global notFoundLabel
    notFoundLabel = Label(screen2, text='user not found', fg= 'red', font= ('calibri', 11))
    notFoundLabel.pack()
    userNameEntry1.delete(0, END)
    passwordEntry1.delete(0, END)
    incorrectLabel.destroy()

def registerUser():
    userNameInfo = userName.get()
    passwordInfo = password.get()

    file = open(userNameInfo, 'w')
    file.write(userNameInfo+'\n')
    file.write(passwordInfo)
    file.close()

    userNameEntry.delete(0, END)
    passwordEntry.delete(0, END)

    Label(screen1, text= 'successful registration', fg= 'green', font= ('calibri', 11)).pack()

def loginVerify():
    userName1 = userNameVerify.get()
    password1 = passwordVerify.get()
    userNameEntry1.delete(0, END)
    passwordEntry1.delete(0, END)

    listOfFiles = os.listdir()
    if userName1 in listOfFiles:
        file1 = open(userName1, 'r')
        verify = file1.read().splitlines()
        if password1 in verify:
            loginSuccess()
        else:
            passwordIncorrect()
    else:
        userNotFound()



def registerScreen():
    global screen1
    screen1 = Toplevel(screen)
    screen1.title('register')
    screen1.geometry('300x250')

    global userName
    global password
    global userNameEntry
    global passwordEntry
    userName = StringVar()
    password = StringVar()

    Label(screen1, text='pls enter new username and password', bg= 'grey', width= '300', height= '2',  font= ('calibri', 13)).pack()
    Label(screen1, text='').pack()
    Label(screen1, text= 'username * ').pack()
    userNameEntry = Entry(screen1, text= userName)
    userNameEntry.pack()
    Label(screen1, text= 'password * ').pack()
    passwordEntry = Entry(screen1, text= password)
    passwordEntry.pack()
    Label(screen1, text='').pack()
    Button(screen1, text= 'register', width= '10', height= '1', command= registerUser).pack()


def login():
    global screen2
    screen2 = Toplevel(screen)
    screen2.title('login')
    screen2.geometry('300x250')

    Label(screen2, text='pls enter username and password', bg= 'grey', width= '300', height= '2',  font= ('calibri', 13)).pack()
    Label(screen2, text='').pack()

    global userNameVerify
    global passwordVerify
    userNameVerify = StringVar()
    passwordVerify = StringVar()

    global userNameEntry1
    global passwordEntry1


    Label(screen2, text='username * ').pack()
    userNameEntry1 = Entry(screen2, textvariable= userNameVerify)
    userNameEntry1.pack()
    Label(screen2, text='').pack()
    Label(screen2, text='password * ').pack()
    passwordEntry1 = Entry(screen2, textvariable= passwordVerify)
    passwordEntry1.pack()
    Label(screen2, text='').pack()
    Button(screen2, text= 'login', width= '10', height= '1', command= loginVerify).pack()



def mainScreen():
    global screen
    screen = Tk()
    screen.geometry('300x250')
    screen.title('login or register')
    Label(text= 'please log in or register ', bg= 'grey', width= '300', height= '2',  font= ('calibri', 13)).pack()
    Label(text= '').pack()
    Button(text= 'login', width= '30', height= '2', command= login).pack()
    Label(text='').pack()
    Button(text= 'register', width= '30', height= '2', command= registerScreen).pack()

    screen.mainloop()


mainScreen()