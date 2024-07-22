import tabula
import pandas as pd
import numpy as np 

def getStatusWeight(status):
    if status == "Issued":
        return 1
    elif status == "Ready for RO":
        return 2
    elif status == "Region Incomplete":
        return 3
    elif status == "Not Submitted":
        return 4
    elif status == "Quote Only":
        return 5
    else:
        print("Status not found: " + str(status))
        return 6

#transform pdf to csv

file = "feli.pdf"

pdfdata= tabula.read_pdf(file,pages="all")

output = tabula.convert_into(file, "feli.csv", pages=[1,2])

#read csv with pandas
feli = pd.read_csv("feli.csv")
diana = pd.read_csv("DIANA.csv")
mera = pd.read_csv("MERA.csv")

#Add extra column 

feli['Alias'] = 'VAGH'

#merge multiple data frames

df = pd.merge(feli, diana, how ='outer')
df = pd.merge(df, mera, how ='outer')

#clean, sanitaze and delete duplicates

previousRow = None

df = df.reset_index() 
for index, row in df.iterrows():

    if index == 0:
        previousRow = row
        continue
    
    if previousRow['Customer Name'] == row['Customer Name']:

        if(getStatusWeight(previousRow['Status']) == getStatusWeight(row['Status'])):
            continue

        if getStatusWeight(previousRow['Status']) < getStatusWeight(row['Status']):
            df.drop(index=row['index'], inplace=True)
            continue
        else:
            df.drop(index=previousRow['index'], inplace=True)

    previousRow = row

df = df.drop(columns=["index", "Acct/App/Quote #", "Date Created"])
df = df.drop_duplicates()

print(df.head(5))

#pivot table for analysis

def sold(status):
    if status == "Issued" or status == "Ready for RO":
        return 1
    else:
        return 0
    
df["Policy sold"]= df["Status"].apply(sold)

pivot_table= pd.pivot_table (df, values = ['Status', 'Policy sold'], index=['Alias'], aggfunc={ 'Status': "count", 'Policy sold' :"sum"})

pivot_table['ratio'] = pivot_table['Status'] / pivot_table['Policy sold']

pivot_table = pivot_table.rename(columns={'Status': 'Quotes Provided'})

final_pd = np.round(pivot_table,2)

print(final_pd)




 