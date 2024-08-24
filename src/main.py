import pandas as pd
from pathlib import Path

def read_file_excel(file_name, path, sheet):
    return pd.read_excel(path / file_name, sheet_name=sheet)

def read_file_csv(file_name, path):
    return pd.read_csv(path / file_name, encoding='latin1')

def clean_ps_parent_data(df):

    df = df.rename(columns={'Contact ID': 'PS_Parents_Contact_ID',
                            'First Name': 'First_Name',
                            'Last Name *': 'Last_Name',
                            'Email Address': 'Email',
                            'Phone Number (As Entered)': 'Phone_Number',
                            'Phone Type': 'Phone_Type'
                        })

    df = df[['PS_Parents_Contact_ID', 'First_Name', 'Last_Name', 'Email', 'Phone_Number', 'Phone_Type']]


    df = df.drop_duplicates(subset=['PS_Parents_Contact_ID'], keep='first')



    df['Last_Name'] = df['Last_Name'].str.lower()
    df['First_Name'] = df['First_Name'].str.lower()
    df['Email'] = df['Email'].str.lower()


    df['Phone_Number'] = df['Phone_Number'].astype(str)
    df['Phone_Number'] = df['Phone_Number'].str.replace(' ', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('-', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace('(', '', regex=False)
    df['Phone_Number'] = df['Phone_Number'].str.replace(')', '', regex=False)

    df = df.sort_values(['Last_Name', 'First_Name'])


    return df

def clean_re_parent_data(df):

    df = df.rename(columns={'CnBio_ID': 'Constituent_ID',
                            'CnBio_First_Name': 'First_Name',
                            'CnBio_Nickname': 'Nickname',
                            'CnBio_Last_Name': 'Last_Name',
                            'CnAdrSalAll_1_01_Salutation': 'Gomez_Addressee',
                            'CnAttrCat_1_01_Description': 'power_school_parent_id',
                            'CnPh_1_01_Phone_type': 'Phone_Type_1',
                            'CnPh_1_02_Phone_type': 'Phone_Type_2',
                            'CnPh_1_01_Phone_number': 'Phone_Number_1',
                            'CnPh_1_02_Phone_number': 'Phone_Number_2',

                            })

    mask = df['Phone_Type_1'] == "Cell Phone"
    df['Cell_Phone'] = df.loc[mask, 'Phone_Number_1']
    df['Cell_Phone'] = df.loc[~mask, 'Phone_Number_2']

    df['Email'] = df.loc[mask, 'Phone_Number_2']
    df['Email'] = df.loc[~mask, 'Phone_Number_1']


    print(f"re_data rows: {df.shape[0]}")
    df = df.drop_duplicates(subset=['Constituent_ID'])
    print(f"re_data rows duplicates removed: {df.shape[0]}")

    df['Last_Name'] = df['Last_Name'].str.lower()
    df['First_Name'] = df['First_Name'].str.lower()
    df['Nickname'] = df['Nickname'].str.lower()

    df['Email'] = df['Email'].str.lower()


#    df['First_Name'] = df['Nickname']

    #df['Phone_Number'] = df['Phone_Number'].str.replace(' ', '', regex=False)



    return df


if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    ps = read_file_excel("PS_data.xlsx", path_data, "Parents (New)")
    ps = clean_ps_parent_data(ps)

    re = read_file_csv("RE_current_parents.CSV", path_data)
    re = clean_re_parent_data(re)


    mask = re['power_school_parent_id'].isna()
    re = re[mask]

    #re['First_Name'] = re['Nickname']

    print("re_data rows after removing power_school_parent_id is null: ", re.shape[0])
    #
    print(ps.to_markdown(floatfmt='.0f'))


    #
    # print(f"ps rows: {ps.shape[0]}")
    #
   # ps = ps.drop_duplicates(subset=['Last_Name', 'First_Name'], keep='first')
   # ps = ps.sort_values(['Last_Name', 'First_Name'])

    #print(ps.to_markdown(floatfmt='.0f'))



    #
    # print(f"ps rows after removing duplicates: {ps.shape[0]}")





    #
    # ps_ids_to_remove = duplicate['PS_Parents_Contact_ID'].tolist()
    #
    # mask = ps['PS_Parents_Contact_ID'].isin(ps_ids_to_remove)
    # ps = ps[~mask]


    # duplicate = duplicate.sort_values(by=['Last_Name','First_Name'])
    #
    # non_duplicate = ps[ps.duplicated(['Last_Name', 'First_Name'], keep=False)]
    # non_duplicate = duplicate.sort_values(by=['Last_Name', 'First_Name'])



    # # print(duplicate.to_markdown())
    # #
    # # print(duplicate.shape[0])
    #
    # # duplicate.to_excel("duplicate.xlsx", index=False)
    # #
    df = ps.merge(re, on=['Last_Name', 'First_Name'], how='left')
    # # #
    # # #
    mask = df['Constituent_ID'].isna()
    df = df[~mask]
    # #
    mask = df['Last_Name'].isna()
    df = df[~mask]
    # # #
    # # # # df = ps.merge(re, on=['Last_Name', 'First_Name'], how='left')
    # # #
    print(df.head(20).to_markdown(floatfmt='.0f'))
    print(df.shape[0])
    # #
    fn_out = path_out / "output.csv"
    # #
    # df.to_excel(fn_out, index=False)

    df = df[['PS_Parents_Contact_ID', 'Constituent_ID']]

    df = df.rename(columns={'Constituent_ID': 'ConsID',
                            'PS_Parents_Contact_ID': 'CAttrDesc'
                            })

    df['CAttrCat'] = 'power_school_parent_id'

    df = df[['ConsID', 'CAttrCat', 'CAttrDesc']]

    print(df.head(20).to_markdown(floatfmt='.0f'))
    print(f"df rows: {df.shape[0]}")

    df['ConsID'] = df['ConsID'].astype(int)

    df.to_csv(fn_out, index=False)



