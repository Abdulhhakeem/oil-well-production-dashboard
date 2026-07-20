def display_results(total_oil, total_gas, total_water, top_five_wells):
    print("==================================================")
    print("        VOLVE FIELD PRODUCTION SUMMARY           ")
    print("==================================================\n")

    print(f"Total Oil Produced:   {total_oil:,.2f} Sm³")
    print(f"Total Gas Produced:   {total_gas:,.2f} Sm³")
    print(f"Total Water Produced: {total_water:,.2f} Sm³")
    print("\n--------------------------------------------------")

    print("🏆 TOP 5 PRODUCING WELLS:")
    print("--------------------------------------------------")
    for well_name, volume in top_five_wells.items():
        print(f"{well_name:<15} {volume:,.2f} sm³")

    print("==================================================")


