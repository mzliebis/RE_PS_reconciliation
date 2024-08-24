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
                            'Student_Import_ID':'IRLink'
                            })

    df['IRRelat'] = "Son"
    df['IRRecip'] = "Parent"


    df = df[['ImportID','IRLink','IRRelat', 'IRRecip']]

    mask = df['IRLink'].notna() & df['ImportID'].notna()
    df = df[mask]

    return df


def format_parents(df):
    df = df.rename(columns={'Student_Number': 'PS_Student_ID'})

    #df = df[['PS_Parents_Contact_ID', 'First_Name', 'Last_Name', 'Spouse_First_Name', 'Spouse_Last_Name']]
    df['PS_Parents_Contact_ID'] = df['PS_Parents_Contact_ID'].astype(int)
    return df


def format_re_students(df):

    df = df.rename(columns={'CnBio_ID': 'Student_Const_ID',
                            'CnBio_First_Name': 'Student_First_Name',
                            'CnBio_Last_Name': 'Student_Last_Name',
                            'CnBio_Import_ID': 'Student_Import_ID',
                            'CnPh_1_01_Phone_number': 'Student_Cell',
                            'CnAttrCat_1_01_Description': 'PS_Student_ID'})

    return df


def format_ps_students(df):

    df = df[['Student_Number', 'First_Name', 'Last_Name', 'Cell_Phone']]

    df = df.rename(columns={'Student_Number': 'PS_Student_ID',
                            'First_Name': 'Student_First_Name',
                            'Last_Name': 'Student_Last_Name',
                            'Cell_Phone': 'Student_Cell'})

    return df


def format_re_parents(df):
    df = df.rename(columns={'CnBio_ID': 'Const_ID',
                            'CnBio_Import_ID': 'Import_ID',
                            'CnAttrCat_1_01_Description': 'PS_Parents_Contact_ID'})

    mask = df['PS_Parents_Contact_ID'].notna()
    df = df[mask]
    df['PS_Parents_Contact_ID'] = df['PS_Parents_Contact_ID'].astype(int)

    return df

if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    class_of = "26"

    fn = "re_np_class_" + class_of + "_raw.csv"
    parents = read_file_csv(fn, path_out)
    number_of_new_parents = parents.shape[0]
    parents = format_parents(parents)

    re_parents = read_file_csv("RE_current_parents_4.csv", path_data)
    re_parents = format_re_parents(re_parents)


    parents = parents.merge(re_parents, how='left', left_on='PS_Parents_Contact_ID', right_on='PS_Parents_Contact_ID')

    #print(parents.head(5).to_markdown())
    ps_students = read_file_excel("PS_data.xlsx", path_data, "Students")
    ps_students = format_ps_students(ps_students)


    parents = parents.merge(ps_students, how='left', left_on='PS_Student_ID', right_on='PS_Student_ID')

    re_students = read_file_csv("re_cs_class_of_26.CSV", path_data)
    re_students = format_re_students(re_students)

    parents = parents.merge(re_students, how='left', left_on=['PS_Student_ID'],
                            right_on=['PS_Student_ID'])

    print(parents.head(100).to_markdown())

    upload_parent_son_file = format_for_re_upload(parents)

   # print(upload_parent_son_file.to_markdown())
    number_of_uploaded_relationships = upload_parent_son_file.shape[0]

    upload_parent_son_file.to_csv(path_out / "upload_parent_son_relationship_25.csv", index=False)
    print(upload_parent_son_file.head(100).to_markdown())

    print(f"Number of new parents: {number_of_new_parents}")
    print(f"Number of uploaded relationships: {number_of_uploaded_relationships}")


