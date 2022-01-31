# AUTHOR: William Noonan

"""
General purpose pandas DataFrame utility functions
#TODO 19 Aug, consolidate all similar functions into "namespaces"? see string class below
"""

import pandas
from multipledispatch import dispatch

import utility
import fileutility


def drop_from_patterns(dataframe, column, regex_pattern_list, resetindex=True, inplace=False):
    # Consumes a list of regex patterns, dropping rows of dataframe where patterns match a value in the user-specified column.
    # xTODO output needs to have index reset, regardless if the drop kwarg 'inplace' is true or not
    # TODO remove kwarg 'resetindex' and just do it anyways?
    # TODO rename to filterRowsByRegex
    if not inplace:
        dataframe = dataframe.copy()
    for pattern in regex_pattern_list:
        print(f"Dropping rows where {column} contains '{pattern}'")
        dataframe.drop(dataframe[dataframe[column].str.contains(pattern, na=False, case=False)].index, inplace=True)
        # NOTE: it doesn't effect the end result if the index is reset in this loop or not
    if resetindex:
        dataframe.reset_index(drop=True,
                              inplace=True)  # drop=True prevents the index from being inserted as a new column
    if not inplace:
        return dataframe


def replace_from_patterns(dataframe, column, regex_tuple_list, inplace=False):
    """
    Consumes a list of regex patterns, replacing text string values in the user-specified column where the patterns match.
    :param dataframe:
    :param column:
    :param regex_tuple_list:
    :param inplace: If False (default), return a copy of the dataframe
    :return:
    """
    if not inplace:
        dataframe = dataframe.copy()
    for pattern, repstring in regex_tuple_list:
        print(f"Replacing values in {column} that contain '{pattern}' with '{repstring}'")
        dataframe[column] = dataframe[column].str.replace(pattern, repstring, case=False)
    if not inplace:
        return dataframe


def overwrite_from_patterns(dataframe, column, regex_tuple_list, inplace=False):
    # Overwrites values in a DataFrame column from a list of tuples of regex patterns and strings.
    # regex_tuple_list is a list of tuples like so: [(regex_pattern1, string1),...,(regex_patternN, stringN)]
    if not inplace:
        dataframe = dataframe.copy()
    for pattern, string in regex_tuple_list:
        print(f"Overwriting values in {column} that contain '{pattern}' with '{string}'")
        dataframe.loc[dataframe[column].str.contains(pattern, na=False, case=False), column] = string
    if not inplace:
        return dataframe


def filter_dataframe_column(dataframe, column, iterable):
    # Performs filtering actions on the column of a dataframe according to an iterable of regex iterables and action identifiers.
    # Acceptable action identifiers are 'drop', 'replace', and 'overwrite', which specify the drop_from_patterns,
    # replace_from_patterns, and overwrite_from_patterns functions.
    # Returns a DataFrame
    # TODO inplace kwarg?
    result = dataframe  # don't need to copy it because this is done in the functions
    for regexiterable, id in iterable:
        if id == 'drop':
            function = drop_from_patterns
        elif id == 'replace':
            function = replace_from_patterns
        elif id == 'overwrite':
            function = overwrite_from_patterns
        else:
            raise ValueError(f"'{id}' is an invalid action identifier")
        result = function(result, column, regexiterable)
    return result


@dispatch(pandas.core.groupby.generic.SeriesGroupBy)
def tuplelistUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, n=None, dropnumbers=True):
    """
    Returns a list of tuples, like [(value1, count1, relfreq1), ... , (valueN, countN, relfreqN)], which is ordered
    from the most to least frequent value (descending order).
    Keyword args: dropnumbers is used to exclude numbers from the output (they're excluded by default); n is a kwarg
    of utility.item_counts, it's used to specify how many tuples to return (like the top 10 if n = 10), it
    defaults to None (all tuples are returned)
    """
    import numpy as np
    from itertools import chain
    import stringutility
    index_size = groupbyobj.unique().size
    unique_values_per_index = groupbyobj.unique().apply(stringutility.split_and_chain).apply(
        np.unique).values  # array of arrays of unique values
    chained_unique_values_per_index = list(chain.from_iterable(unique_values_per_index))
    list_of_unique_value_count_tuples = utility.item_counts(chained_unique_values_per_index,
                                                            n)  # item_counts returns a list of tuples, (item, count)
    if dropnumbers:  # if numbers are to be excluded from the output
        list_of_unique_value_count_tuples = [tup for tup in list_of_unique_value_count_tuples if
                                             not utility.is_int(tup[0])]
    value_list, count_list = zip(*list_of_unique_value_count_tuples)  # unpacks the tuples into individual lists
    relative_frequency = np.array(
        [count / index_size for count in count_list])  # putting in np.array for future convenience
    list_value_count_relfreq_tuples = list(
        zip(value_list, count_list, relative_frequency))  # (value, count, freq)
    return list_value_count_relfreq_tuples


@dispatch(pandas.core.frame.DataFrame, str, str)
def tuplelistUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(dataframe, column, index, n=None,
                                                                     dropnumbers=True):
    # Returns a list of tuples, like [(value1, count1, relfreq1), ... , (valueN, countN, relfreqN)], which is ordered
    # from the most to least frequent value (descending order).
    # Keyword args: dropnumbers is used to exclude numbers from the output (they're excluded by default); n is a kwarg
    # of utility.item_counts, it's used to specify how many elements/tuples to return (like the top 10 if n = 10), it
    # defaults to None (all elements are returned)
    groupbyobj = dataframe[column].groupby(dataframe[index])
    return tuplelistUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, n=n, dropnumbers=dropnumbers)


@dispatch(pandas.core.groupby.generic.SeriesGroupBy)
def dataframeUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, n=None, dropnumbers=True):
    #
    import os, pandas
    columns = ["value", "count", "relative_frequency"]
    df = pandas.DataFrame(
        tuplelistUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, n=n, dropnumbers=dropnumbers),
        columns=columns)
    return df


@dispatch(pandas.core.frame.DataFrame, str, str)
def dataframeUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(dataframe, column, index, n=None,
                                                                     dropnumbers=True):
    groupbyobj = dataframe[column].groupby(dataframe[index])
    return dataframeUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, n=n, dropnumbers=dropnumbers)


@dispatch(pandas.core.groupby.generic.SeriesGroupBy)
def dataframeExplodeUniqueValuesInColumnGroupedByIndex(groupbyobj):
    # Groups DataFrame column by index, explodes the index
    # column and index must be strings
    # Returns a DataFrame
    return groupbyobj.unique().explode().reset_index()


@dispatch(pandas.core.frame.DataFrame, str, str)
def dataframeExplodeUniqueValuesInColumnGroupedByIndex(dataframe, column, index):
    groupbyobj = dataframe[column].groupby(dataframe[index])
    return dataframeExplodeUniqueValuesInColumnGroupedByIndex(groupbyobj)


@dispatch(pandas.core.groupby.generic.SeriesGroupBy, list)
def dataframeBooleanTableKeywordsInListGroupedByIndex(groupbyobj, keywordlist, case=False):
    """
    Creates a dataframe whose columns are the strings in keywordlist. The column of dataframe is grouped by index,
    producing lists of unique values per index. Each string in keywordlist is examined for containment in these lists,
    yielding a 1 for containment, 0 otherwise.
    Returns a DataFrame
    """
    import pandas as pd
    import numpy as np
    import stringutility
    from itertools import chain
    keywordlist = [word.lower() if not case else word for word in keywordlist]
    grouping_name = groupbyobj.keys.name
    columns = [grouping_name] + keywordlist  # cannot use list(grouping_name), because that unpacks a string into a list
    unique_strings_groupedby_index = groupbyobj.unique().apply(stringutility.split_and_chain, case=case).apply(
        np.unique)  # (uwlbm) Series, index: unique MRN, values: numpy array of unique words (produced by splitandchain)
    boolean_list_keyword_isin_usgbi = unique_strings_groupedby_index.apply(
        lambda item_list: [1 if word in set(item_list) else 0 for word in
                           keywordlist])  # this is a value-for-value (non-regex) match, sets are best for containment checks
    zipchain_keyword_boolean_list = [list(chain.from_iterable(item)) for item in list(
        zip([[index] for index in boolean_list_keyword_isin_usgbi.index], boolean_list_keyword_isin_usgbi.values))]
    keyword_boolean_df = pd.DataFrame(zipchain_keyword_boolean_list,
                                      columns=columns)  # can only concatenate list (not "set" or "tuple") to list, which
                                                        # is why I forced keywordlist to be a list
    return keyword_boolean_df


@dispatch(pandas.core.frame.DataFrame, str, str, list)
def dataframeBooleanTableKeywordsInListGroupedByIndex(dataframe, column, index, keywordlist, case=False):
    keywordlist = list(keywordlist)
    groupbyobj = dataframe[column].groupby(dataframe[index])
    # TODO replace np.unique with pd.unique?
    return dataframeBooleanTableKeywordsInListGroupedByIndex(groupbyobj, keywordlist, case=case)


def updateFromDataFrame(tgtdataframe, srcdataframe, index=None, overwrite=True, inplace=False):
    """
    Update a DataFrame with another DataFrame on index, which can be specified (defaults to dataframe.index); overwrite
    behavior can be specified (default is overwrite everything).
    Returns a DataFrame if inplace is False (default), modifies passed DataFrame if inplace is True
    """
    if not inplace:
        tgtdataframe = tgtdataframe.copy()
    if not index:
        index = tgtdataframe.index
    tgtdataframe.set_index(index, inplace=True)
    reindex_srcdataframe = srcdataframe.set_index(index)  # set index (copy)
    reindex_srcdataframe = reindex_srcdataframe[
        ~reindex_srcdataframe.index.duplicated(keep='first')]  # ignore duplicates
    tgtdataframe.update(reindex_srcdataframe, overwrite=overwrite)
    tgtdataframe.reset_index(inplace=True)
    if not inplace:
        return tgtdataframe


def updateNaNFromDataFrame(tgtdataframe, srcdataframe, index=None, inplace=False):
    # Update a DataFrame from other DataFrame on index, which can be specified (defaults to dataframe.index); only
    # overwrites NaN values.
    # Returns a DataFrame if inplace is False (default), modifies passed DataFrame if inplace is True
    result = updateFromDataFrame(tgtdataframe, srcdataframe, index=index, overwrite=False, inplace=inplace)
    if not inplace:
        return result


# TODO just export DataFrame returned by dataframeUniqueValueCountRelativeFrequencyInColumnGroupedByIndex to excel
def exportUniqueValueCountRelativeFrequencyFromGroupbyObjectToExcel(groupbyobj, fname, n=None, **kwargs):
    # Exports to an Excel spreadsheet the counts and relative frequency of unique values from a pandas groupby object
    import os
    import pandas
    from pandas.io.excel import ExcelWriter
    columns = ["value", "count", "relative_frequency"]
    df = dataframeUniqueValueCountRelativeFrequencyInColumnGroupedByIndex(groupbyobj, columns=columns, n=n)
    path = os.path.join(fileutility.maketodayfolder(), fname)  # TODO setup and path dependency
    with ExcelWriter(path) as writer:
        df.to_excel(writer, index=False, **kwargs)
    print(f"Saved unique word counts to {path}")


def backupDataFrameToCSV(dataframe, message=None):
    # Backs up (exports) DataFrame to OUTPUTROOT path specified in fileutility
    # Writes a 'readme' for the export if message is passed
    import os
    import fileutility, timeutility
    fname = "df{}".format(timeutility.gettimenow())
    fullfname = f'{fname}.csv'
    targetroot = fileutility.maketodayfolder(root=os.path.join(fileutility.OUTPUTROOT, "backup"))  # TODO this is messy
    if message:
        if not isinstance(message, str):
            raise ValueError('message must be a string')
        else:
            import textwrap
            with open(os.path.join(targetroot, f'readme_{fname}.txt'), 'wt') as fout:
                fout.write(textwrap.fill(message, 80))
    targetpath = os.path.join(targetroot, fullfname)
    dataframe.to_csv(targetpath, index=False)
    print(f"Saved {fullfname} to {targetpath}")


def exportDataFrameToExcel(dataframe, excelname, index=False):
    # Exports a DataFrame to an Excel spreadsheet
    # DataFrame index is excluded from export if index is False (default), included if True
    import os
    import fileutility
    path = os.path.join(fileutility.maketodayfolder(), excelname + '.xlsx')
    dataframe.to_excel(path, index=index)
    print(f"Exported DataFrame to {path}")


def exportArrayToExcel(array, excelname):
    # Exports the passed array to an Excel spreadsheet
    import os, fileutility
    import pandas as pd
    # TODO allow .csv or .xlsx inputs?
    # TODO allow user to pass in specific path; if just filename, use setup.maketodayfolder
    columns = ["value"]
    df = pd.DataFrame(array, columns=columns)
    path = os.path.join(fileutility.maketodayfolder("valuematches"), f"{excelname}.xlsx")
    df.to_excel(path, index=False)  # TODO setup and path dependency
    print(f"Saved value matches to {path}")


def listExcelFileSheetNames(excelfile):
    # Note works for .xls as well (because read_excel does too)
    import pandas as pd
    return pd.ExcelFile(excelfile).sheet_names


# TODO a generic method
def getDictDataFramesFromExcelFilesInFolder():
    pass


def simplifyDataFrameColumnHeaders(dataframe, case='upper', inplace=False):  # TODO move to string class
    # Removes non-word characters from DataFrame column headers, converts case to upper (default) or lower case
    # Returns a DataFrame if inplace is False (default), modifies passed DataFrame if inplace is True
    import re
    if not inplace:
        dataframe = dataframe.copy()

    def raise_exception(exception):
        raise exception

    pattern = r'\W+'  # matches 1 or more non-word characters (dash, comma, parenthesis, whitespace, etc.)
    dataframe.columns = [
        re.sub(pattern, '_', item.strip().upper()) if case == 'upper' else re.sub(pattern, '_', item.strip().lower())
        if case == 'lower' else raise_exception(ValueError("Invalid input, case must be of type str."))
        for item in dataframe.columns]  # replacement is an underscore because it's a word character
    if not inplace:
        return dataframe


class string:
    """Behaves like a namespace"""

    def __init__(self):
        pass

    @classmethod
    def lowercase_str_in_series(cls, series):
        # Lowercases (and strips) only the str instances in a pandas Series (ignores NaN)
        return series.apply(lambda value: value.strip().lower() if isinstance(value, str) else value)

    @classmethod
    def lowercase_str_in_dataframe(cls, dataframe, inplace=False):
        if not inplace:
            dataframe = dataframe.copy()
        for col in dataframe.columns:
            dataframe[col] = cls.lowercase_str_in_series(dataframe[col])
        if not inplace:
            return dataframe

    @classmethod
    def replace_yes_no_in_series_with_bool(cls, series):
        return [True if isinstance(value, str) and value.strip().lower() == "yes" else
                (False if isinstance(value, str) and value.strip().lower() == "no" else value) for value in series]

    @classmethod
    def replace_yes_no_in_dataframe_with_bool(cls, dataframe, inplace=False):
        if not inplace:
            dataframe = dataframe.copy()
        for col in dataframe.columns:
            # dataframe[col] = dataframe[col].apply(True if isinstance(value, str) and value.strip().lower() == "yes" else (
            #     False if isinstance(value, str) and value.strip().lower() == "no" else value))
            # Supposedly a list comprehension is faster, idk:
            dataframe[col] = cls.replace_yes_no_in_series_with_bool(dataframe[col])
        if not inplace:
            return dataframe
