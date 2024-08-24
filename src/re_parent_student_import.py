import numpy as np

from common_functions import *
pd.options.mode.chained_assignment = None  # default='warn'
pd.options.display.float_format = '{:.0f}'.format


def format_for_re_upload(df):

    df = df.rename(columns={'Import_ID':'ImportID',
                            'Student_Import_ID':'IRLink'
                            })

    df['IRImpID'] = np.nan
    df['IRRelat'] = "Son"
    df['IRRecip'] = "Parent"
    df['IRIsSpouse'] = np.nan

    df = df[['ImportID','IRLink', 'IRImpID','IRRelat', 'IRRecip', 'IRIsSpouse']]

    return df


def format_parents(df):
    df = df.rename(columns={'Student_Number': 'PS_Student_ID',
                            'CnBio_Import_ID': 'Parent_Import_ID'})

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

    parents = read_file_csv("np_no_son.CSV", path_data)
    students = read_file_csv("RE_students_ps.CSV", path_data)

    mask = parents['CnAttrCat_1_01_Description'].isna()
    parents = parents[~mask]
    parents['CnAttrCat_1_01_Description'] = parents['CnAttrCat_1_01_Description'].astype(int)

    parents = parents.rename(columns={'CnAttrCat_1_01_Description': 'PS_Parents_ID',
                                      'CnBio_Import_ID': 'Parent_Import_ID'})

    ps_parents = read_file_excel("PS_data.xlsx", path_data, "Parents")
    ps_parents = ps_parents[['Contact ID','Student Number']]

    ps_parents = ps_parents.dropna()

    ps_parents = ps_parents.astype(int)

    ps_parents = ps_parents.rename(columns={'Contact ID': 'PS_Parents_ID',
                                   'Student Number': 'PS_Student_ID'})

    students = students.rename(columns={'CnBio_Import_ID': 'Student_Import_ID',
                                        'CnAttrCat_1_01_Description': 'PS_Student_ID'})

    parents = ps_parents.merge(parents, how='inner', left_on='PS_Parents_ID', right_on='PS_Parents_ID')

    temp = parents.merge(students, how='inner', left_on='PS_Student_ID', right_on='PS_Student_ID')

    #print(temp.to_markdown(floatfmt='.0f'))

    temp = temp[['Parent_Import_ID','Student_Import_ID']]

    temp = temp.rename(columns={'Parent_Import_ID': 'ImportID',
                                'Student_Import_ID': 'IRLink'})

    temp['IRImpID'] =np.nan
    temp['IRRelat'] = "Son"
    temp['IRRecip'] = "Parent"
    temp['IRIsSpouse'] = np.nan




    print(temp.to_markdown(floatfmt='.0f'))

    temp.to_csv(path_out / "upload_parent_son_relationship_07_24_2024.csv", index=False)



    #parents = format_parents(parents)

    # re_parents = read_file_csv("RE_current_parents_2.csv", path_data)
    # re_parents = format_re_parents(re_parents)
    #
    # #print(parents.head(5).to_markdown())
    # #print(re_parents.head(5).to_markdown())
    #
    #
    #
    # parents = parents.merge(re_parents, how='left', left_on='PS_Parents_Contact_ID', right_on='PS_Parents_Contact_ID')
    #
    # #print(parents.head(5).to_markdown())
    # ps_students = read_file_excel("PS_data.xlsx", path_data, "Students")
    # ps_students = format_ps_students(ps_students)
    #
    #
    #
    #
    #
    # parents = parents.merge(ps_students, how='left', left_on='PS_Student_ID', right_on='PS_Student_ID')
    #
    # re_students = read_file_csv("current_student_class_24.CSV", path_data)
    # re_students = format_re_students(re_students)
    #
    #
    # parents = parents.merge(re_students, how='left', left_on=['Student_First_Name', 'Student_Last_Name'],
    #                         right_on=['Student_First_Name', 'Student_Last_Name'])
    #
    # print(re_students.head(5).to_markdown())
    # print(parents.to_markdown())
    #
    # upload_parent_son_file = format_for_re_upload(parents)
    #
    # print(upload_parent_son_file.to_markdown())
    #
    # upload_parent_son_file.to_csv(path_out / "upload_parent_son_relationship.csv", index=False)
    # # print(temp.to_markdown())

