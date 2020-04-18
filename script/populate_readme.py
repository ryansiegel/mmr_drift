import os
import json
import statistics
from datetime import datetime

pwd_path = os.path.realpath(__file__).rstrip("populate_readme.py")
json_file = os.path.join(pwd_path, "json")

sData = {}

for inFile in os.listdir(json_file):
    with open(os.path.join(json_file, inFile), 'r') as in_file:
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

stat.append(["date",
             "min",
             "max",
             "mean",
             "drift_daily",
             "drift_total",
             "median",
             "stdev"])


with open(f'{pwd_path}/../README.md', 'w') as readme_file:
    readme_file.write("# MMR Daily Status\n")
    readme_file.write("\n")
    readme_file.write(f"**Last Updated (UTC):** {datetime.utcnow()} ")
    readme_file.write("\n")

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
