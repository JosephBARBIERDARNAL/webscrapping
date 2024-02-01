import pandas as pd

all_jobs = pd.DataFrame()
paths = ['linkedin.csv', 'hellowork.csv', 'jobteaser.csv', 'welcometothejungle.csv']
for path in paths:
    jobs_data = pd.read_csv(f'www/{path}')
    all_jobs = pd.concat([all_jobs, jobs_data], axis=0)

all_jobs['Keyword'] = 'data science'
print(all_jobs.columns)
all_jobs.to_csv('www/all_jobs.csv', index=False)

print(f'Number of jobs: {len(all_jobs)}')