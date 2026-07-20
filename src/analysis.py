def calculate_total_oil(df):
    total_oil= df['Oil'].sum()
    return total_oil

def calculate_total_water(df):
    total_water= df['Water'].sum()
    return total_water

def calculate_total_gas(df):
    total_gas= df['Gas'].sum()
    return total_gas

def calculate_top_five_wells(df):
    grouped_wells = df.groupby('Wellbore name')["Oil"].sum()
    sorted_totals = grouped_wells.sort_values(ascending=False)
    top_5= sorted_totals.head(5)
    return top_5

def calculate_monthly_trend(df, column):
    monthly_group = df.groupby(["Year", "Month"])[column].sum()
    return monthly_group



