import pandas as pd
import numpy as np

# Define the possible values for each field
age_bins = [
    ">16",
    "16-20",
    "21-25",
    "26-30",
    "31-35",
    "36-40",
    "41-45",
    "46-50",
    "51-55",
    "56-60",
    "61-65",
    ">65",
]
genders = ["male", "female", "other"]
act_daytime_profiles = ["dark_night", "morning_fun", "midday_hero", "keeps_walking"]
act_frequency_profiles = ["rarely_acts", "sometimes_acts", "often_acts", "daily_acts"]
most_views_brands = ["brand_1", "brand_2", "brand_3", "brand_4", "brand_5"]
most_views_item_categories = ["electronics", "food", "clothing", "beauty", "household"]

# Define the proportions for gender
gender_proportions = [0.45, 0.45, 0.10]
brand_proportions = [0.4, 0.25, 0.2, 0.1, 0.05]

# Generate the data
np.random.seed(42)  # For reproducibility

df_size = 100

data = {
    "user_id": [f"u_{i+1}" for i in range(df_size)],
    "age_bin": np.random.choice(age_bins, df_size),
    "gender": np.random.choice(genders, df_size, p=gender_proportions),
    "act_daytime_profile": np.random.choice(act_daytime_profiles, df_size),
    "act_frequency_profile": np.random.choice(act_frequency_profiles, df_size),
    "most_views_brand": np.random.choice(most_views_brands, df_size, p=brand_proportions),
    "most_views_item_category": np.random.choice(most_views_item_categories, df_size),
}

# Create the DataFrame
users_acts_brands_network = pd.DataFrame(data)


# Save the DataFrame to a CSV file
users_acts_brands_network.to_csv("users_acts_brands_network.csv", index=False)
