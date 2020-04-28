import os
import json
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

pwd_path = os.path.realpath(__file__).rstrip("populate_readme.py")
json_file = os.path.join(pwd_path, "json")

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

print(df)

plt.title('Max, Min, Mean & Median')
plt.fill_between(x='date', y1='min', y2='max', alpha=0.4, data=df)
plt.plot(df['date'], df['mean'])
plt.plot(df['date'], df['median'])
plt.grid(linewidth=0.25)
plt.legend(['Mean', 'Median'], loc='upper left')
plt.gcf().autofmt_xdate()
plt.savefig(f"{pwd_path}/../images/fig1.png", format="png")

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))
ax1.plot(df['date'], df['drift_total'])
ax1.set_title('Total Drift')
ax1.grid(linewidth=0.25)
ax2.plot(df['date'], df['drift_daily'])
ax2.set_title('Daily Drift')
ax2.grid(linewidth=0.25)
plt.gcf().autofmt_xdate()
plt.savefig(f"{pwd_path}/../images/fig2.png", format="png")

stat.append(clms)
with open(f'{pwd_path}/../README.md', 'w') as readme_file:
    readme_file.write("# MMR Drift Status\n")
    readme_file.write("\n")
    readme_file.write(f"**Last Updated (UTC):** {datetime.utcnow()}\n")

    readme_file.write(f"![Figure 1](/images/fig1.png)\n")
    readme_file.write(f"![Figure 2](/images/fig2.png)\n")

    header = True
    for row in stat[::-1]:
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
