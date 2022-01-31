#AUTHOR: William Noonan
import os
import pandas as pd
import numpy as np
import fileutility
import osteoutility
import dfutility
import re
import itertools

from importlib import reload

#pandas settings:
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 12)

while True:
    inp = input("Read csv (y/n):")
    if inp.lower() == "y":
        path = os.path.join(fileutility.DATAROOT, "dhr_traumaresearch_osteofractures.csv")
        print("Reading {}".format(path))
        #origosteodf = pd.read_excel(path, sheet_name=0)
        origosteodf = dfutility.simplifyDataFrameColumnHeaders(pd.read_csv(path))
        # origosteodf['DOB'] = origosteodf['DOB'].dt.strftime('%Y/%m/%d')
        origosteodf['CHRONIC_PROBLEM'].replace(np.nan, "None", inplace=True)
        osteodf = origosteodf.copy()
        break
    elif inp.lower() == "n":
        break
    else:
        print("Invalid input. Enter y or n.")


#xTODO lowercase every column like so: nomultivitamin.HOME_MEDICATION = nomultivitamin.HOME_MEDICATION.str.lower(), NOTE: may not be helpful when consolidating certain things like vitamin-D NOTE: obe
#xTODO make a copy of columns expected to be modified like so: nomultivitamin['origHOME_MEDICATION'] = nomultivitamin.HOME_MEDICATION #NOTE: must use bracket/string syntax to create a new column

#def getFilteredChronicProblemDataFrame(): #TODO make a function

"""CHRONIC PROBLEM FILTERING"""
#TODO For partial string replacements. NOTE: calling .str.replace() on a column returns a series. The column of the dataframe
#TODO must be set like so df['Column5'] = df['Column5'].str.replace(<regexpat>, <string>, case=False). TODO Nested dict
#TODO with column name as key, and values are dictionaries of regex replacements? OR use default_dict from collections
# For the CHRONIC_PROBLEM column:
cp_replace_patterns = [(r'(?<=\bnon)-', '_'),
                       (r"\b(?:obese)\b", "obese (obesity)"),
                       (r"\b(?:mellitus)", ''),
                       (r"^(?!.*\b(?:diabetes)\b).*\b(?:dm[1-2]*)\b", "diabetes"),
                       (r"\b(?:kidney)\b", 'renal'),
                       ]

#TODO For cell replacements, create dictionary of regex patterns and replacement string:
cp_overwrite_patterns = [(r"osteoporosis", "osteoporosis"),
                         (r"fall", "fall_risk"),
                         (r"^(?!.*\b(?:index)\b).*(?:\b(?:lymphoma|melanoma|myeloma|cancer|carcinoma|tumor|mass|malignant)\b|(?:sarcoma|leuk.*emia))", "cancer"),
                         (r"\b(?:hypertensive disorder)\b", 'hypertension'),
                         (r"^(?!.*\b(?:pain)\b).*(?:\b(?:ability|mobility|gait)\b|(?:walk))", 'impaired mobility'),
                         (r"(?:thyroid)", 'thyroid disorder'),
                         (r"(?:Benign hypertensive heart AND renal disease)", 'renal disease'),  #TODO be aware of potential conflict with dropping "benign" matches #TODO make case-insensitive
                         (r"(?:arthritis)", 'arthritis'),
                         (r"(?:coronary|cardiac|heart)", 'heart problems'),
                         (r"\b(?:HLD|(?:dys|hyper(?:cho|lip|tri)).*emia)\b", 'lipid'), #TODO make case-insensitive
                         (r'^(?!.*diabetes).*type II', 'diabetes'),  # wasn't really worth it, found in only one MRN #TODO make case-insensitive
                         ]



#TODO Excludes. Requires the dataframe to be re-set
cp_drop_patterns_1 = (r"\b(?:history|late|old|H/O)\b", r"(?:stone)", r"(?:sore)") # must be excluded BEFORE cell replacements because of conflict with r"(?:Benign hypertensive heart AND renal disease)"
cp_drop_patterns_2 = (r"(?:benign)",)

#Query:
#TODO how many patients only have 'At risk of pressure sore' as their only comorbidity?
#nomultivit.CHRONIC_PROBLEM.groupby(nomultivit.MRN).unique().apply(lambda x: len(x)==1 and any(["sore" in y.lower() for y in x]) ).sum()

cp_filtering_list = [(cp_drop_patterns_1, 'drop'),
                     (cp_replace_patterns, 'replace'),
                     (cp_overwrite_patterns, 'overwrite'),
                     (cp_drop_patterns_2, 'drop'),
                     ]

#xTODO obe, delete
# osteodf = utility.drop_from_patterns(osteodf, col_of_interest, exclude1)
# osteodf = utility.replace_from_patterns(osteodf, col_of_interest, stringreplace)
# osteodf = utility.overwrite_from_patterns(osteodf, col_of_interest, celloverwrite)
# osteodf = utility.drop_from_patterns(osteodf, col_of_interest, exclude2)


#TODO isolate the column of interest, drop duplicates grouped by MRN
cp_column_name = 'CHRONIC_PROBLEM'

#osteodf = dfutility.dataframe_reduce_column(osteodf, cpcolumnstr, [(dfutility.drop_from_patterns, exclude1)])

exploded_unique_cp_values_df = dfutility.dataframeExplodeUniqueValuesInColumnGroupedByIndex(osteodf.CHRONIC_PROBLEM.groupby(osteodf.MRN))
filtered_eucvd = dfutility.filter_dataframe_column(exploded_unique_cp_values_df, cp_column_name, cp_filtering_list)

chronic_problem_keywordlist = ['hypertension', 'obesity', 'mobility', 'diabetes', 'lipid', 'arthritis', 'heart',
                               'thyroid', 'cancer', 'osteoporosis', 'renal']

bool_table_filtered_chronic_problem = dfutility.dataframeBooleanTableKeywordsInListGroupedByIndex(filtered_eucvd, cp_column_name, chronic_problem_keywordlist)

########################################################################################################################
"""HOME_MEDICATION FILTERING"""
import druginfo
drug_dict = druginfo.drug_dict


#xTODO implement elsewhere:
#xTODO How to create a DataFrame of only the unique HOME_MEDICATION values grouped by MRN. NOTE: the only columns will be
# MRN and HOME_MEDICATION. Likewise can be done for CHRONIC_PROBLEMS, then these two DataFrames can be merged together,
#xTODO, I need to see if there is a difference in MRN between these two DataFrames before merging, or else MRN may
# be dropped from one of them
#unqhomemed = nomultivit.HOME_MEDICATION.groupby(nomultivit.MRN).unique().reset_index().explode('HOME_MEDICATION')

#xTODO steps: find all unique vitamin types,
#xTODO: consolidate vitamin D types, i.e. D,D2,D3, D-3 as D. It can appear as D-3
#NOTE it looks like every home med row contains parenthesis
#NOTE vitamin K is very low yield (only 42 hits)
#NOTE Can't ignore B12, B6, B-12 in the parenthetical part since sometimes the name before the parenthesis is unusual
#NOTE every item in HOME_MEDICATION has a parenthetical part except my overwrites
#TODO useful regex pattern that matches whole word that contains a paticular string, example: r'\b(?=\w*calciferol)\w+\b'
#NOTE only one MRN contains 'tnf medication(vitamin-d)' and that MRN also has more explicit entries for vitamin-D


hm_drop_patterns = [r'multivitamin', ]

hm_overwrite_patterns = [(r'(?i:vitamin) A & D', 'vitamin_A, vitamin_D'), #TODO make case-insensitive
                         (r'{}'.format('|'.join(drug_dict['vitamin_d'])), 'vitamin_D'),  #xTODO moved here from vitstringreplace; just go ahead and replace calciferol-containing cells with vitamin-D?
                         (r'estrogens|estradiol', 'estrogen'),
                         (r'(?i:colace|docusate|glycol|polyethylene)', 'constipation_drug'), #TODO make case-insensitive
                         (r'^(?!.*guaifenesin)(?!.*promethazine)(?=.*acetaminophen)(?=.*codeine)', 'acetaminophen_codeine'),
                         (r'^(?=.*acetaminophen)(?=.*(?:tramadol|codone|codeine|propoxyphene))','acetaminophen_opiod'),  #TODO use drug_dict
                         #(r'\b(?:codeine|tramadol)\b', 'opiod'), # see below
                         (r'^(?=.*acetaminophen)(?=.*butalbital)', 'acetaminophen_barbiturate'),
                         (r'^(?=.*aspirin)(?=.*dipyridamole)', 'aspirin_dipyridamole'),  #TODO find other vasodilator/bloodthinners to group with?
                         (r'^(?=.*(?:{meds}))(?=.*codone)'.format(meds='|'.join(drug_dict['NSAID'])), 'NSAID_opioid'),
                         (r'^(?=.*(?:{meds}))(?=.*butalbital)'.format(meds='|'.join(drug_dict['NSAID'])), 'NSAID_barbiturate'),
                         (r'(?:{meds})(?!_)'.format(meds='|'.join(drug_dict['NSAID'])), 'NSAID'),  #TODO be aware that one NSAID is a topical cream, ask dr. torres
                         (r'(?:{meds})(?!_)'.format(meds='|'.join(drug_dict['opioid'])), 'opioid'),
                         (r'tylenol', 'acetaminophen'),  # only because I forget how associated they are in the output, TODO make a replace instead of overwrite? are there tylenol-opioid cases?
                         (r'^(?!.*(?:{antib}))(?=.*(?:{meds}))'.format(antib='|'.join(drug_dict['antibiotic']), meds='|'.join(drug_dict['proton_pump_inhibitor'])), 'proton_pump_inhibitor'),
                         (r'^(?=.*(?:{antib}))(?=.*(?:{meds}))'.format(antib='|'.join(drug_dict['antibiotic']), meds='|'.join(drug_dict['proton_pump_inhibitor'])), 'antibiotic, proton_pump_inhibitor'),
                         #TODO are we interested in consolidating all the antibiotics? assume not. the prior consolidation was meant to separate antibiotics from proton_pump_inhibitors
                         (r'statin', 'statin'),
                         (r'{}'.format('|'.join(drug_dict['thyroid_med'])), 'thyroid_med'),
                         (r'{}'.format('|'.join(drug_dict['antidiabetic'])), 'antidiabetic'),
                         (r'^(?!.*ophthalmic)(?=.*(?:{}))'.format('|'.join(drug_dict['antihypertensive'])), 'antihypertensive'),
                         #TODO for tuesday 21, July: look into furosemide from the word count output; work with unqhomemed
                         # DataFrame; consolidate ophthalmic hypertensives as ophthalmic_med or similar?
                         (r'^(?!.*ophthalmic)(?=.*(?:{}))'.format('|'.join(drug_dict['diuretic'])), 'diuretic'),
                         ]

hm_replace_patterns = [(r'(?<=(?i:vitamin))\s+(?=[A-Za-z]{1})', '_'),  # anything like "vitamin    D" gets replaced with "vitamin-D" #TODO make case-insensitive
                       #(r'(?<=D)-?\d+', ''), # replaces anything after D with ''
                       (r'(?<=vitamin_B)-(?=\d+\b)', ''),  # replace dash in B-12 with ''
                       (r'(?<=vitamin_)[dD]-?\d+\b', 'D'),  # replace D2, D3 preceded by vitamin_ with D
                       #(r'estrogens', 'estrogen'), # decided to overwrite instead
                       #(r'estradiol', 'estradiol (estrogen)'),
                       (r'(?<=(?i:polyethylene))\s+(?=(?i:glycol))', '_'),  # replace whitespace between these two words with an underscore (it won't be stripped in splitstrip) #TODO make case-insensitive
                       (r'(?<=codeine)-|-(?=codeine)', '_'),
                       (r'(codeine-\w+).*', r'\1'),  # replaces match group 1, codeine-<some word>, and anything thereafter with match group 1
                       ]


hm_filtering_list = [(hm_drop_patterns, 'drop'),
                     (hm_overwrite_patterns, 'overwrite'),
                     (hm_replace_patterns, 'replace')]


hm_keyword_list = ['antihypertensive', 'nsaid', 'statin', 'acetaminophen_opiod', 'constipation_drug',
                       'proton_pump_inhibitor', 'antidiabetic', 'acetaminophen', 'opioid', 'vitamin_d', 'diuretic',
                       'thyroid_med', 'calcium', 'alendronate', 'estrogen', 'denosumab', 'ibandronate', 'raloxifene',
                       'risedronate', 'calcitonin', 'pth', 'zoledronic']

exploded_unique_home_med_df = dfutility.dataframeExplodeUniqueValuesInColumnGroupedByIndex(osteodf.HOME_MEDICATION.groupby(osteodf.MRN))
#xTODO lowercase the columns to avoid having to specify case in regex patterns
#dfutility.string.lowercase_str_in_dataframe(hmdf, inplace=True) #TODO test, added 19 Aug, NOTE: can't do because there are still case-sensitive regex patterns used
filthmdf = dfutility.filter_dataframe_column(exploded_unique_home_med_df, 'HOME_MEDICATION', hm_filtering_list)
bool_table_filtered_home_med = dfutility.dataframeBooleanTableKeywordsInListGroupedByIndex(filthmdf.HOME_MEDICATION.groupby(filthmdf.MRN), hm_keyword_list)

#TODO Merge of boolean tables for CHRONIC_PROBLEM and HOME_MEDICATION, in this order :
merged_bool_tables_chronic_problem_home_med = bool_table_filtered_chronic_problem.merge(bool_table_filtered_home_med, on='MRN') # default merge type is 'inner' (key intersection), which is desired

#TODO check that the merge output is not effected by what is used as the input dataframe to generate hmdf, DONE, it
# doesn't matter
#cphmbool.to_csv(os.path.join(fileutility.maketodayfolder(), "withoutOsteoDfpre-filtering.csv"))

#TODO what columns to use from dhr_traumaresearch_osteofractures.xlsx (which was transformed into
# the merged boolean table)? Ans: ['ETHNICITY', 'TOBACCO_USE']
#TODO DON'T USE, DELETE
# osteodf_unique_column_values_groupedby_mrn = dfutility.getUniqueColumnValuesGroupedByIndex(osteodf, 'MRN', ['SEX', 'ETHNICITY', 'TOBACCO_USE', ]) # then of course the rest of the boolean table
# merged_big_bool_tables_and_osteodf_columns = osteodf_unique_column_values_groupedby_mrn.merge(merged_bool_tables_chronic_problem_home_med, on='MRN') # order of merge doesn't matter
# because the merge type is 'inner' (intersection of keys) and because if one of them has less keys, it will be cphmbool

#Pointless, I think:
# hmdf2 = explodeUniqueColumnValuesGroupedByMRN(filtosteodf, 'HOME_MEDICATION')
# filthmdf2 = dataframe_reduce_column(hmdf2, 'HOME_MEDICATION', hm_filter_function_call_list)

########################################################################################################################
"""S-FILES"""
########################################################################################################################
# origsfiledf = fileutility.getSfileDataFrameNamedTuple() # basically useless for anything other than viewing since it is
#                                                         # immutable and cannot be copied into a new namedtuple
#                                                         # (well it's possible but difficult and stupid)
origsfiledict = fileutility.getSfilesDataFrameDict()
concatorigsfiledict = pd.concat(origsfiledict.values()).reset_index()
sfiledict = fileutility.getSfilesDataFrameDict() # fileutility.getSfileDataFrameNamedTuple() # did this because a dict is
                                               # mutable

#xTODO rename columns: uppercase, re.sub non-words (\W) with _
#for df in sfiledf.values(): df.columns = [re.sub(r'\W+','_', item.upper()) for item in df.columns] #xTODO move to getSfilesDataFrameDict. MOVED 28/07
"""Data formatting and exclusions"""
#TODO what columns to use from sfiles? note: there is no smoking column in the sfiles
sfile_columns_to_keep = ['MRN', 'ACCOUNT', 'AGE', 'ADMIT_DATE', 'LENGTH_OF_STAY', 'DIAGNOSIS_CD', 'MECHANISM', 'OTHER_FRACTURES', 'DEXA',
                  'INSURANCE_CLASS', 'ZIP_CODE', 'FILE_NAME', ] # FILE_NAME is created by dfutility.getSfilesDataFrameDict
#xTODO should df = df.drop(columns=[...]) be used instead of df = df[[...]].copy()? YES because the df must contain all
# columns passed to df[[...]].copy(). Use difference() method instead of a difference of sets
# The difference gets dropped.
for key, df in sfiledict.items(): sfiledict[key] = df.drop(columns=df.columns.difference(sfile_columns_to_keep, sort=False))


#TODO modify DEXA values. if null, 0, else 1
for df in sfiledict.values():
    df.loc[df.DEXA.notnull(), 'DEXA'] = 1
for df in sfiledict.values():
    df.loc[df.DEXA.isnull(), 'DEXA'] = 0


#TODO concatenate s-files:
concatsfiledict = pd.concat(sfiledict.values()).reset_index(drop=True) # easier to work with for certain tasks
#xTODO inspect for duplicates:
# duplicate_account_mrn = concatsfiledict[concatsfiledict.set_index(['ACCOUNT', 'MRN']).index.duplicated(keep=False)].reset_index(drop=True).sort_values(by='MRN')
# dfutility.exportDataFrameToExcel(duplicate_account_mrn, "Duplicate Account&MRN, SFile")

"""DATES:"""
#TODO if there are serial dates in 'ADMIT_DATE', convert to datetime
# for df in sfiledict.values(): df.ADMIT_DATE = pd.to_datetime(df.ADMIT_DATE)
# from datetime import datetime
# for df in sfiledict.values(): df.ADMIT_DATE = df.ADMIT_DATE.apply(lambda x: datetime.utcfromtimestamp((x - 25569)*86400.0) if isinstance(x, float) else pd.to_datetime(x))
#TODO export rows where ADMIT_DATE year is 2018 and month < 3 (March):
# concatsfiledict = pd.concat(sfiledict.values()).reset_index()
# dfutility.exportDataFrameToExcel(concatsfiledict.loc[concatsfiledict.ADMIT_DATE.apply(lambda x: x.year == 2018 and x.month < 3), ['ACCOUNT', 'MRN','ADMIT_DATE', 'FILE_NAME']], "AdmitDateBeforeMarch2018")

#-----------------------------------------------------------------------------------------------------------------------
"""Consolidations/fill missing values"""

"""MECHANISM: fill in missing mechanisms, exclude patients with certain mechanisms"""
#TODO lowercase and strip Mechanism columns
for df in sfiledict.values(): df.MECHANISM = dfutility.string.lowercase_str_in_series(df.MECHANISM)

# missing_mechanisms = pd.concat([df.loc[df.MECHANISM.isna(), ['ACCOUNT','MRN','MECHANISM','ADMIT_DATE']] for df in sfiledict.values() if df.MECHANISM.isna().any()])
# missing_mechanisms = concat_origsfiledict.loc[concat_origsfiledict.MECHANISM.isna(), ['ACCOUNT','MRN','MECHANISM','ADMIT_DATE'] ]
# dfutility.exportDataFrameToExcel(missing_mechanisms, "EverySfileMissingMechanisms")
missing_mechanisms_excel = dfutility.simplifyDataFrameColumnHeaders(pd.read_excel(r"C:\Users\nnnwn00\Documents\data\osteo\OUTPUT\30072020\FilledInEverySfileMissingMechanism.xlsx"))[['ACCOUNT', 'MRN', 'MECHANISM']].copy()
dr_torres_unspecified_mech_excel = dfutility.simplifyDataFrameColumnHeaders(pd.read_excel(r"C:\Users\nnnwn00\Documents\data\osteo\OUTPUT\10082020\dr_torres_notes_UnspecifiedOrUncategorizedMechanisms.xlsx"))
# unspecified_mechanisms_excel = dr_torres_unspecified_mech_excel.loc[~dr_torres_unspecified_mech_excel.EXCLUDE, ['ACCOUNT', 'MRN', 'MECHANISM']]
unspecified_mechanisms_excel = dr_torres_unspecified_mech_excel[['ACCOUNT', 'MRN', 'MECHANISM','EXCLUDE']]
missing_mechanisms_excel['EXCLUDE'] = False
filled_in_missing_mechanisms = dfutility.updateFromDataFrame(missing_mechanisms_excel, unspecified_mechanisms_excel, index=['ACCOUNT', 'MRN'], overwrite=True)
filled_in_missing_mechanisms.EXCLUDE = filled_in_missing_mechanisms.EXCLUDE.astype(bool) # I don't know why the pandas update function converts dtype bool to dtype object
# merge_exclude = filled_in_missing_mechanisms.merge(unspecified_mechanisms_excel[['ACCOUNT','EXCLUDE']].copy(), on='ACCOUNT')
valid_filled_in_missing_mechanisms = filled_in_missing_mechanisms[~filled_in_missing_mechanisms.EXCLUDE] # keep only the values where EXCLUDE is not True
updated_mechanism_sfiledict = {key:dfutility.updateNaNFromDataFrame(df, valid_filled_in_missing_mechanisms, index='ACCOUNT') for key, df in sfiledict.items() if df.MECHANISM.isna().any()}
sfiledict.update(updated_mechanism_sfiledict)

#TODO 24: locate rows where sfile Mechanism is undesirable, manually edit excel files, recategorize these as something
# more consistent. strip whitespace in cells?
# unique_mechanisms = [pd.unique(list(itertools.chain(*[df.MECHANISM.unique() for df in sfiledict.values()])))] # for viewing
concatsfiledict = pd.concat(sfiledict.values()).reset_index(drop=True) # easier to work with for certain tasks
unique_mechanisms = concatsfiledict.MECHANISM.unique()
#TODO list of Mechanisms to exclude from elements of unique_mechanisms
mechanism_exclude_patterns = ['bicycle', 'motorcycle', r'^(?=.*fall)(?=.*(?:over|6m))', 'mvc', 'vehicle', 'pedestrian']
mechanism_overwrite_patterns = [('fall', 'fall_under_1m')]
for key, df in sfiledict.items(): sfiledict[key] = dfutility.drop_from_patterns(df, 'MECHANISM', mechanism_exclude_patterns)
for key, df in sfiledict.items(): sfiledict[key] = dfutility.overwrite_from_patterns(df, 'MECHANISM', mechanism_overwrite_patterns)


"""INSURANCE: fill missing insurance information"""
#TODO completed missing zip and insurance file
filled_zip_and_insurance = dfutility.simplifyDataFrameColumnHeaders(pd.read_excel(r"C:\Users\nnnwn00\Documents\data\osteo\sfiles\missing zip and health insurance.xlsx"))
# NOTE not using the zip codes from this file because the ones I pulled from powerchart are the correct ones
#TODO drop duplicate account values in filled_zip_and_insurance. the duplicate account values have the same
# insurance value so it doesn't matter which duplicate account value is dropped:
filled_insurance = filled_zip_and_insurance[['ACCOUNT', 'PRIMARY_PAYOR']].drop_duplicates(subset=['ACCOUNT'])
filled_insurance.rename(columns={'PRIMARY_PAYOR':'INSURANCE_CLASS'}, inplace=True) # need to rename the column for the update operation
updated_insurance_sfiledf = {key:dfutility.updateNaNFromDataFrame(df, filled_insurance, index='ACCOUNT') for key, df in sfiledict.items() if df.INSURANCE_CLASS.isna().any()} # essentially a copy of sfiledf
sfiledict.update(updated_insurance_sfiledf)

#TODO consolidate insurance
for df in sfiledict.values(): df.INSURANCE_CLASS = df.INSURANCE_CLASS.str.lower() # convert to lowercase for stat programs
#TODO export unique insurance values for viewing
# dfutility.exportArrayToExcel(pd.concat(sfiledict.values()).INSURANCE_CLASS.unique(), "UniqueInsuranceValues")

insurance_overwrite_patterns = [(r'^(?=.*(?:\bmc\b|medicare|texan|dual|\bmmp\b))(?=.*\bhmo\b)', 'medicare_hmo'),  # sometimes medicare is not immediately followed by hmo (like in 'medicare blue cross hmo')
                                (r'^(?!.*hmo\b)(?=.*(?:\bmc\b|medicare|dual|\bmmp\b))', 'medicare'),
                                (r'medicaid|star plus', 'medicaid'),
                                (r'\bwc\b|worker', 'workers_compensation'),
                                (r'indigent', 'indigent'),
                                (r'charity', 'charity'),
                                (r'government|municipal', 'government'),
                                (r'^(?=.*self)(?=.*pay)', 'self_pay'),
                                 #TODO which S-file is 'incident r' from??
                                # (r'blue|\bbc\b', 'blue_cross'), (r'united|\buhc\b', 'unitedhealthcare'),
                                # (r'molina', 'molina'), (r'cigna', 'cigna'), (r'superior', 'superior'),
                                #(r'texan', 'texanplus'), (r'triwest', 'triwest'),
                                ]
#TODO overwrite values in INSURANCE_CLASS using insurance_overwrite_patterns
for key, df in sfiledict.items(): sfiledict[key] = dfutility.overwrite_from_patterns(df, 'INSURANCE_CLASS', insurance_overwrite_patterns)
#TODO overwrite any value not overwritten by insurance_overwrite_patterns with 'private_insurance'
for df in sfiledict.values(): df.loc[~df.INSURANCE_CLASS.str.contains(r'|'.join(dict(insurance_overwrite_patterns).values())), 'INSURANCE_CLASS'] = 'private_insurance'


"""ZIP CODES: clean existing zip codes, fill missing zip codes"""
#TODO remove 4-digit extension on zip codes. this is done before replacing missing zip codes because that process will
# unavoidably convert ints to floats, which are more difficult to work with (require additional pattern matching)
#First have to convert ZIP_CODE column to type str (conversion to str doesn't happen in Series.str.contains and I don't know why).
# also because any zip+4 is already a str (that's what pandas converts it to on file read-in):
for df in sfiledict.values(): df.ZIP_CODE = df.ZIP_CODE.astype(str)
#Then use regex to fix unwanted zip code formats/numbers:
for df in sfiledict.values(): df.ZIP_CODE = df.ZIP_CODE.str.replace(r'-\d{4}.*', '') # replaces -1234 with ''
for df in sfiledict.values(): df.ZIP_CODE = df.ZIP_CODE.str.replace(r'\d{6,}', 'nan') # replaces any 6+ digit instances with 'nan', which is then converted to float
for df in sfiledict.values(): df.ZIP_CODE = df.ZIP_CODE.astype(float) #xTODO convert back to int after filling missing values?

#TODO export account #s with missing zip code by sfile for viewing:
# for key, df in sfiledf.items(): dfutility.exportDataFrameToExcel(df.loc[df.ZIP_CODE.isna(),['ACCOUNT','MRN','ZIP_CODE']], "missingZIP_CODE_"+key)
#xTODO create DataFrame from sfiles with missing zip codes: (can export to excel as well)
# missing_zipcodes = pd.concat([df.loc[df.ZIP_CODE.isna(),['ACCOUNT','MRN','ZIP_CODE']] for df in sfiledf.values() if df.ZIP_CODE.isna().any()])
# dfutility.exportDataFrameToExcel(missing_zipcodes, "EverySfileMissingZipCodes")

#xTODO concatenate the missingZIP_CODE files NOTE: replaced with
#missing_zipcodes_df=pd.concat([pd.read_excel(os.path.join(missing_zipcode_root, file)) for file in os.listdir(missing_zipcode_root) if file.startswith('missing')], ignore_index=True)
filled_missing_zipcodes = pd.read_excel(r"C:\Users\nnnwn00\Documents\data\osteo\OUTPUT\29072020\CompletedEverySfileMissingZipCode.xlsx")
updated_zipcode_sfiledf = {key:dfutility.updateNaNFromDataFrame(df, filled_missing_zipcodes, index='MRN') for key, df in sfiledict.items() if df.ZIP_CODE.isna().any()} # essentially a copy of sfiledf
sfiledict.update(updated_zipcode_sfiledf)
for df in sfiledict.values(): df.ZIP_CODE = df.ZIP_CODE.apply(lambda x: int(x) if pd.notna(x) else x)





"""TOBACCO_USE: fill in missing tobacco use for unique MRN"""

#TODO export duplicate MRN for viewing, because a given patient could appear in multiple s-files (has multiple fracture types)
# dfutility.exportDataFrameToExcel(concatsfiledf.loc[concatsfiledf.MRN.duplicated(keep=False),
#                                                    ['MRN','ACCOUNT','FILE_NAME']].sort_values(by=['MRN']),
#                                  "SFileMrnWithMultipleAccountValues")

#TODO merge concatenated s-files with osteodf, which contains the 'TOBACCO_USE' column:
concatsfileosteotobacco = concatsfiledict.merge(osteodf[['MRN', 'TOBACCO_USE']], on='MRN') # using osteodf and not filtered dfs because
# the unique TOBACCO_USE values are identical after the cp filtering
#TODO group TOBACCO_USE of the merged file by MRN, keep only the first element of the unique values array
first_unique_tobacco_groupedby_mrn = concatsfileosteotobacco.TOBACCO_USE.groupby(concatsfileosteotobacco.MRN).unique().apply(lambda arr: arr[0]).reset_index()
#xTODO export TOBACCO_USE grouped by MRN where the value is NaN for viewing:
# na_tobacco = first_unique_tobacco_groupedby_mrn[first_unique_tobacco_groupedby_mrn.TOBACCO_USE.isna()] # don't care about
# dfutility.exportDataFrameToExcel(na_tobacco, "NaNTobaccoGroupedByMRN")

#TODO until IT installs powerchart features to get tobacco info, look into consolidating the non-NaN values:
notna_tobacco = first_unique_tobacco_groupedby_mrn[first_unique_tobacco_groupedby_mrn.TOBACCO_USE.notna()].copy() # using .copy() to avoid the SettingWithCopyWarning warning
notna_tobacco.TOBACCO_USE = notna_tobacco.TOBACCO_USE.str.lower()
notna_tobacco['ORIGINAL_TOBACCO_USE'] = notna_tobacco.TOBACCO_USE
# dfutility.exportArrayToExcel(notna_tobacco.TOBACCO_USE.unique(), "UniqueFirstUniqueTobaccoUseByMRN")
# joinedunique_notna_tobacco = notna_tobacco.TOBACCO_USE.groupby(notna_tobacco.MRN).unique().apply(lambda arr: ', '.join(arr)).apply(lambda string: string.lower()).reset_index() # perform filtering on this
# first_unique_notna_tobacco = notna_tobacco.TOBACCO_USE.groupby(notna_tobacco.MRN).unique().apply(lambda arr: arr[0]).apply(lambda string: string.lower()).reset_index() # perform filtering on this

"""TOBACCO_USE consolidating"""
tobacco_overwrites = [(r'former', 'former'),
                      (r'never', 'never'),
                      (r'^(?=.*(?:heavy|(?:(?<!\.)[2-9]\d(?: per|\/day))))', 'heavy'),
                      (r'smoker|cigar', 'light'), # cigar is a substring of cigarette, so it captures both
                      #(r'^(?=.*(?:light|some|1/[24] pack|(?:(?:\b\d\b|1\d|\.\d+)(?:\/day| per))))', 'light'),
                      (r'^(?!.*(?:{}))'.format('|'.join(['former','never','light','heavy'])), 'unknown/unspecified' ),
                    ] #^(?!.*(?:pack|per))(?=.*(?:smoker|cigar))

filt_notna_tobacco = dfutility.overwrite_from_patterns(notna_tobacco, 'TOBACCO_USE', tobacco_overwrites)
#xTODO view the consolidations:
# dfutility.exportDataFrameToExcel(dfutility.dataframeExplodeUniqueColumnValuesGroupedByIndex(filt_notna_tobacco, 'ORIGINAL_TOBACCO_USE', 'TOBACCO_USE'), "ConsolidatedFirstValueOfUniqueTobaccoUseGroupedByCategory")

for key, df in sfiledict.items(): sfiledict[key] = df.merge(filt_notna_tobacco[['MRN','TOBACCO_USE']].copy(), on='MRN')


"""FINAL MERGE: merge sfiledict values (DataFrames) with big demographic/CHRONIC_PROBLEM/HOME_MEDICATION boolean table"""
#TODO drop undesirable columns:
for key, df in sfiledict.items(): sfiledict[key] = df.drop(columns=['ADMIT_DATE','FILE_NAME'])
#TODO create new dictionary for merged data frames:
merged_sfiles = {key:df.merge(merged_bool_tables_chronic_problem_home_med, on='MRN') for key, df in sfiledict.items()}
#TODO export data frames to excel spreadsheets
for key, df in merged_sfiles.items(): dfutility.exportDataFrameToExcel(df, "aug14_v2_{}_booltable".format(key))


