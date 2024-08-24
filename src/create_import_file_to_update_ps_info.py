from common_functions import *
import usaddress




if __name__ == '__main__':
    path_data = Path(Path.cwd().parent / "data")
    path_out = Path(Path.cwd().parent / "out")

    ps = read_file_excel("PS_data.xlsx", path_data, "Parents (New)")
    ps = clean_ps_parent_data(ps)


    re = read_file_csv("re_total_cp_import_ids_and_ps_parent_ids.CSV", path_data)
    re = clean_re_rename_columns(re)

    ps = ps[['PS_Parents_Contact_ID','First_Name','Last_Name', 'Street', 'City', 'State', 'Zip']]

    fd = re.merge(ps, on=['PS_Parents_Contact_ID'], how='left')
    print(f"after merge: {fd.shape[0]}")

    mask = fd['Street'].isna()
    fd = fd[~mask]

    fd['temp'] = fd['Zip'].str.len()
    mask= ((fd['temp']==5) | (fd['temp']==10))
    fd = fd[mask]

    fd = fd.dropna()




    print(f"final: {fd.shape[0]}")



    # rename columns
    fd = fd.rename(columns={'CnBio_Import_ID': 'ImportID',
                            'Street': 'AddrLines',
                            'City': 'AddrCity',
                            'State': 'AddrState',
                            'Zip': 'AddrZip'})

    fd['PrefAddr'] = "Yes"
    fd['AddrImpID'] = np.nan

    fd.to_csv(path_out / "raw.csv", index=False)



    fd = fd[['ImportID', 'AddrImpID', 'PrefAddr', 'AddrLines', 'AddrCity', 'AddrState', 'AddrZip']]

    #fd =fd.head(1)

    fd.to_csv(path_out / "update_addresses.csv", index=False)

    # drop any rows with nan




    # check zip length


    #print(fd['temp'].value_counts())


    #print(re.head(20))


