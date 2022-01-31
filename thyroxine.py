from imports import *

osteodf = pd.read_csv(os.path.join(fileutility.DATAROOT, "dhr_traumaresearch_osteofractures.csv"))
origlevothyroxinedf = dfutility.simplifyDataFrameColumnHeaders(pd.read_excel(r"C:\Users\nnnwn00\Documents\data\tbi\original_MRNs-levothyroxine-w injury date.xlsx"))
levothyroxinedf = dfutility.simplifyDataFrameColumnHeaders(pd.read_excel(r"C:\Users\nnnwn00\Documents\data\tbi\modified_MRNs-levothyroxine-w injury date.xlsx"))
#Replace "yes" and "no" strings:
dfutility.string.replace_yes_no_in_dataframe_with_bool(levothyroxinedf, inplace=True)

#Split into chunks
for indx, chunk in enumerate(np.array_split(levothyroxinedf, 3)): dfutility.exportDataFrameToExcel(pd.DataFrame(chunk), "MRNs-levothyroxine_chunk{}".format(indx+1))

#use osteodf for meds, s-files for admit dates
merge_osteo_levothy = osteodf[['MRN','HOME_MEDICATION']].merge(levothyroxinedf, on='MRN')
concatsfiledict = pd.concat(fileutility.getSfilesDataFrameDict().values()).reset_index(drop=True)

merge_osteo_levothy_sfile = merge_osteo_levothy.merge(concatsfiledict[['MRN','ADMIT_DATE']], on='MRN')

#Lowercase strings in the df
dfutility.string.lowercase_str_in_dataframe(merge_osteo_levothy, inplace=True)

#If ADMIT_DATE is before TBI date and HOME_MEDICATION contains levothyroxine,