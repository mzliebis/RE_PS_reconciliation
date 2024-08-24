import pandas as pd
from pathlib import Path
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'


def read_file_excel(file_name, path, sheet):
    return pd.read_excel(path / file_name, sheet_name=sheet)


def read_file_csv(file_name, path):
    return pd.read_csv(path / file_name, encoding='latin1')

def format_ps_students(df):

    df = df.rename(columns={'Student_Number': 'PS_Student_ID',
                            'First_Name': 'First_Name',
                            'Last_Name': 'Last_Name',
                            'Cell_Phone': 'Cell',
                            'email': 'Email',
                            'ClassOf': 'Class_Of' })

    print(df.info())

    df['Cell'] = df['Cell'].astype(str)

    df['Email'] = df['Email'].str.lower()

    df = df.drop_duplicates(subset=['PS_Student_ID'], keep='first')

    df['Class_Of'] = df['Class_Of'].subtract(2000).astype(int)


    df = df[['PS_Student_ID', 'First_Name', 'Last_Name', 'Cell', 'Email', 'Class_Of']]

    return df

def format_re_students(df):

        df = df.rename(columns={'CnBio_ID': 'Const_ID',
                                'CnBio_First_Name': 'First_Name',
                                'CnBio_Last_Name': 'Last_Name',
                                'CnBio_Import_ID': 'Import_ID',
                                'CnPh_1_01_Phone_number': 'Email',
                                'CnAttrCat_1_01_Description': 'PS_Student_ID'})

        mask = df['PS_Student_ID'].isna()
        df = df[mask]

        df = df[['Const_ID', 'First_Name', 'Last_Name', 'Import_ID', 'Email']]

        return df

def format_for_re_upload(df):

    df = df.rename(columns={'PS_Student_ID': 'CattrDesc',
                            'Const_ID': 'ConstID'})

    mask = df['CattrDesc'].isna()
    df = df[~mask]

    df['CattrDesc'] = df['CattrDesc'].astype(int)


    df['CattrCat'] = "power_school_student_id"

    df = df[['ConstID', 'CattrCat',  'CattrDesc']]

    mask = df['CattrDesc'].isna()
    df = df[~mask]


    return df


if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    class_of = 27
    ps_students = read_file_excel("PS_data.xlsx", path_data, "Students")
    re = read_file_csv("cs_ps_id_missing.CSV", path_data)

    print(re.to_markdown())




    ps_students = format_ps_students(ps_students)
    #
    # mask = ps_students['Class_Of'] == class_of
    # ps_students = ps_students[mask]
    # number_of_ps_students = ps_students.shape[0]



    # fn_re_students = "re_cs_class_of_" +str(class_of) + ".csv"
    #
    # re_students = read_file_csv(fn_re_students, path_data)
    # number_of_re_students = re_students.shape[0]
    # re_students = format_re_students(re_students)
    #
    # students = re_students.merge(ps_students, how= 'left', left_on= ['First_Name', 'Last_Name'], right_on=['First_Name', 'Last_Name'])
    #
    # upload_students_ps_id = format_for_re_upload(students)
    #
    # fn_upload = "upload_students_ps_id_class_" + str(class_of) + ".csv"
    # upload_students_ps_id.to_csv(path_out / fn_upload, index=False)
    #
    #
    #
    # print(upload_students_ps_id.to_markdown())
    #
    # print(f"Number of PS students: {number_of_ps_students}")
    # print(f"Number of RE students: {number_of_re_students}")
    # print(f"Number of uploaded students: {upload_students_ps_id.shape[0]}")






