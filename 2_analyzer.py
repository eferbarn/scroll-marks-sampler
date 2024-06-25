# %%
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_rank(row):
    rank_position = 10*(len(freq_df) - row.name)
    return f'Top {rank_position}%'

def rzero(number):
    zeroes = len(str(len(df_filtered)))
    result = str(number)
    return result.rjust(zeroes, '0')

with open('./configs/configs.json', 'r') as file:
    configs = json.load(file)
ot_factor = configs['Outlier_Factor']

directory = './historical_data'

files = [f for f in os.listdir(directory) if f.endswith('.csv')]
files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))
files_to_merge = files[-4:]

dataframes = []

for file in files_to_merge:
    file_path = os.path.join(directory, file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

if dataframes:
    merged_df = pd.concat(dataframes, ignore_index=True)
else:
    print("No CSV files found to merge.")

# Sort the DataFrame by 'point'
df_sorted = merged_df.sort_values(by='point').reset_index(drop=True)

# Calculate the number of rows to remove from each end (5%)
n = len(df_sorted)
n_to_remove = int(ot_factor * n)

# Remove outliers (top and bottom 5%)
df_filtered = df_sorted.iloc[n_to_remove:-n_to_remove]

descriptive_stats = df_filtered['point'].describe()
descriptive_stats.to_json('./assets/Descriptive.json', indent=4)

print("Descriptive Statistics:")
print(descriptive_stats, end='\n--------------\n')

# Divide into 10 categories based on index
num_categories = 9
category_size = len(df_filtered) // (num_categories + 1)

# Calculate average points for each category
category_averages = []
for i in range(num_categories):
    start_idx = i * category_size
    end_idx = (i + 1) * category_size
    avg_points = df_sorted.iloc[start_idx:end_idx]['point'].mean()
    category_averages.append(avg_points)

# Add the last category which may have more elements due to integer division
avg_points_last = df_sorted.iloc[end_idx:]['point'].mean()
category_averages.append(avg_points_last)

# Create DataFrame to display results
category_df = pd.DataFrame({
    'Rank': map(
        lambda x: f'{rzero((10-x) * category_size)}' +
        ' - ' + 
        f'{rzero((9 - x) * category_size + 1)}',
        range(0, 10)
    ),
    'Category': [f'Top {10 * (10 - i)}%' for i in range(num_categories)] + 
    ['Top 10%'],
    'Average Marks': category_averages
})

category_df.to_json('./assets/Ranks.json', indent=4)
print(category_df, end='\n--------------\n')

axis_bins = list(
    range(
        0,
        int(descriptive_stats['max']) + 50,
        50
    )
)
bins_count = 50
freq, bins = np.histogram(
    df_filtered['point'],
    bins=np.linspace(
        descriptive_stats['min'],
        descriptive_stats['max'],
        num = bins_count + 1
    )
)

total_freqs = np.sum(freq)
portion_of_freqs = (freq / total_freqs) * 100

freq_df = pd.DataFrame({
    'Marks': bins[1:],
    'Frequency': freq,
    'Freq. Portion': portion_of_freqs
})

freq_df.to_json('./assets/Histogram.json', indent=4)

print(freq_df, end='\n--------------\n')

# Distribution Analysis
plt.figure(figsize=(10, 6))
plt.hist(
    df_filtered['point'], bins=bins_count, edgecolor='k', alpha=0.7, log=True
)
plt.title('Distribution of Marks')
plt.xlabel('Marks')
plt.ylabel('Frequency')
plt.axvline(
    descriptive_stats['50%'],
    color='darkblue',
    linestyle='dashed',
    linewidth=2,
    label=f'Median (50%): {round(descriptive_stats.get("50%"), 2)}'
)
plt.axvline(
    descriptive_stats['mean'],
    color='green',
    linestyle='dashed',
    linewidth=2,
    label=f'Mean: {round(descriptive_stats.get("mean"), 2)}'
)
plt.axvline(
    descriptive_stats['std'],
    color='grey',
    linestyle='dashed',
    linewidth=2,
    label=f'STD: {round(descriptive_stats.get("std"), 2)}'
)
plt.axvline(
    descriptive_stats['max'],
    color='grey',
    linestyle='dashed',
    linewidth=2,
    label=f'Max: {round(descriptive_stats.get("max"), 2)}'
)
plt.axhline(
    freq.max(),
    color='red',
    linewidth=1,
    label=f'Max Freq: {round(freq.max(), 2)} addresses'
)
plt.axhline(
    freq.mean(),
    color='red',
    linestyle='dotted',
    linewidth=1,
    label=f'Average Freq: {int(freq.mean())} addresses'
)
plt.axhline(
    freq.min(),
    color='red',
    linewidth=1,
    label=f'Min Freq: {round(freq.min(), 2)} addresses'
)
plt.xticks(axis_bins, rotation=45, ha='right')
plt.legend()
plt.savefig('./assets/Histogram.jpeg', dpi=300)
plt.show()

plt.figure(figsize=(10, 4))
plt.boxplot(
    df_filtered['point'], 
    vert = False,
    patch_artist=True,
    showmeans=True,
    showfliers=False,
    notch=False,
    widths=0.7,
    boxprops=dict(facecolor='lightblue'),
    whiskerprops=dict(color='gray', linewidth=1.5),
    capprops=dict(color='gray', linewidth=1.5),
    medianprops=dict(color='darkblue', linewidth=2)
)
plt.axvline(
    descriptive_stats['mean'],
    color='green',
    linestyle='dashed',
    linewidth=2,
    label=f'Mean: {round(descriptive_stats.get("mean"), 2)}'
)
plt.axvline(
    descriptive_stats['25%'],
    color='grey',
    linestyle='dashed',
    linewidth=1,
    label=f'Quantile (25%): {round(descriptive_stats.get("25%"), 2)}'
)
plt.axvline(
    descriptive_stats['50%'],
    color='darkblue',
    linestyle='dashed',
    linewidth=2,
    label=f'Median (50%): {round(descriptive_stats.get("50%"), 2)}'
)
plt.axvline(
    descriptive_stats['75%'],
    color='grey',
    linestyle='dashed',
    linewidth=1,
    label=f'The last quarter (75%): {round(descriptive_stats.get("75%"), 2)}'
)
plt.title('Box Plot - Excluding Outliers')
plt.xlabel('Marks')
plt.ylabel('Values')
plt.legend()
plt.savefig('./assets/Box.jpeg', dpi=300)
plt.show()
# %%
