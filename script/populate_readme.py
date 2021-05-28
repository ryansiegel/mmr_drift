import os
import json
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


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


def season_plot(df, start_date, end_date, season_name):
    season_mask = (df['date'] > start_date) & (df['date'] <= end_date)
    season_df = df.loc[season_mask].copy()
    season_reset = True
    start_mean = 0
    for row in season_df.itertuples():
        if season_reset:
            season_df.at[row.Index, 'drift_total'] = 0
            season_df.at[row.Index, 'drift_daily'] = 0
            start_mean = row.mean
            season_reset = False
        else:
            prev_mean = season_df.at[row.Index-1, 'mean']
            season_df.at[row.Index, 'drift_daily'] = round(row.mean - prev_mean, 1)
            season_df.at[row.Index, 'drift_total'] = round(row.mean - start_mean, 1)
    print(season_df)
    plots(season_df, season_name)


sData = {}
seasons_calc = {}
for inFile in os.listdir(json_file):
    with open(os.path.join(json_file, inFile), 'r') as in_file:
        if "latest" in inFile:
            continue
        sID = inFile.rstrip(".json")

        jData = json.load(in_file)
        if 'trainers' not in jData:
            continue
        sData[sID] = {}
        for el in jData.get('trainers'):
            ratings = el.get('rating')
            if 'ratings' not in sData[sID]:
                sData[sID]['ratings'] = []
            if ratings > 100:
                sData[sID]['ratings'].append(ratings)

        s = str(jData.get('season',1))
        if s not in seasons_calc:
            seasons_calc[s] = []
        seasons_calc[s].append(datetime.strptime(sID, "%Y-%m-%d"))

seasons = {}
for key in sorted(seasons_calc):
    sorted_list = sorted(seasons_calc[key])
    seasons[key] = {
        'start': sorted_list[0],
        'start_str': sorted_list[0].strftime("%Y-%m-%d"),
        'end': sorted_list[len(sorted_list)-1],
        'end_str': sorted_list[len(sorted_list)-1].strftime("%Y-%m-%d")
    }

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

    backfill = datetime.strptime("2020-06-22", "%Y-%m-%d")
    if backfill == timestamp:
        missing = 27
        for x in range(missing):
            backfill = timestamp + timedelta(days= x + 1)
            change = (321.3 / (missing + 1)) 
            offset = ((change) * (x + 1))
            new_row = [
                backfill,
                round(rMean + offset, 1),
                round(rMean + offset, 1),
                round(rMean + offset, 1),
                round(change, 1),
                round(start_diff + offset, 1),
                round(statistics.median(rData) + offset, 1),
                0,
            ]
            stat.append(new_row)
        prev_mean = rMean + offset
    
    backfill = datetime.strptime("2020-07-20", "%Y-%m-%d")

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

for key in sorted(seasons):
    start = seasons[key]['start_str']
    end = seasons[key]['end_str']
    season_plot(df, start, end, f"season-{key}")


stat.append(clms)
with open(f'{pwd_path}/../README.md', 'w') as readme_file:
    readme_file.write("# MMR Drift Status\n")
    readme_file.write("\n")
    readme_file.write(f"**Last Updated (UTC):** {datetime.utcnow()}\n")

    readme_file.write("# All Time\n")
    readme_file.write(f"![Figure 1](/images/all-time_MMMM.png)\n")
    readme_file.write(f"![Figure 2](/images/all-time_CHANGE.png)\n")

    for key in sorted(seasons)[::-1]:
        readme_file.write(f"# Season {key}\n")
        readme_file.write(f"![Figure 1](/images/season-{key}_MMMM.png)\n")
        readme_file.write(f"![Figure 2](/images/season-{key}_CHANGE.png)\n")

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
