import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# LOAD NETFLIX DATASET
df = pd.read_csv('netflix_titles.csv')

#DISPLAY FIRST 5 ROWS OF DATASET
print("First five rows of the dataset:")
print(df.head())

#DATASET SIZE
print("\nTotal rows and columns:", df.shape)

#COUNT MOVIES AND TV SHOWS
print("\nCount of movies and Tv shows:")
print(df['type'].value_counts())

#TITLES RELEASED BY YEAR
print("\nTop 10 Release years:")
print(df['release_year'].value_counts().head(10))

#RATINGS ANALYSIS
print("\nTop 10 Ratings:")
print(df['rating'].value_counts().head(10))

#COUNTRY ANALYSIS
print("\nTop 10 Countries:")
print(df['country'].value_counts().head(10))

#MISSING VALUES
print("\nmissing values :")
print(df.isnull().sum())

#MOST COMMON GENRES
print("\nTop 10 genres:")
print(df['listed_in'].value_counts().head(10))

#MOST COMMON DURATIONS
print("\nTop 10 durations:")
print(df['duration'].value_counts().head(10))

# GRAPH 1: MOVIES vs TV SHOWS
plt.figure(figsize=(7,5))
sns.countplot(data=df, x='type')
plt.title("Netflix Movies vs TV Shows")
plt.xlabel("Content Type")
plt.ylabel("Number of Titles")
plt.tight_layout()
plt.savefig("content_type.png")
plt.show()

# GRAPH 2: CONTENT ADDED BY YEAR
df['date_added'] = pd.to_datetime(df["date_added"].str.strip(), format="mixed" , errors="coerce")
df["year_added"] = df["date_added"].dt.year

plt.figure(figsize=(10,5))
df["year_added"].value_counts().sort_index().plot(kind="line")
plt.title("Netflix Titles added by Year")
plt.xlabel("Year Added")
plt.ylabel("Number of Titles")
plt.tight_layout()
plt.savefig("titles_by_year.png")
plt.show()
