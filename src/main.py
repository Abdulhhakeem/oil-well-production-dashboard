from loader import load_data
from analysis import (
    calculate_total_oil,
    calculate_total_gas,
    calculate_total_water,
    calculate_top_five_wells,
    calculate_monthly_trend,
)
from report import display_results
from visualization import create_top_five_wells_chart, create_monthly_trend_chart

df = load_data("../data/Volve production data.xlsx", sheet_name="Monthly Production Data")

oil = calculate_total_oil(df)
gas = calculate_total_gas(df)
water = calculate_total_water(df)
top_5 = calculate_top_five_wells(df)
# formatted_top_5 = top_5.map("{:,.2f}".format)


display_results(oil, gas, water, top_5)
create_top_five_wells_chart(top_5)

metrics = ["Oil","Gas","Water"]
for metric in metrics:
    metric_trend = calculate_monthly_trend(df, metric)

    title = f"Monthly {metric} Production Trend"
    y_label = f"{metric} Produced (Sm³)"
    filename = f"monthly_{metric.lower()}_trend"

    create_monthly_trend_chart(
        metric_trend,
        metric,
        title,
        y_label,
        filename,
    )