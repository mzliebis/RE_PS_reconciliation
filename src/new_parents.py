import numpy as np
import pandas as pd
from pathlib import Path
import sys
import gender_guesser.detector as gender
from common_functions import *

pd.options.mode.chained_assignment = None  # default='warn'

def read_file_excel(file_name, path, sheet):
    return pd.read_excel(path / file_name, sheet_name=sheet)

def read_file_csv(file_name, path):
    return pd.read_csv(path / file_name, encoding='latin1')


def clean_ps_parent_data(df, df_id):

    print(f"ps_data rows pre clean: {df.shape[0]}")



    df = df.rename(columns={'Contact ID': 'PS_Parents_Contact_ID',
                            'First Name': 'First_Name',
                            'Last Name *': 'Last_Name',
                            'Email Address': 'Email',
                            'Phone Number (As Entered)': 'Phone_Number',
                            'Phone Type': 'Phone_Type',
                            'Relationship Type': 'Relationship_Type',
                            'Student Number': 'Student_Number',
                            'Prefix': 'Prefix',
                            'Suffix': 'Suffix',
                            'Street': 'Street',
                            'City': 'City',
                            'State': 'State',
                            'Postal Code': 'Zip'
                        })


    # remove duplicates
    df = df.drop_duplicates(subset=['PS_Parents_Contact_ID'], keep='first')
    print(f"ps_data after drop duplicates: {df.shape[0]}")

    # remove parents matching on re ps_parents_id
    mask = df['PS_Parents_Contact_ID'].isin(df_id['PS_Parents_Contact_ID'])
    df = df[~mask]
    print(f"ps_data after drop ps id already in re: {df.shape[0]}")


    df = ps_format_street_address(df)

    df['Zip'] = df['Zip'].astype(str)

    # if zip is less than 5 digits add leading zeros
    mask = df['Zip'].str.len() < 5
    df.loc[mask, 'Zip'] = df['Zip'].apply(lambda x: x.zfill(5))


    df = df[['PS_Parents_Contact_ID', 'Prefix','First_Name', 'Last_Name', 'Suffix', 'Email',
             'Phone_Number', 'Phone_Type', 'Relationship_Type', 'Student_Number', 'Street',
             'City', 'State', 'Zip']]

    df['Phone_Type'] = df['Phone_Type'].replace({'Mobile': 'Cell Phone',
                                                  'Daytime': 'Business'})

    df['Phone_Type'] = df['Phone_Type'].str.title()

    # remove type for missing phone numbers
    mask = df['Phone_Number'].isna()
    df.loc[mask, 'Phone_Type'] = np.nan


    df = df.sort_values(['Last_Name', 'First_Name'])

    # filter for mother ot father
    mask = (df['Relationship_Type'] == 'Father') | (df['Relationship_Type'] == 'Mother')
    df = df[mask]
    print(f"ps_data after drop sfter filter for mother or father: {df.shape[0]}")

    # drop missing last name
    mask = df['Last_Name'].isna()
    df = df[~mask]
    print(f"ps_data remove missing last name: {df.shape[0]}")



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

    # print(f"total rows: {df.shape[0]}")
    # print(f"non duplicates rows: {non_duplicates.shape[0]}")
    # print(f"duplicates rows: {duplicates.shape[0]}")

    # gender_guesser
    # d = gender.Detector()
    # duplicates['Gender_Guess'] = duplicates['First_Name'].apply(lambda x: d.get_gender(x, 'usa'))
    #
    # duplicates['Parent_Guess'] = duplicates['Gender_Guess'].map({"mostly_male": "Father",
    #                                                              "male": "Father",
    #                                                              "mostly_female": "Mother",
    #                                                              "female": "Mother"})

    # mask_valid = duplicates['Parent_Guess'].notna()
    # mask = (duplicates['Parent_Guess'] != duplicates['Relationship_Type']) & mask_valid
    # duplicates = duplicates[~mask]
    # print(f"duplicates rows after gender check: {duplicates.shape[0]}")

    # mask = duplicates.duplicated(subset=['PS_Parents_Contact_ID'], keep='first')
    # duplicates = duplicates[mask]
    # print(f"duplicates rows after 2nd duplicate removal: {duplicates.shape[0]}")
    #
    # df = pd.concat([non_duplicates,duplicates])

    df = df.sort_values(['Last_Name', 'First_Name'])


    #print(df.to_markdown())




    #print(duplicates.to_markdown())


    return df

def clean_re_parent_data(df):

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

    # phone email
    mask = df['Phone_Number_Type_1'] == "Cell Phone"
    df['Cell_Phone'] = df.loc[mask, 'Phone_Number_1']
    df['Cell_Phone'] = df.loc[~mask, 'Phone_Number_2']

    df['Email'] = df.loc[mask, 'Phone_Number_2']
    df['Email'] = df.loc[~mask, 'Phone_Number_1']


    df = df.drop_duplicates(subset=['Constituent_ID'], keep='first')
    print(f"re_data rows duplicates removed: {df.shape[0]}")

    df['Last_Name'] = df['Last_Name'].str.lower()
    df['First_Name'] = df['First_Name'].str.lower()
    df['Nickname'] = df['Nickname'].str.lower()

    df['Email'] = df['Email'].str.lower()

    #df['Phone_Number'] = df['Phone_Number'].str.replace(' ', '', regex=False)



    return df

def clean_ps_students_data(df):
    df = df.rename(columns={'Student Number': 'Student_Number',
                            'ClassOf': 'Class_Of',
                            'parental_status': 'Parental_Status'
                            })

    df = df[['Student_Number', 'Class_Of', 'Parental_Status']]

    df['Class_Of'] = df['Class_Of'].sub(2000).astype('str')

    df['Parental_Status'] = df['Parental_Status'].replace({'Never Married': 'Single'})


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

    # if a prefix does not end with a period add one
    mask = df['Prefix'].str[-1] != "."
    df.loc[mask, 'Prefix'] = df.loc[mask, 'Prefix'] + "."


    mask = ~(df['Prefix'].isin(allowed_values))

    if sum(mask)> 0:
        print(f"problem with prefix: {sum(mask)}")
        print(df[mask])
        sys.exit("problem with prefix")

    return df


def add_spouse_info(df):

    original_num_rows = df.shape[0]
    print(f"original_rows: {original_num_rows}")
    sp = df.copy()
    sp = sp[['Student_Number', 'Prefix', 'First_Name', 'Last_Name']]

    sp = sp.rename(columns={'Student_Number': 'Student_Number',
                            'Prefix': 'Spouse_Prefix',
                            'First_Name': 'Spouse_First_Name',
                            'Last_Name': 'Spouse_Last_Name'
                            })

    #masks
    mask_married = df['Parental_Status'] == 'Married'
    mask_not_married = ~mask_married


    # if not married set spouse info to nan
    df_not_married = df[mask_not_married].copy()
    df_not_married[['Spouse_Prefix', 'Spouse_First_Name', 'Spouse_Last_Name']] = np.nan
    print(f"not married {df_not_married.shape[0]}")

    # married
    df_married = df[mask_married].copy()
    print(f"married {df_married.shape[0]}")
    df_married = df_married.merge(sp, on=['Student_Number'], how='left')
    print(f"married after merge {df_married.shape[0]}")


    # need to look into
    mask_temp = (df_married['First_Name'] != df_married['Spouse_First_Name'])

#
    df_married = df_married[mask_temp]



    df = pd.concat([df_not_married,df_married])


    final_num_rows = df.shape[0]
    print(f"final_rows: {final_num_rows}")

    return df

def add_salutation(df):

    df['Saluation'] = df['First_Name']
    return df

def add_addressee(df):

    df['Addressee'] = df['Prefix'] + " " + df['First_Name'] + " " + " " + df['Last_Name'] + ", P'" + df['Class_Of']


    return df


def add_gomez_salutation(df):

    df = df.reset_index()

    df['Gomez_Salutation'] = df['First_Name']

    mask_married = df['Parental_Status'] == 'Married'
    mask_spouse_first_name = df['Spouse_First_Name'].notna()

    mask_father = df['Relationship_Type'] == 'Father'
    mask_mother = df['Relationship_Type'] == 'Mother'



    mask_total_father = mask_married & mask_spouse_first_name & mask_father
    mask_total_mother = mask_married & mask_spouse_first_name & mask_mother

    df.loc[mask_total_father, 'Gomez_Salutation'] = df['Spouse_First_Name'] + " and " + df['First_Name']
    df.loc[mask_total_mother, 'Gomez_Salutation'] = df['First_Name'] + " and " + df['Spouse_First_Name']

    return df


def add_gomez_addressee(df):

    df['Gomez_Addressee'] = df['Addressee']

    mask_married = df['Parental_Status'] == 'Married'
    mask_spouse_first_name = df['Spouse_First_Name'].notna()

    mask_father = df['Relationship_Type'] == 'Father'
    mask_mother = df['Relationship_Type'] == 'Mother'

    mask_same_last_name = df['Last_Name'] == df['Spouse_Last_Name']
    mask_different_last_name = df['Last_Name'] != df['Spouse_Last_Name']

    mask_total_father_same_last_name = mask_married & mask_spouse_first_name & mask_father & mask_same_last_name
    mask_total_father_different_last_name = mask_married & mask_spouse_first_name & mask_father & mask_different_last_name

    mask_total_mother_same_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_same_last_name
    mask_total_mother_different_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_different_last_name


    df.loc[mask_total_father_same_last_name, 'Gomez_Addressee'] = df['Prefix'] + " and " + df['Spouse_Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
    df.loc[mask_total_father_different_last_name,  'Gomez_Addressee'] = df['Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + " and " + df['Spouse_Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']

    df.loc[mask_total_mother_same_last_name, 'Gomez_Addressee'] = df['Spouse_Prefix'] + " and " + df['Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']
    df.loc[mask_total_mother_different_last_name,  'Gomez_Addressee'] = df['Spouse_Prefix'] + " " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + " and " + df['Prefix'] + " " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
    return df

def add_presidents_report_listing(df):


    mask_married = df['Parental_Status'] == 'Married'
    mask_spouse_first_name = df['Spouse_First_Name'].notna()

    mask_father = df['Relationship_Type'] == 'Father'
    mask_mother = df['Relationship_Type'] == 'Mother'

    mask_same_last_name = df['Last_Name'] == df['Spouse_Last_Name']
    mask_different_last_name = df['Last_Name'] != df['Spouse_Last_Name']

    mask_total_father_same_last_name = mask_married & mask_spouse_first_name & mask_father & mask_same_last_name
    mask_total_father_different_last_name = mask_married & mask_spouse_first_name & mask_father & mask_different_last_name

    mask_total_mother_same_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_same_last_name
    mask_total_mother_different_last_name = mask_married & mask_spouse_first_name & mask_mother & mask_different_last_name

    df['Presidents_Report_Listing'] = df['Gomez_Addressee']
    df.loc[mask_total_father_same_last_name, 'Presidents_Report_Listing'] = "M/M " + df['First_Name'] + " " + df['Last_Name'] + ", P'" + df['Class_Of']
    df.loc[mask_total_mother_same_last_name, 'Presidents_Report_Listing'] = "M/M " + df['Spouse_First_Name'] + " " + df['Spouse_Last_Name'] + ", P'" + df['Class_Of']


    return df

def format_for_re_import(df):
    df['KeyInd'] = "I"
    df['ConsCode'] = "Current Parent"
    df['PrefAddr'] = "Yes"
    df['AddrType'] = "Home"
    df['ConsCode2'] = df['Relationship_Type']
    df['PhoneType2'] = 'E-mail Primary'

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

    df['CAttrCat'] = "power_school_parent_id"
    df['CAttrDesc'] = df['PS_Parents_Contact_ID']

    mask = df['Phone_Type'].isna()
    df.loc[mask,'Phone_Type'] = "Cell Phone"

    mask = df['Phone_Number'].isna()
    df.loc[mask,'Phone_Number'] = "nan"

    mask = df['Email'].isna()
    df.loc[mask, 'Email'] = "nan"

    mask = df['First_Name'].isna()
    df = df[~mask]


    df = df.rename(columns={'Prefix':'Titl1',
                            'First_Name':'FirstName',
                            'Last_Name':'LastName',
                            'Street': 'AddrLines',
                            'City': 'AddrCity',
                            'State': 'AddrState',
                            'Zip': 'AddrZip',
                            'Phone_Type': 'PhoneType',
                            'Phone_Number': 'PhoneNum',
                            'Email': 'PhoneNum2',
                            'Parental_Status': 'MrtlStat',

                            })



    df = df[['KeyInd', 'ConsCode', 'ConsCode2',
             'Titl1', 'FirstName',
             'LastName', 'PrefAddr',
             'AddrType', 'AddrLines',
             'AddrCity', 'AddrState', 'AddrZip',
             'PhoneType', 'PhoneNum',
             'PhoneType2', 'PhoneNum2',
             'MrtlStat',
             'PrimSalID','PrimSalEdit','PrimSalText',
             'PrimAddID','PrimAddEdit','PrimAddText',
             'AddSalID','AddSalType','AddSalEditable','AddSalText',
             'AddSalID2','AddSalType2','AddSalEditable2','AddSalText2',
             'AddSalID3','AddSalType3','AddSalEditable3','AddSalText3',
             'CAttrCat','CAttrDesc']]

    return df

def reformat_re_ps_id(df):
    df = df.rename(columns={
        'Constituent Specific Attributes power_school_parent_id Description':
            'PS_Parents_Contact_ID',
        'Constituent ID': 'Constituent_ID'
    })

    return df




if __name__ == '__main__':

    class_of = "28"

    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    ps = read_file_excel("PS_data.xlsx", path_data, "Parents")
    re_ps_id = read_file_csv("re_ps_parents_ids.CSV", path_data)

    re_ps_id = reformat_re_ps_id(re_ps_id)

    ps = clean_ps_parent_data(ps, re_ps_id)

    #print(ps.to_markdown())




    ps_students = read_file_excel("PS_data.xlsx", path_data, "Students")
    ps_students = clean_ps_students_data(ps_students)

    #
    # re = read_file_csv("RE_current_parents_5.CSV", path_data)
    # re = clean_re_parent_data(re)
    #
    # # remove parents already mapped
    # ids_removed = re['PS_Parents_Contact_ID'].tolist()
    # print(f"re parents already in system: {len(ids_removed)}")

    #
    # mask = ps['PS_Parents_Contact_ID'].isin(ids_removed)
    # ps = ps[~mask]

    ps = ps.merge(ps_students, on=['Student_Number'], how='left')


    # class of filter
    mask = ps['Class_Of'] == class_of
    ps = ps[mask]
    print(f"ps_data rows class of filter {class_of}: {ps.shape[0]}")

    ps = fix_prefix(ps)
    ps = add_spouse_info(ps)
    ps = add_salutation(ps)
    ps = add_addressee(ps)
#    print(ps.head(50).to_markdown())


    ps = add_gomez_salutation(ps)
    ps = add_gomez_addressee(ps)
    ps = add_presidents_report_listing(ps)

    fn_out_raw = "re_np_class_" + class_of + "_raw.csv"
    ps.to_csv(path_out / fn_out_raw, index=False)

    ps = format_for_re_import(ps)

    fn_out_import = "re_np_class_" + class_of + "_import.csv"
    ps.to_csv(path_out / fn_out_import, index=False)

