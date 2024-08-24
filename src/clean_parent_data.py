import pandas as pd
from pathlib import Path
from common_functions import *



def clean_ps_parent_data(df):

    df = df.rename(columns={'Contact ID': 'PS_Parents_Contact_ID',
                            'Prefix': 'Prefix',
                            'Suffix':'Suffix',
                            'First Name': 'First_Name',
                            'Last Name *': 'Last_Name',
                            'Email Address': 'Email',
                            'Phone Number (As Entered)': 'Phone_Number',
                            'Phone Type': 'Phone_Type',
                            'Gender': 'Gender',
                            'Relationship Type': 'Relationship_Type',
                            'Student Number': 'Student_Number',
                            'Street': 'Address_1'

                            })

    df = df[['PS_Parents_Contact_ID','Prefix', 'Suffix','First_Name', 'Last_Name',
             'Email', 'Phone_Number', 'Phone_Type', 'Gender', 'Student_Number', 'Address_1']]


    df = df.drop_duplicates(subset=['PS_Parents_Contact_ID'], keep='first')



    df['Last_Name'] = df['Last_Name'].str.title()
    df['First_Name'] = df['First_Name'].str.title()
    df['Email'] = df['Email'].str.lower()


    df['Phone_Number'] = df['Phone_Number'].astype(str)
    df['Phone_Number'] = df['Phone_Number'].str.replace(' ', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('-', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('(', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace(')', '', regex=False)

    df = df.sort_values(['Last_Name', 'First_Name'])

    # impute prefix
    mask_1 = df['Prefix'].isna()
    mask_2 = df['Gender'] == "M"
    mask_T = mask_1 & mask_2

    df.loc[mask_T, 'Prefix'] = "Mr."

    return df

def create_parental_status_dict(df):
    df = df.rename(columns={'Student_Number': 'Student_Number',
                            'parental_status': 'Parental_Status'})

    return dict(zip(df['Student_Number'], df['Parental_Status']))

def clean_re_potential_parents(df):
    df = df.rename(columns={'CnBio_ID': 'Contact_ID',
                            'CnBio_First_Name': 'First_Name',
                            'CnBio_Last_Name': 'Last_Name',
                            'CnPh_1_01_Phone_number': 'Phone_Number',
                            'CnPh_1_02_Phone_number': 'Email',
                            'CnAdrPrf_Addrline1': 'Address_1'
                            })

    df['Phone_Number'] = df['Phone_Number'].astype(str)
    df['Phone_Number'] = df['Phone_Number'].str.replace(' ', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('-', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('(', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace(')', '', regex=False)

    return df




if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    ps_parents = read_file_excel("PS_data.xlsx", path_data, "Parents")
    ps_parental_status = read_file_excel("PS_data.xlsx", path_data, "Parental Status")
    re_potential_parents = read_file_excel("potential_parent_search.xlsx", path_data, "sheet1")

    re_ps_id = read_file_csv("re_parents_ps_ids.CSV", path_data)

    re_ps_id = re_ps_id.rename(columns={
                            'Constituent Specific Attributes power_school_parent_id Description':
                            'PS_Parents_Contact_ID',
                            'Constituent ID': 'Constituent_ID'
                            })



    #dict_parental_status = create_parental_status_dict(ps_parental_status)


    #print(dict_parental_status)


    ps_parents = clean_ps_parent_data(ps_parents)

    # find and save parents in system
    #mask = re_ps_id['PS_Parents_Contact_ID'].isin(ps_parents['PS_Parents_Contact_ID'])
    # re_ps_id = re_ps_id[mask]
    #
    # ps_parents['PS_Parents_Contact_ID'].isin(re_ps_id['PS_Parents_Contact_ID'])
    #

    # test = ps_parents.merge(re_ps_id, on='PS_Parents_Contact_ID', how='inner')
    #
    # test.to_excel(Path(path_out / "test.xlsx"), sheet_name='Sheet1', index=False)
    #
    # print(test.to_markdown(floatfmt='.0f'))



    #re_ps_id.to_excel(Path(path_out / "parents_in_system.xlsx"), sheet_name='Sheet1', index=False)


    # remove parents in system
    mask = ps_parents['PS_Parents_Contact_ID'].isin(re_ps_id['PS_Parents_Contact_ID'])
    ps_parents = ps_parents[~mask]

    # find new potential parents
    re_potential_parents = clean_re_potential_parents(re_potential_parents)





    mask_last_name = re_potential_parents['Last_Name'].isin(ps_parents['Last_Name'])
    mask_first_name = re_potential_parents['First_Name'].isin(ps_parents['First_Name'])
    mask_phone_number = (re_potential_parents['Phone_Number'].isin(ps_parents['Phone_Number'])) & \
                        (re_potential_parents['Phone_Number'].notna())

    mask_email = (re_potential_parents['Email'].isin(ps_parents['Email']) & re_potential_parents['Email'].notna())

    mask_address = (re_potential_parents['Address_1'].isin(ps_parents['Address_1']))



    mask_total = mask_last_name & mask_address

    print(re_potential_parents[mask_total].to_markdown(floatfmt='.0f'))




    print(f"potential matches {sum(mask_total)}")





    #ps_parents['status'] = ps_parents['Student_Number'].map(dict_parental_status)

    #ps_parents.to_excel(Path(path_out / "ps_parents_cleaned.xlsx"), sheet_name='Sheet1', index=False)



   #  re = read_file_csv("RE_current_parents.CSV", path_data)
   #  re = clean_re_parent_data(re)
   #
   #
   #  mask = re['power_school_parent_id'].isna()
   #  re = re[mask]
   #
   #  #re['First_Name'] = re['Nickname']
   #
   #  print("re_data rows after removing power_school_parent_id is null: ", re.shape[0])
   #  #
    #print(ps_parents.to_markdown(floatfmt='.0f'))
   #print(ps_parental_status.head(10))
   #
   #
   #  #
   #  # print(f"ps rows: {ps.shape[0]}")
   #  #
   # # ps = ps.drop_duplicates(subset=['Last_Name', 'First_Name'], keep='first')
   # # ps = ps.sort_values(['Last_Name', 'First_Name'])
   #
   #  #print(ps.to_markdown(floatfmt='.0f'))
   #
   #
   #
   #  #
   #  # print(f"ps rows after removing duplicates: {ps.shape[0]}")
   #
   #
   #
   #
   #
   #  #
   #  # ps_ids_to_remove = duplicate['PS_Parents_Contact_ID'].tolist()
   #  #
   #  # mask = ps['PS_Parents_Contact_ID'].isin(ps_ids_to_remove)
   #  # ps = ps[~mask]
   #
   #
   #  # duplicate = duplicate.sort_values(by=['Last_Name','First_Name'])
   #  #
   #  # non_duplicate = ps[ps.duplicated(['Last_Name', 'First_Name'], keep=False)]
   #  # non_duplicate = duplicate.sort_values(by=['Last_Name', 'First_Name'])
   #
   #
   #
   #  # # print(duplicate.to_markdown())
   #  # #
   #  # # print(duplicate.shape[0])
   #  #
   #  # # duplicate.to_excel("duplicate.xlsx", index=False)
   #  # #
   #  df = ps.merge(re, on=['Last_Name', 'First_Name'], how='left')
   #  # # #
   #  # # #
   #  mask = df['Constituent_ID'].isna()
   #  df = df[~mask]
   #  # #
   #  mask = df['Last_Name'].isna()
   #  df = df[~mask]
   #  # # #
   #  # # # # df = ps.merge(re, on=['Last_Name', 'First_Name'], how='left')
   #  # # #
   #  print(df.head(20).to_markdown(floatfmt='.0f'))
   #  print(df.shape[0])
   #  # #
   #  fn_out = path_out / "output.csv"
   #  # #
   #  # df.to_excel(fn_out, index=False)
   #
   #  df = df[['PS_Parents_Contact_ID', 'Constituent_ID']]
   #
   #  df = df.rename(columns={'Constituent_ID': 'ConsID',
   #                          'PS_Parents_Contact_ID': 'CAttrDesc'
   #                          })
   #
   #  df['CAttrCat'] = 'power_school_parent_id'
   #
   #  df = df[['ConsID', 'CAttrCat', 'CAttrDesc']]
   #
   #  print(df.head(20).to_markdown(floatfmt='.0f'))
   #  print(f"df rows: {df.shape[0]}")
   #
   #  df['ConsID'] = df['ConsID'].astype(int)
   #





