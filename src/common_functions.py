import numpy as np
import pandas as pd
from pathlib import Path
import sys
import gender_guesser.detector as gender
import phonenumbers

pd.options.mode.chained_assignment = None  # default='warn'

def read_file_excel(file_name, path, sheet):
    return pd.read_excel(path / file_name, sheet_name=sheet)

def read_file_csv(file_name, path):
    return pd.read_csv(path / file_name, encoding='latin1')

def format_phone_number(df1, column_name):

    """  format phone number and check phone numbers """

    df = df1.copy()
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].map(lambda x: ''.join([i for i in x if i.isdigit()]))
    mask = df[column_name].str.len() != 10
    df.loc[mask, column_name] = np.nan
    df[column_name] = df[column_name].astype(str)
    df.loc[~mask, column_name] = df[column_name].apply(lambda x: f"{x[:3]}-{x[3:6]}-{x[6:]}")

    return df[column_name]

def clean_ps_parent_data(df):

    print(f"ps_data rows pre clean: {df.shape[0]}")

    # clean up Street

    # df['Unit'] = df['Unit'].astype(str)
    # df['Line Two'] = df['Line Two'].astype(str)
    #
    # print(df['Unit'].head())
    #
    df['Street'] = df['Street'].astype(str)
    #df['Street'] = df['Street'].str.capitalize()
    df['Street'] = df['Street'].map(lambda x: ' '.join([w.capitalize() for w in x.split()]))
    # capitilize only words in string that begin with letters


    mask = df['Unit'].notna()
    df.loc[mask, 'Street'] = df['Street'] + ", " + df['Unit'].astype(str)

    mask = df['Line Two'].notna()
    df.loc[mask, 'Street'] = df['Street'] + ", " + df['Line Two'].astype(str)










    df = df.rename(columns={'Contact ID': 'PS_Parents_Contact_ID',
                            'First Name': 'First_Name',
                            'Last Name *': 'Last_Name',
                            'Email Address': 'Email',
                            'Phone Number (As Entered)': 'Phone_Number',
                            'Phone Type': 'Phone_Type',
                            'Relationship Type': 'Relationship_Type',
                            'Student Number': 'Student_Number',
                            'Prefix': 'Prefix',
                            'Street': 'Street',
                            'City': 'City',
                            'State': 'State',
                            'Postal Code': 'Zip'
                        })

    df['Zip'] = df['Zip'].astype(str)

    # if zip is less than 5 digits add leading zeros
    mask = df['Zip'].str.len() < 5
    df.loc[mask, 'Zip'] = df['Zip'].apply(lambda x: x.zfill(5))


    df = df[['PS_Parents_Contact_ID', 'Prefix','First_Name', 'Last_Name', 'Email',
             'Phone_Number', 'Phone_Type', 'Relationship_Type', 'Student_Number', 'Street',
             'City', 'State', 'Zip']]

    df['Phone_Type'] = df['Phone_Type'].replace({'Mobile': 'Cell',
                                                  'Daytime': 'Business'})

    df['Phone_Type'] = df['Phone_Type'].str.title()

    # remove type for missing phone numbers
    mask = df['Phone_Number'].isna()
    df.loc[mask, 'Phone_Type'] = np.nan


    df = df.sort_values(['Last_Name', 'First_Name'])

    # filter for mother ot father
    mask = (df['Relationship_Type'] == 'Father') | (df['Relationship_Type'] == 'Mother')
    df = df[mask]

    # drop missing last name
    mask = df['Last_Name'].isna()
    df = df[~mask]


    df['Last_Name'] = df['Last_Name'].str.title()
    df['First_Name'] = df['First_Name'].str.title()
    df['Email'] = df['Email'].str.lower()


    # format phone number and check phone numbers
    df['Phone_Number'] = df['Phone_Number'].astype(str)
    df['Phone_Number'] = df['Phone_Number'].map(lambda x: ''.join([i for i in x if i.isdigit()]))
    mask = df['Phone_Number'].str.len() != 10
    df.loc[mask, 'Phone_Number'] = np.nan
    df['Phone_Number'] = df['Phone_Number'].astype(str)
    df.loc[~mask,'Phone_Number'] = df['Phone_Number'].apply(lambda x: f"{x[:3]}-{x[3:6]}-{x[6:]}")

    df = df.drop_duplicates(subset=['PS_Parents_Contact_ID'], keep='first')





    print(f"total rows: {df.shape[0]}")
    print(f"non duplicates rows: {df.shape[0]}")





    return df

def clean_re_rename_columns(df):

    df = df.rename(columns={'CnBio_ID': 'Constituent_ID',
                            'CnBio_First_Name': 'First_Name',
                            'CnBio_Nickname': 'Nickname',
                            'CnBio_Last_Name': 'Last_Name',
                            'CnPh_1_01_Phone_number': 'Phone_Number_1',
                            'CnPh_1_01_Phone_type': 'Phone_Number_Type_1',
                            'CnPh_1_02_Phone_number': 'Phone_Number_2',
                            'CnPh_1_02_Phone_type': 'Phone_Number_Type_2',
                            'CnAttrCat_1_01_Description': 'PS_Parents_Contact_ID'

                            })


    print(f"re_data rows: {df.shape[0]}")

    return df

def ps_format_street_address(df):

        df['Street'] = df['Street'].astype(str)
        df['Street'] = df['Street'].map(lambda x: ' '.join([w.capitalize() for w in x.split()]))
        mask = df['Unit'].notna()
        df.loc[mask, 'Street'] = df['Street'] + ", " + df['Unit'].astype(str)

        mask = df['Line Two'].notna()
        df.loc[mask, 'Street'] = df['Street'] + ", " + df['Line Two'].astype(str)

        return df