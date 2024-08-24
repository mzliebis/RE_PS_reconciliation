import pandas as pd
from pathlib import Path
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

def read_file_excel(file_name, path, sheet):
    return pd.read_excel(path / file_name, sheet_name=sheet)

def read_file_csv(file_name, path):
    return pd.read_csv(path / file_name, encoding='latin1')

def format_for_re_upload(df):

    df = df.rename(columns={'Import_ID':'ImportID',
                            'Spouse_Import_ID':'IRLink'
                            })


    df['IRRelat'] = "Spouse"
    df['IRRecip'] = "Spouse"
    df['IRIsSpouse'] = "Yes"


    df = df[['ImportID','IRLink','IRRelat', 'IRRecip', 'IRIsSpouse']]

    return df

def format_parents(df):

    # only want married parents
    mask = df['Parental_Status'] == 'Married'
    df = df[mask]

    # sort so fathers are first
    df = df.sort_values(by=['Relationship_Type'])


    # fix problem with scientific notation
    df['PS_Parents_Contact_ID'] = df['PS_Parents_Contact_ID'].astype(int)

    # remove columns
    df = df[['PS_Parents_Contact_ID', 'Relationship_Type', 'First_Name', 'Last_Name', 'Spouse_First_Name', 'Spouse_Last_Name']]

    return df

#def remove_duplicate_spouse_relationship(df):
def add_const_and_import_ids(df, re):


    temp = re.copy()
    temp = temp[['PS_Parents_Contact_ID', 'Const_ID', 'Import_ID']]

    df = df.merge(temp, how='left', left_on=['PS_Parents_Contact_ID'], right_on=['PS_Parents_Contact_ID'])

    return df

def format_re_parents(df):
    df = df.rename(columns={'CnBio_ID': 'Const_ID',
                            'CnBio_First_Name': 'First_Name',
                            'CnBio_Last_Name': 'Last_Name',
                            'CnBio_Import_ID': 'Import_ID',
                            'CnAttrCat_1_01_Description': 'PS_Parents_Contact_ID'})


    df = df[['Const_ID', 'First_Name', 'Last_Name', 'Import_ID', 'PS_Parents_Contact_ID']]

    # remove parents without contact ids:
    mask = df['PS_Parents_Contact_ID'].notna()
    df = df[mask]

    # format ps contact id
    df['PS_Parents_Contact_ID'] = df['PS_Parents_Contact_ID'].astype(int)

    return df

def add_spouse_const_and_import_ids(df, re):

        temp = re.copy()
        temp = temp.rename(columns={'Const_ID': 'Spouse_Const_ID',
                                    'Import_ID': 'Spouse_Import_ID',
                                    'First_Name': 'Spouse_First_Name',
                                    'Last_Name': 'Spouse_Last_Name'})

        temp = temp[['Spouse_First_Name', 'Spouse_Last_Name', 'Spouse_Const_ID', 'Spouse_Import_ID']]

        df = df.merge(temp, how='left', left_on=['Spouse_First_Name', 'Spouse_Last_Name'], right_on=['Spouse_First_Name', 'Spouse_Last_Name'])

        return df

def remove_duplicate_spouse_relationship(df):
    """removes duplicate spouse relationships"""

    mask = df['First_Name'].isna()
    df = df[~mask]

    # find if Const_ID is in Spouse_Const_ID for any prior rows
    mask = df.apply(lambda row: ((df[df['Const_ID'] == row['Spouse_Const_ID']].index > row.name))[0], axis=1)

    df = df[mask]

    return df

def clean_upload_spouse_file(df):
    """cleans up the upload file and remove dupilcate relationships"""

    mask = df['ImportID'].isna() | df['IRLink'].isna()
    df = df[~mask]

    # find index of first instance of Import ID in IRLink

    temp_1 = df[['ImportID','IRLink']].max(axis=1)
    temp_2 = df[['ImportID','IRLink']].min(axis=1)

    df['ImportID'] = temp_1
    df['IRLink'] = temp_2
    #df.apply(lambda row: print(max([row['ImportID'],row['IRLink']]), axis=1)

    df.drop_duplicates(subset=['ImportID', 'IRLink'], keep='first', inplace=True)

    return df


if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")


    parents = read_file_csv("re_np_class_28_raw.csv", path_out)
    parents = format_parents(parents)

    re_parents = read_file_csv("RE_current_parents.csv", path_data)
    re_parents = format_re_parents(re_parents)

    parents = add_const_and_import_ids(parents, re_parents)
    parents = add_spouse_const_and_import_ids(parents, re_parents)

    print(parents.to_markdown())

    #parents = remove_duplicate_spouse_relationship(parents)

    upload_spouse_file = format_for_re_upload(parents)

    upload_spouse_file = clean_upload_spouse_file(upload_spouse_file)



    #print(parents.to_markdown())

    upload_spouse_file.to_csv(path_out / "upload_spouse_relationship_28.csv", index=False)
    #print(temp.to_markdown())
    print(upload_spouse_file.to_markdown())