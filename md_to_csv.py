import pandas as pd
import re

file = open(r'C:\Users\d1ves\New-Grad-Positions-2023\README.md', 'r')
data = []

for i, line in enumerate(file):
    if (i > 18):
        temp = line.split('|')
        name = re.findall(r'\[(.*?)\]', temp[1])[0]
        if '~' not in name:
            link = re.findall(r'\((.*?)\)', temp[1])[0]
            position = temp[3]

            data.append([name, link, position])
            
        # print(temp)

df = pd.DataFrame(data, columns=['Company', 'Link', 'Position'])
df.to_csv('new_grad_positions.csv', index=False)
