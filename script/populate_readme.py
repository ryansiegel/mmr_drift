import os
import json
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

pwd_path = os.path.realpath(__file__).rstrip("populate_readme.py")
json_file = os.path.join(pwd_path, "json")


def plots(data_frame, fig_name):
    fig, ax = plt.subplots()
    plt.title('Max, Min, Mean & Median')
    ax.fill_between(x='date', y1='min', y2='max', alpha=0.4, data=data_frame)
    ax.plot(data_frame['date'], data_frame['mean'])
    ax.plot(data_frame['date'], data_frame['median'])
    ax.grid(linewidth=0.25)
    ax.legend(['Mean', 'Median'], loc='lower left')
    fig.autofmt_xdate()
    fig.savefig(f"{pwd_path}../images/{fig_name}_MMMM.png", format="png")

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))
    ax1.plot(data_frame['date'], data_frame['drift_total'])
    ax1.set_title('Total Drift')
    ax1.grid(linewidth=0.25)  
    ax2.plot(data_frame['date'], data_frame['drift_daily'])
    ax2.set_title('Daily Drift')
    ax2.grid(linewidth=0.25)
    plt.gcf().autofmt_xdate()
    fig.savefig(f"{pwd_path}../images/{fig_name}_CHANGE.png", format="png")

sData = {}

for inFile in os.listdir(json_file):
    with open(os.path.join(json_file, inFile), 'r') as in_file:
        if "latest" in inFile:
            continue
        sID = inFile.rstrip(".json")

        jData = json.load(in_file)
        sData[sID] = {}
        for el in jData.get('trainers'):
            ratings = el.get('rating')
            if 'ratings' not in sData[sID]:
                sData[sID]['ratings'] = []
            sData[sID]['ratings'].append(ratings)

stat = []

prev_mean = 0
start_val = 0
for timestamp in sorted(sData.keys()):
    rData = sData[timestamp]['ratings']

    mean_diff = 0
    start_diff = 0

    rMean = statistics.mean(rData)
    if prev_mean != 0:
        mean_diff = round(rMean - prev_mean, 1)
        start_diff = round(rMean - start_val, 1)
        prev_mean = rMean
    else:
        prev_mean = rMean
        start_val = rMean

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")

    new_row = [
        timestamp,
        min(rData),
        max(rData),
        round(rMean, 1),
        mean_diff,
        start_diff,
        round(statistics.median(rData), 1),
        round(statistics.stdev(rData), 1)
    ]

    stat.append(new_row)


clms = ["date",
        "min",
        "max",
        "mean",
        "drift_daily",
        "drift_total",
        "median",
        "stdev"]

df = pd.DataFrame(np.array(stat), columns=clms)
for clm in clms:
    if clm not in "date":
        df[clm] = df[clm].astype(float)

# all time plots
plots(df, "all-time")
# season 1 plots
season1 = (df['date'] > "2020-04-11") & (df['date'] <= "2020-05-11")
plots(df.loc[season1].copy(), "season-1")
# season 2 plots
season2_mask = (df['date'] > "2020-05-12") & (df['date'] <= "2022-01-01")
season2 = df.loc[season2_mask].copy()
season_reset = True
start_mean = 0
for row in season2.head().itertuples():
    if season_reset:
        season2.at[row.Index, 'drift_total'] = 0
        season2.at[row.Index, 'drift_daily'] = 0
        start_mean = row.mean
        season_reset = False
    else:
        prev_mean = season2.at[row.Index-1, 'mean']
        season2.at[row.Index, 'drift_daily'] = round(row.mean - prev_mean, 1)
        season2.at[row.Index, 'drift_total'] = round(row.mean - start_mean, 1)
plots(season2, "season-2")

stat.append(clms)
with open(f'{pwd_path}/../README.md', 'w') as readme_file:
    readme_file.write("# MMR Drift Status\n")
    readme_file.write("\n")
    readme_file.write(f"**Last Updated (UTC):** {datetime.utcnow()}\n")

    readme_file.write("# Season 2\n")
    readme_file.write(f"![Figure 1](/images/season-2_MMMM.png)\n")
    readme_file.write(f"![Figure 2](/images/season-2_CHANGE.png)\n")

    readme_file.write("# Season 1\n")
    readme_file.write(f"![Figure 1](/images/season-1_MMMM.png)\n")
    readme_file.write(f"![Figure 2](/images/season-1_CHANGE.png)\n")

    readme_file.write("# All Time\n")
    readme_file.write(f"![Figure 1](/images/all-time_MMMM.png)\n")
    readme_file.write(f"![Figure 2](/images/all-time_CHANGE.png)\n")

    header = True
    for row in stat[::-1]:
        if not header:
            row[0] = row[0].strftime("%d-%b-%Y")

        row_len = len(row)
        row = str(row)
        row = row.replace("[", "")
        row = row.replace("]", "")
        row = row.replace("'", "")
        row = row.replace(",", "|")
        row = f"|{row}|\n"
        readme_file.write(row)

        if header:
            line = "|:---" * row_len + " |\n"
            readme_file.write(line)
            header = False

