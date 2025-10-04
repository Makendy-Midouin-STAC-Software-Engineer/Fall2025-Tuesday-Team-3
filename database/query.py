import pandas as pd

url = "https://data.cityofnewyork.us/resource/43nn-pn8j.csv"
data = pd.read_csv(url)

def get_restaurant_by_name(name):
    result = data[data['dba'].str.contains(name, case=False, na=False)].copy()
    result['grade'] = result['grade'].fillna('Not Recorded')
    grade_order = ['A', 'B', 'C', 'Not Recorded']
    result['grade'] = pd.Categorical(result['grade'], categories=grade_order, ordered=True)
    result = result.sort_values('grade')
    print(result[['dba', 'boro', 'building', 'street', 'cuisine_description', 'grade', 'violation_description', 'inspection_date']].head(15))

if __name__ == "__main__":
    name = input("Enter restaurant name: ")
    get_restaurant_by_name(name)
