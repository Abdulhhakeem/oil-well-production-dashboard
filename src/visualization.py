import matplotlib.pyplot as plt
import pandas as pd

def create_top_five_wells_chart(top_five_wells):
    plt.figure(figsize=(10, 6))

    plt.barh(
        top_five_wells.index,
        top_five_wells.values
    )

    plt.grid(axis="x")

    plt.title("Top 5 Oil Producing Wells")
    plt.xlabel("Oil Produced (Sm³)")
    plt.ylabel("Wellbore Name")

    plt.tight_layout()

    plt.savefig("../charts/top_5_oil_producing_wells.png", dpi=300)

    plt.show()
    plt.close()

def create_monthly_trend_chart(
    monthly_trend,
    value_column,
    title,
    y_label,
    filename
    ):
    monthly_trend = monthly_trend.reset_index()
    monthly_trend["Date"] = pd.to_datetime(
        {
            "year": monthly_trend["Year"],
            "month": monthly_trend["Month"],
            "day": 1,
         }
    )

    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly_trend["Date"],
        monthly_trend[value_column],
        marker = "o",
        linewidth= 2
    )

    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.title(title)
    plt.xlabel("Production Date")
    plt.ylabel(y_label)

    plt.tight_layout()

    plt.savefig(
        f"../charts/{filename}.png",
        dpi=300
    )

    plt.show()
    plt.close()

