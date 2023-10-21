import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances




job = pd. read_csv('job_excel.csv')
pd.set_option('display.max_columns', None)
print(job.size)

def clean_df(df1):
    col_to_drop = ["EA No.", "Benefits & Others", "Average Processing Time", "Registration No.", "Job Type"]
    df1 = df1.drop(col_to_drop, axis='columns')
    df1 = df1.fillna(0)
    df1.loc[df1["Company Size"] == "1 - 50 Employees", "Company Size"] = 0
    df1.loc[df1["Company Size"] == "51 - 200 Employees", "Company Size"] = 1
    df1.loc[df1["Company Size"] == "201 - 500 Employees", "Company Size"] = 2
    df1.loc[df1["Company Size"] == "501 - 1000 Employees", "Company Size"] = 3
    df1.loc[df1["Company Size"] == "1001 - 2000 Employees", "Company Size"] = 4
    df1.loc[df1["Company Size"] == "2001 - 5000 Employees", "Company Size"] = 5
    df1.loc[df1["Company Size"] == "More than 5000 Employees", "Company Size"] = 6
    df1["Years of Experience"] = df1["Years of Experience"].str.extract('(\d+)').astype(float)

    return df1


def filtering(df1):
    df1 = df1.loc[(df1['Company Size'] > 0) & (df1['Years of Experience'] < 5.0) & (df1['Career Level'] != "Manager")]
    df1 = df1.loc[df1['Job Title'].str.contains('data|scientist|analyst|analytics|science', flags=re.I, regex=True)]
    df1 = df1.loc[df1['Job Content'].str.contains('SPSS|python|sql|tensorflow|pandas|scikit|keras|soup|scrape|statistic', flags=re.I, regex=True)]
    df1.reset_index(drop=True, inplace=True)

    return df1



job = filtering(clean_df(job))
print(job.head(200))
# job.to_csv("filtered_search.csv", sep=',', index=False, encoding='utf-8')
tfidf = TfidfVectorizer(max_features=3000)
print(len(job))


def tfidf_suggestion(title, job):

    string_matrix = tfidf.fit_transform(job['Job Content'])
    job_title2idx = pd.Series(job.index, index=job['Job Title'])
    idx = job_title2idx[title]
    if type(idx) == pd.Series: #Due to the inconsistency of pandas API, there may be a few same title, and pandas might return more than 1 idx
        idx = idx.iloc[0]      #Hence in here we choose to select the first row

    # calculate the pairwise similarities for this movie
    query = string_matrix[idx]
    scores = cosine_similarity(query, string_matrix)

    #Now the array is 1 x N, let's just make it just a 1-D array directly
    scores = scores.flatten()

    # get the indexes of the best match posting

    recommended_idx = (-scores).argsort()[0:30]
    return job[['Job Title','url']].iloc[recommended_idx]


# print(job['Job Title'].iloc[recommended_idx])
tit = "Data Scientist M/F"
rec_job = tfidf_suggestion(tit, job)
print(rec_job)
rec_job.to_csv("rec_job.csv", sep=',', index=False, encoding='utf-8')
