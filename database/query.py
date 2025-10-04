import pandas as pd

data = pd.read_csv('database/DOHMH_New_York_City_Restaurant_Inspection_Results_20251004.csv')

def get_restaurant_by_name(name):
    result = data[data['DBA'].str.contains(name, case=False, na=False)]
    print(result[['DBA', 'BORO', 'BUILDING', 'STREET', 'CUISINE DESCRIPTION', 'GRADE', 'VIOLATION DESCRIPTION', 'INSPECTION DATE']].head())

if __name__ == "__main__":
    name = input("Enter restaurant name: ")
    get_restaurant_by_name(name)
