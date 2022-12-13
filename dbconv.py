import os, csv, sys, re, sqlite3, openpyxl as xl
from tabulate import tabulate

def conv_csv(n,temp):

    #CONVERSION TO EXCEL SECTION
    if n=='1':
        print('Converting to xlsx format(Excel). Just a moment, please.')
        with open(temp,'r') as csv_rf:
            csv_data=csv.reader(csv_rf)
            wb=xl.Workbook()
            sheet=wb.active
            i=1 #Row count
            for dr in csv_data: #j-data column, dr-data row
                for j in range(1,len(dr)+1):
                    sheet.cell(row=i, column=j).value=dr[j-1]
                i+=1
            pass
        new_file=temp.split('.')[0]+'.xlsx'
        wb.save(new_file)
        print(f'The file has been ported into Excel as {new_file}')
        return new_file

    #CONVERSION TO DATABASE SECTION
    if n=='2':
        print('Converting to Database Format(.db). Just a moment, please')

        #TABLE CREATION SECIION
        brr=temp.split('.')[0]
        filename=brr+'.db' #FILENAME
        table_name=brr.upper()+'_TABLE'
        create_query=f'CREATE TABLE {table_name}(' #AUTO CREATE TABLE NAME
        with open(temp,'r') as csv_rf:
            csv_data=csv.reader(csv_rf)
            #NEED FIRST 2 ROWS FOR COLUMN NAME(1) AND TYPE(2)
            count=0
            rowstore=[]
            for i in csv_data:
                rowstore.append(i)
                count+=1
                if count==2:
                    break
            count=0
            for i in range(len(rowstore[0])):
                jtype=' INTEGER, ' if rowstore[1][i].isdigit()==True else ' TEXT, '
                create_query+=rowstore[0][i]+jtype #Like Name TEXT or Age INTEGER
            create_query=create_query.strip(', ')
            create_query+=')'
            conn=sqlite3.connect(filename)
            c=conn.cursor()
            c.execute(create_query) #TABLE IS CREATED!
            pass

        with open(temp,'r') as csv_rf:
            csv_data=csv.reader(csv_rf)
            for i in csv_data:
                if count==0:
                    count+=1
                    continue
                c.execute(f'INSERT INTO {table_name}{tuple(rowstore[0])} VALUES{tuple(i)}')
            pass

        conn.commit()
        conn.close()
    return filename


def conv_txt(n,temp): #WIP

    with open(temp,'r') as txt_rf:
        rf=txt_rf.readlines()
        clean_rf=[rf[i].strip('\n').split(',') for i in range(len(rf))]
        pass

    #CONVERSION TO EXCEL
    if n=='1':
        print('Converting to xlsx format(Excel). Just a moment, please.')
        wb=xl.Workbook()
        sheet=wb.active
        i=1 #Row count
        for dr in (clean_rf):
            for j in range(1,len(dr)+1):
                sheet.cell(row=i,column=j).value=dr[j-1]
            i+=1
        new_file=temp.split('.')[0]+'.xlsx'
        wb.save(new_file)
        print(f'The file has been ported into Excel as {new_file}')
        return new_file

    #CONVERSION TO DATABASE SECTION
    if n=='2':
        print('Converting to Database Format(.db). Just a moment, please')

        #TABLE CREATION SECIION
        filename=temp.split('.')[0]+'.db'
        table_name=temp.split('.')[0].upper()+'_TABLE'
        create_query=f'CREATE TABLE {table_name}('
        #clean_rf is the data to be formatted into db
        for i in range(len(clean_rf[0])):
            dtype=' INTEGER,' if clean_rf[1][i].isdigit() else ' TEXT,'
            create_query+=clean_rf[0][i]+dtype
        create_query=create_query.strip(', ')
        create_query+=')'
        conn=sqlite3.connect(filename)
        c=conn.cursor()
        c.execute(create_query) #TABLE IS CREATED!

        count=0
        for i in clean_rf:
            ins_query=f'INSERT INTO {table_name}{tuple(clean_rf[0])} VALUES {tuple(i)}'
            c.execute(ins_query)
        conn.commit()
        conn.close()
        return filename


def conv_xlsx(temp):
    wb=xl.load_workbook(temp)
    sheet=wb.active
    file=temp.split('.')[0]
    file_name=file+'.db'
    table_name=file.upper()+'_TABLE'
    
    #TABLE CREATE QUERY SECTION
    create_query=f'CREATE TABLE {table_name}('
    for i in range(1, sheet.max_column+1):
        create_query+=str(sheet.cell(row=1,column=i).value)
        jtype=' INTEGER, ' if str(sheet.cell(row=2,column=i).value).isdigit()==True else ' TEXT, '
        create_query+=jtype
    create_query=create_query.strip(', ')
    create_query+=')'
    conn=sqlite3.connect(file_name)
    c=conn.cursor()
    c.execute(create_query)

    col_tup=tuple(str(sheet.cell(row=1,column=i).value) for i in range(1,sheet.max_column+1))
    for i in range(2,sheet.max_row+1):
        val_tup=tuple(str(sheet.cell(row=i,column=j).value) for j in range(1,sheet.max_column+1))
        insert_query=f'INSERT INTO {table_name}{col_tup} VALUES{val_tup}'
        c.execute(insert_query)
    conn.commit()
    conn.close()
    return file_name 


def db_operations(db_name):

    while 1:
        print('''\nDB Operations:
1.  View all
2.  Make new entry
3.  Filtered view
4.  Update
5.  Delete
6.  Exit
7.  Clear Screen
        ''')
        op=input('Enter operation number: ')
        print('')

        if op=='6':
            break
        if op=='7':
            os.system('cls')
        conn=sqlite3.connect(db_name)
        c=conn.cursor()
        c.execute("SELECT * FROM sqlite_master WHERE type=='table'")
        table_name=c.fetchone()[1] #GET Tablename
        c.execute("SELECT * FROM sqlite_master")
        brr=str(c.fetchall()) 
        head=re.findall(r'(\w+)\s(?:INTEGER|TEXT)',brr) #GET column names from the table
        ops=['==','>=','<=']

        if op=='1':
            view_all=f'SELECT * FROM {table_name}'
            c.execute(view_all)
            table=c.fetchall()
            print(tabulate(table, headers=head))
            continue

        elif op=='2':
            names=tuple(head)

            print(f'\nKeep entering new values in the proper format:{names}, apostrophes optional. Hit enter to stop.')
            while 1:
                try:
                    new_val=input('Enter values, separated by a comma, apostrope optional:\n')
                    new_val_lis=str(tuple(new_val.split(',')))
                    if not new_val:
                        break
                    insert_que=f'INSERT INTO {table_name}{names} VALUES{new_val_lis}'
                    c.execute(insert_que)
                    conn.commit()
                except:
                    print('Data entered in an invalid format. Please enter data in the correct format')
                    continue
            continue

        elif op=='3':
            while 1:
                print(*(str(i)+'. '+head[i-1] for i in range(1,len(head)+1)),sep='\n')
                a=int(input('Enter column: '))
                if not 0<a<=len(head):
                    print('Error')
                    continue
                print(*(str(i)+'. '+ops[i-1] for i in range(1,len(ops)+1)),sep='\n')
                b=int(input('Enter operation: '))
                if b not in [1,2,3]:
                    print('Error')
                    continue
                cons=input('Enter comparison constant: ').title()
                print('')

                filt_view=f"SELECT * FROM {table_name} WHERE {head[a-1]}{ops[b-1]}{cons}" if cons.isdigit()==True else f"SELECT * FROM {table_name} WHERE {head[a-1]}{ops[b-1]}"+f"'{cons}'"

                c.execute(filt_view)
                table=c.fetchall()
                print(tabulate(table, headers=head))
                break
        
        elif op=='4':
            #UPDATE Artists SET ArtistName = 'EUROBEAT' where ArtistId = 1;
            print(*(head[i-1] for i in range(1,len(head)+1)),sep=', ')
            while 1:
                try:
                    updt=input('\nEnter the values in the format: <new_assignment>,<condition>. To exit, just hit enter:\n')
                    if not updt:
                        break
                    brr=updt.split(',')
                    brr1_e,brr2_e=brr[0],brr[1]

                    brr1=brr[0].split('=')
                    if brr1[1].isdigit()!=True:
                        brr1_e=brr1[0].title()+'='+'\''+f'{brr1[1].title()}'+'\''

                    brr2=brr[1].split('=')
                    if brr2[1].isdigit()!=True:
                        brr2_e=brr2[0].title()+'='+'\''+f'{brr2[1].title()}'+'\''

                    update_table=f'UPDATE {table_name} SET {brr1_e} WHERE {brr2_e}'
                    c.execute(update_table)
                    conn.commit()
                except:
                    continue
                
        elif op=='5':
            while 1:
                print('''
1.  Delete all
2.  Filtered deletion
3.  Exit
                ''')
                del_op=int(input('Enter delete option:'))
                if del_op not in [1,2,3]:
                    print('Error')
                    continue
                if del_op==1:
                    del_all=f'DELETE FROM {table_name}'
                    c.execute(del_all)
                    conn.commit()
                elif del_op==2:
                    while 1:
                        cond=input('Enter the condition: ')
                        if not cond:
                            break
                        cond_e=cond.split('=')
                        if not cond_e[1].isdigit():
                            cond=cond_e[0]+'='+'\''+f'{cond_e[1]}'+'\''

                        del_sel=f'DELETE FROM {table_name} WHERE {cond}'
                        c.execute(del_sel)
                        conn.commit()
                elif del_op==3:
                    break

        conn.commit()
        conn.close()


def main():
    while 1:
        print(os.getcwd())
        print('\n Firing up Database Converter/Editor...\n')

        #INPUT VALIDATION SECTION
        while 1:
            file=input('Please enter the file name or the folder path: ')
            if '/' in file or '\\' in file:

                try:
                    os.chdir(file)
                    #REMOVE THE NEXT THREE LINES BEFORE FINAL PRESENTATION
                    for i in os.listdir():
                        if '.db' in i:
                            os.remove(i)
                except:
                    sys.exit('The specified path is either mistaken or does not exist')

                file_list=[]
                for i in os.listdir():
                    if '.csv' in i or '.xlsx' in i or '.db' in i or '.txt' in i:
                        file_list.append(i)

                if len(file_list)==1:
                    temp=file_list[0]
                elif len(file_list)==0:
                    print('No files in the accepted formats present in the user specified folder path')
                    temp=0
                    break
                else:
                    print('\nWhich file is to be edited?')
                    print(*(str(i+1)+' '+file_list[i] for i in range(len(file_list))),sep='\n')
                    choice=int(input('\nEnter file number: '))
                    temp=file_list[choice-1]
                break

            else:
                if file not in os.listdir(os.getcwd()):
                    print('Specified file does not exist. Please enter valid file or filepath.')
                    continue
                temp=file
                break

        #FILE IDENTIFICATION SECTION
        if temp==0:
            break

        if '.csv' in temp:
            print('CSV file was detected.')
            file=conv_csv(input('Enter corresponding number to choose conversion type:\n1: .xlsx\n2: .db'),temp)
            print(f'{file} was generated')
            adv=input('Is there anything else to do? Hit y/Y if yes, and just hti enter if not\n')
            if not adv:
                sys.exit('Exiting...')

        elif '.txt' in temp: #Basically CSV's, but in a text file instead of csv format
            print('tct file detected.')
            file=conv_txt(input('Enter corresponding number to choose conversion type:\n1: .xlsx\n2: .db'),temp)
            print(f'{file} was generated')
            adv=input('Is there anything else to do? Hit y/Y if yes, and just hti enter if not\n')
            if not adv:
                sys.exit('Exiting...')

        
        elif '.xlsx' in temp:
            print('Excel file was detected. Converting to .db, please wait a moment')
            file=conv_xlsx(temp)
            print(f'{file} was generated')
        
        if '.db' in temp:
            print('Database format file was detected.')
            file=temp

        if '.db' in file:
            db_op=input('Perform Database operation? Enter any value if yes, hit enter if no.\n')
            if db_op:
                db_operations(file) #CALLS db_operatons and sends it the name of the file
            cont=input('Any other conversion operations to occur? Hit enter if no, y/Y if yes: ')
            if not cont:
                break
            if cont:
                continue    

if __name__=='__main__':
    main()
    input('Hit Enter to clear screen')
    os.system('cls')
