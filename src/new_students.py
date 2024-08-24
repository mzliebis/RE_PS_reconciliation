from common_functions import *


def clean_ps_students_data(df):

    print(f"ps_data rows pre clean: {df.shape[0]}")

    print(df.columns)

    df = df.rename(columns={'Student_Number': 'PS_Student_ID',
                            'First Name': 'First_Name',
                            'Last Name': 'Last_Name',
                            'ClassOf': 'Class_Of',
                            'Student_Email_spprep_org': 'Prep_Email',
                            'student_email': 'Personal_Email',
                            'Cell_phone': 'Cell_Phone',
                            'Student Number': 'Student_Number',
                            'Prefix': 'Prefix',
                            'street': 'Street',
                            'city': 'City',
                            'state': 'State',
                            'zip': 'Zip'
                        })

    # add Prefix
    df['Prefix'] = "Mr."

    df['Class_Of'] = df['Class_Of'].subtract(2000).astype(str)


    #zip formating
    df['Zip'] = df['Zip'].astype(str)
    mask = df['Zip'].str.len() < 5
    df.loc[mask, 'Zip'] = df['Zip'].apply(lambda x: x.zfill(5))

    #sort by last name, first name
    df = df.sort_values(['Last_Name', 'First_Name'])


    df['Cell_Phone'] = format_phone_number(df, 'Cell_Phone')

    df = df[['PS_Student_ID', 'First_Name',
             'Last_Name','Class_Of',
             'Prefix', 'Street',
             'City', 'State', 'Zip', 'Cell_Phone',
             'Prep_Email', 'Personal_Email']]

    return df


def fix_prefix(df):

    df['Prefix'] = df['Prefix'].map({'Mr': 'Mr.',
                                     'Ms':'Ms.',
                                     'Mrs.': 'Mrs'
                                     })

    mask_na = df['Prefix'].isna()
    mask_father = df['Relationship_Type'] == 'Father'
    mask_mother = df['Relationship_Type'] == 'Mother'
    mask_married = df['Parental_Status'] == 'Married'
    mask_mrs_fix = mask_mother & mask_married & mask_na
    mask_ms_fix = mask_mother & ~mask_married & mask_na

    mask_father_fix = mask_na & mask_father

    df.loc[mask_father_fix, 'Prefix'] = "Mr."
    df.loc[mask_mrs_fix, 'Prefix'] = "Mrs."
    df.loc[mask_ms_fix, 'Prefix'] = "Ms."

    allowed_values = ['Mrs.', 'Ms.', 'Mr.']
    mask = ~(df['Prefix'].isin(allowed_values))

    if sum(mask)> 0:
        print(f"problem with prefix: {sum(mask)}")
        print(df[mask])
        sys.exit("problem with prefix")

    return df

def add_all_addresses_and_slautation(df):

    df['Saluation'] = df['First_Name']
    df['Addressee'] = df['Prefix'] + " " + df['First_Name'] + " " + " " + df['Last_Name'] + ", '" + df['Class_Of']
    df['Gomez_Salutation'] = df['Saluation']
    df['Gomez_Addressee'] = df['Addressee']
    df['Presidents_Report_Listing'] = df['Addressee']

    return df
#
# def add_salutation(df):
#
#     df['Saluation'] = df['First_Name']
#     return df
#
# def add_addressee(df):
#
#     df['Addressee'] = df['Prefix'] + " " + df['First_Name'] + " " + " " + df['Last_Name'] + ", '" + df['Class_Of']
#     return df
#
#
# def add_gomez_salutation(df):
#
#     df = df.reset_index()
#
#     df.loc[mask_total_father, 'Gomez_Salutation'] = df['Spouse_First_Name'] + " and " + df['First_Name']
#     df.loc[mask_total_mother, 'Gomez_Salutation'] = df['First_Name'] + " and " + df['Spouse_First_Name']
#
#     return df
#
#
# def add_gomez_addressee(df):
#
#     df['Gomez_Addressee'] = df['Addressee']
#
#     mask_married = df['Parental_Status'] == 'Married'
#     mask_spouse_first_name = df['Spouse_First_Name'].notna()
#
#     mask_father = df['Relationship_Type'] == 'Father'
#     mask_mother = df['Relationship_Type'] == 'Mother'
#
#     mask_same_last_name = df['Last_Name'] == df['Spouse_Last_Name']
#     mask_different_last_name = df['Last_Name'] != df['Spouse_Last_Name']
#
#     mask_total_father_same_last_name = mask_married & mask_spouse_first_name & mask_father & mask_same_last_name
#     mask_total_father_different_last_name = mask_married & mask_spouse_first_name & mask_father & mask_different_last_name
#
#     mask_total_mother_same_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_same_last_name
#     mask_total_mother_different_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_different_last_name
#
#
#
#
#     df.loc[mask_total_father_same_last_name, 'Gomez_Addressee'] = df['Prefix'] + " and " + df['Spouse_Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
#     df.loc[mask_total_father_different_last_name,  'Gomez_Addressee'] = df['Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + " and " + df['Spouse_Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']
#
#     df.loc[mask_total_mother_same_last_name, 'Gomez_Addressee'] = df['Spouse_Prefix'] + " and " + df['Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']
#     df.loc[mask_total_mother_different_last_name,  'Gomez_Addressee'] = df['Spouse_Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + " and " + df['Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
#     return df
#
# def add_presidents_report_listing(df):
#
#
#     mask_married = df['Parental_Status'] == 'Married'
#     mask_spouse_first_name = df['Spouse_First_Name'].notna()
#
#     mask_father = df['Relationship_Type'] == 'Father'
#     mask_mother = df['Relationship_Type'] == 'Mother'
#
#     mask_same_last_name = df['Last_Name'] == df['Spouse_Last_Name']
#     mask_different_last_name = df['Last_Name'] != df['Spouse_Last_Name']
#
#     mask_total_father_same_last_name = mask_married & mask_spouse_first_name & mask_father & mask_same_last_name
#     mask_total_father_different_last_name = mask_married & mask_spouse_first_name & mask_father & mask_different_last_name
#
#     mask_total_mother_same_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_same_last_name
#     mask_total_mother_different_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_different_last_name
#
#     df['Presidents_Report_Listing'] = df['Gomez_Addressee']
#     df.loc[mask_total_father_same_last_name, 'Presidents_Report_Listing'] = "M/M " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
#     df.loc[mask_total_mother_same_last_name, 'Presidents_Report_Listing'] = "M/M " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']
#
#
#     return df

def format_for_re_import(df):

    df['KeyInd'] = "I"
    df['ConsCode'] = "Current Student"
    df['PrefAddr'] = "Yes"
    df['AddrType'] = "Home"

    df['PrimSalText'] = df['Saluation']
    df['PrimSalID'] = np.nan
    df['PrimSalEdit'] = "Y"

    df['PrimAddText'] = df['Addressee']
    df['PrimAddID'] = np.nan
    df['PrimAddEdit'] = "Y"

    df['AddSalID'] = 56
    df['AddSalType'] = 'Gomez Salutation'
    df['AddSalEditable'] = "Y"
    df['AddSalText'] = df['Gomez_Salutation']

    df['AddSalID2'] = 56
    df['AddSalType2'] = "Gomez Addressee"
    df['AddSalEditable2'] = "Y"
    df['AddSalText2'] = df['Gomez_Addressee']

    df['AddSalID3'] = 56
    df['AddSalType3'] = "President's Report Listing"
    df['AddSalEditable3'] = "Y"
    df['AddSalText3'] = df['Presidents_Report_Listing']

    df['CAttrCat'] = "power_school_student_id"
    df['CAttrDesc'] = df['PS_Student_ID']

    df['PhoneType'] = "Cell Phone"
    df['PhoneNum'] = df['Cell_Phone']

    df['PhoneType2'] = "E-mail Primary"
    df['PhoneNum2'] = df['Prep_Email']



    df = df.rename(columns={'Prefix':'Titl1',
                            'First_Name':'FirstName',
                            'Last_Name':'LastName',
                            'Street': 'AddrLines',
                            'City': 'AddrCity',
                            'State': 'AddrState',
                            'Zip': 'AddrZip'

                            })



    df = df[['KeyInd', 'ConsCode',
             'Titl1', 'FirstName',
             'LastName', 'PrefAddr',
             'AddrType', 'AddrLines',
             'AddrCity', 'AddrState', 'AddrZip',
             'PhoneType', 'PhoneNum',
             'PhoneType2', 'PhoneNum2',
             'PrimSalID','PrimSalEdit','PrimSalText',
             'PrimAddID','PrimAddEdit','PrimAddText',
             'AddSalID','AddSalType','AddSalEditable','AddSalText',
             'AddSalID2','AddSalType2','AddSalEditable2','AddSalText2',
             'AddSalID3','AddSalType3','AddSalEditable3','AddSalText3',
             'CAttrCat','CAttrDesc']]

    return df





if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    class_year = "28"


    ps_students = read_file_excel("PS_data.xlsx", path_data, "Students")
    ps_students = clean_ps_students_data(ps_students)

    # only keep current class
    mask = ps_students['Class_Of'] == class_year
    ps_students = ps_students[mask]
    print(f"ps_students class of {class_year}: {ps_students.shape[0]}")



    # re current student ids
    fn_re_curent_students = "re_students_ps_ids.CSV"
    re_students = read_file_csv(fn_re_curent_students, path_data)

    # only keep students not in re
    ps_student_ids_in_re = re_students['Constituent Specific Attributes power_school_student_id Description'].tolist()
    print(f"ps_student_ids_in_re: {len(ps_student_ids_in_re)}")
    mask = ps_students['PS_Student_ID'].isin(ps_student_ids_in_re)
    print(f"students removed {sum(mask)}")
    ps_students = ps_students[~mask]
    print(f"ps_students for upload: {ps_students.shape[0]}")


    ps_students = add_all_addresses_and_slautation(ps_students)



    import_format_ps_students = format_for_re_import(ps_students)

    print(import_format_ps_students)

    fn_out = "re_new_students_class_" + class_year + "_import.csv"
    # #
    import_format_ps_students.to_csv(path_out / fn_out, index=False)
    # #print(ps.to_markdown(floatfmt='.0f'))





