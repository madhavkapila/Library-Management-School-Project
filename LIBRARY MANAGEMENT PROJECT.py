import pandas as pd 
import mysql.connector as sqlctr
import sys
from datetime import datetime
mycon = sqlctr.connect(host='localhost', user='root', password='<password>')
if mycon.is_connected():
    print('\n')
    print('Successfully connected to localhost')
else:
    print('Error while connecting to localhost')
cursor = mycon.cursor()

#creating database
cursor.execute("CREATE DATABASE IF NOT EXISTS LIBRARY_MANAGEMENT_SYSTEM")
cursor.execute("USE LIBRARY_MANAGEMENT_SYSTEM")

#creating the tables we need

cursor.execute("CREATE TABLE IF NOT EXISTS BOOKS(SN int(5) PRIMARY KEY,BOOK_NAME VARCHAR(100), QUANTITY_AVAILABLE INT(10),PRICE_PER_DAY INT(10))")
cursor.execute("CREATE TABLE IF NOT EXISTS BORROWER(SN INT(5), I_NAME VARCHAR(50), BOOK_LENT VARCHAR(100), DATE_LENT date , CONTACT_NO INT(10))")


def command(cmd):  #To execute any SQL query
    cursor.execute(cmd)



def fetch():      #To fetch and print data from database
    data = cursor.fetchall()
    for i in data:
        print(i)



def all_data(tname):   #To get all details of any table of the database
    List = []
    cmd = 'DESCRIBE '+tname
    command(cmd)
    data = cursor.fetchall()
    for i in data:
        List.append(i[0])
    cmd = 'SELECT * FROM '+tname
    command(cmd)
    print('\n')
    print('-------ALL_DATA_FROM_TABLE_'+tname+'_ARE-------\n')
    print(tuple(List))
    tup=cursor.fetchall()
    print(tup)




def detail_borrower(name,contact):    #To print details for a particular borrower
    tup=('SN',"Borrower's Name",'Book_Lent','Date','Contact Number')
    print('\n---Details for borrower '+name+'---\n')
    print(tup)
    cmd  = 'SELECT * FROM BORROWER WHERE I_NAME LIKE "{}" AND CONTACT_NO = {}'.format(name,contact)
    command(cmd)
    fetch()



def days_between(d1, d2):      #To calculate days for which a specific book is lent
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    global days
    days = abs((d2 - d1).days)





def price_book(days,book_name):     #To calculate price to be paid by the borrower when a book is lent for specific no. of days
    cmd = 'SELECT PRICE_PER_DAY FROM BOOKS WHERE BOOK_NAME = "{}"'.format(book_name)
    command(cmd)
    data = cursor.fetchall()
    for i in data:
        global total_price
        total_price = int(i[0]) * days
        print('No. of days {} book is kept : {}'.format(book_name,days))
        print('Price per day for book {} is Rs.{}'.format(book_name,i[0]))
        print('Total fare for book '+book_name +' is',total_price)




def lend():
    flag='True'   #label or checkpoint or button to start/stop following loop
    while flag == 'True':
        print('\n___AVAILABLE BOOKS___\n')
        q0 = 'SELECT BOOK_NAME FROM BOOKS WHERE QUANTITY_AVAILABLE>=1'
        command(q0)
        fetch()
        q1='SELECT MAX(SN) FROM BORROWER' #To find latest serial_num from borrower's table to assign next SN
        command(q1)
        data_sn=cursor.fetchall()
        for i in data_sn:
            prev_index = i[0]
            if not prev_index:
                prev_index = 0
            SN=prev_index+1        
        book_selected=str(input('Enter name of book from above list : '))
        borrowers_name=str(input('Enter Borrower Name : '))
        date=str(input('Enter date (YYYY-MM-DD) : '))
        contact=int(input('Enter contact no. : '))
        q_insert='INSERT INTO BORROWER VALUES({},"{}","{}","{}",{})'.format(SN,borrowers_name,book_selected,date,contact)
        command(q_insert)
        command('COMMIT')
        q_quantity='SELECT QUANTITY_AVAILABLE FROM BOOKS WHERE BOOK_NAME="{}"'.format(book_selected)
        command(q_quantity)
        data_quantity = cursor.fetchall()
        for qty in data_quantity:
            quantity=qty[0]-1
        qty_dec='UPDATE BOOKS   SET QUANTITY_AVAILABLE = {}   WHERE BOOK_NAME = "{}"'.format(quantity,book_selected)
        command(qty_dec)
        dec=str(input('Do you want to add more records (Y/N) : '))
        if dec.upper == "Y":
            flag= 'True'
        else:
            flag='False'
        

def borrowers():        #To work upon Borrower table
    print('\n\n___OPTIONS AVAILABLE___\n\nEnter 1 : To Show detail of all borrowers \nEnter 2 : To check detail of a particular borrower \nEnter 3 : To calculate total fine of a borrower \nEnter 4 : To go Back \nEnter 5 : To commit all the changes and exit')
    dec = input('enter your choice-')
    if dec == '1':
        all_data('BORROWER')
    elif dec=='2':
        name = str(input('\nenter borrower name-'))
        contact = str(input('enter borrower contact no.-'))
        detail_borrower(name,contact)
    elif dec=='3':
        tfine()
    elif dec=='4':
        action_list()
    elif dec=='5':
        close()
    borrowers()




def tfine():       #To calculate and find price to be paid by a borrower
    name=str(input('\nEnter borrower name : '))
    contact=input('Enter borrower contact_no : ')        
    detail_borrower(name, contact)
    q1 = 'SELECT BOOK_LENT FROM BORROWER WHERE I_NAME = "{}" AND CONTACT_NO = {}'.format(name,contact)
    command(q1)
    data=cursor.fetchall()
    for i in data:
        book_name=i[0]
        q2 = 'SELECT DATE_LENT   FROM BORROWER   WHERE I_NAME = "{}" AND  BOOK_LENT = "{}"'.format(name,book_name)
        command(q2)
        data1=cursor.fetchall()
        for date in data1:
            date_taken=date[0]
            date_return = str(input('\nEnter returning date for book "{}" (YYYY-MM-DD) , Press ENTER to skip-'.format(book_name)))
            while date_return!='':
                days_between(str(date_return),str(date_taken))
                price_book(days,i[0])
                print('\nEnter Y : If Rs.{} is paid and book is returned.\nEnter N : If fare is not paid and book is not returned.'.format(total_price))
                dec=str(input('Enter (Y?N) : ')) 
                if dec.upper()=="Y":
                    q= 'SELECT SN , QUANTITY_AVAILABLE FROM BOOKS WHERE BOOK_NAME = "{}"'.format(i[0])
                    command(q)
                    data2 = cursor.fetchall()
                    for price in data2:
                        update('books', 'Quantity_Available',price[1]+1,price[0])
                    st_del = 'DELETE FROM BORROWER WHERE I_NAME = "{}" AND BOOK_LENT = "{}"'.format(name,book_name)
                    command(st_del)
                    break
                else:
                    print("\n\nPLEASE PAY THE FARE AND RETURN BOOK AFTER READING.\n\n")
                    break
        

def insert():       #To insert new tuples in the relation 'BOOKS'
    flag = 'true'
    while flag=='true':
        li_col_name=[]
        li=[]
        li_values=[]
        command('DESCRIBE BOOKS')
        data=cursor.fetchall()
        for i in data:
            li_col_name.append(i[0])   #To store column headings in a list
        command('SELECT MAX(SN) FROM BOOKS')
        dta=cursor.fetchall()
        for j in dta:
            prev_index = j[0]
            if not prev_index:
                prev_index = 0
            li_values.append(prev_index+1)   #To add Serial no.
        for k in range(1,4):
            val = str(input('Enter '+li_col_name[k]+'-'))
            li_values.append(val)
        li.append(tuple(li_values))
        values = ', '.join(map(str, li))
        q1 = "INSERT INTO books VALUES {}".format(values)
        command(q1)
        command('COMMIT')
        all_data('BOOKS')
        print('\n')
        print("\nDATA INSERTED SUCCESSFULLY\n")
        dec = str(input('Do u want to insert more data?(Y/N)-'))
        if dec.upper() == "Y":
            flag='true'
        else:
            flag='false' 
    action_list()



    

def update(tname,collumn,post_value,pre_value):  #To update tuples in the given table
    cmd = str('update %s set %s=%s where SN=%s') % (tname, collumn, "'%s'", "'%s'") % (post_value, pre_value)
    command(cmd)
    command('COMMIT')
    all_data(tname)
    print('\nVALUE UPDATED SUCCESSFULLY')
     

def close():                                    #To close LIBRARY MANAGEMENT SYSTEM
    mycon.commit()
    mycon.close()
    if mycon.is_connected():
        print('still connected to localhost')
    else:
        print('\n\nconnection closed successfully.')
    sys.exit()


def action_list():                              #Home or welcome page ccepting requests/input fom user of LIBRARY MANAGEMENT SYSTEM
    print('\n')
    print('#### WELCOME TO LIBRARY MANAGEMENT SYSTEM ####\n\nEnter 1 : To View details of all available Books\nEnter 2 : To check detail of a particular book\nEnter 3 : To lend a book \nEnter 4 : To add new books in list \nEnter 5 : To update data \nEnter 6 : To view details of borrowers \nEnter 7 : To commit all changes and exit')
    dec = input('\nEnter your choice-')
    if dec == '1':
        all_data('BOOKS')
    elif dec=='2':
        tup=('SN','Book_Name','Quantity_Available','Price_Per_Day')
        tup1 = ('SN', 'borrowers_name', 'book_lent', 'contact_no')
        in1=str(input('enter first name , last name or middle name of a book-'))
        print('\n___ALL DATA OF BOOKS HAVING "{}" IN THEIR NAME FROM BOTH TABLE____'.format(in1))
        q1 =str('SELECT * FROM BOOKS WHERE BOOK_NAME LIKE "{}"'.format('%'+in1+'%'))
        q2=str('SELECT * FROM BORROWER WHERE BOOK_LENT LIKE "{}"'.format('%'+in1+'%'))
        print('\n__DATA FROM TABLE BOOKS__\n')
        command(q1)
        print(tup)
        fetch()
        print('\n__DATA FROM TABLE BORROWER__\n')
        command(q2)
        print(tup1)
        fetch()
        print()
    elif dec == '3':
        lend()
    elif dec=='4':
        insert()
    elif dec=='5':
        flag='true'
        while flag=='true':
            tname = 'BOOKS'
            li = []
            q1 = 'desc '+tname
            command(q1)
            data1 = cursor.fetchall()
            for i in data1:
                li.append(i[0])
            all_data(tname)
            print('\n columns in table '+tname+' are')
            print(li)
            column = str(input('enter column name for modification from above list-'))
            li_po = ['SN']
            li_po.append(column)
            print(tuple(li_po))
            q0 = 'SELECT SN, %s FROM BOOKS' % (column)
            command(q0)
            fetch()
            pre_value = str(input('enter corresponding SN for the data to be changed-'))
            post_value = str(input('enter new value for column %s having SN %s-' % (column, pre_value)))
            update(tname, column, post_value, pre_value)
            dec = str(input('Do you want to change more data?(Y/N)-'))
            if dec == 'y' or dec == 'Y':
                flag='true'            
            else:
                flag='false'
        
    elif dec=='6':
        borrowers()
    elif dec=='7':
        close()
    action_list()



action_list()
