EXAMPLES = 100
file_template = X
FILES = 1024
FILE_LEN_LIMIT = 300000
SOURCE_BUCKET = Y
COL = "text"

import numpy as np
import boto3
file_names = np.random.choice(np.arange(FILES), EXAMPLES, replace = False)
line_nos = np.random.choice(np.arange(FILE_LEN_LIMIT), EXAMPLES, replace = False)
import polars

new_filenames = []
lines = []
new_line_nos = []
for file_name, line_no in zip(file_names, line_nos):
    line_no = int(line_no)
    file_name = str(file_name)
    filename = file_template.format(file_name.zfill(5))
    # filename = file_template.format(file_name)
    # download this file
    s3 = boto3.client("s3")
    s3.download_file(SOURCE_BUCKET, filename, filename)
    table = polars.read_parquet(filename)

    # take second line out of the document.
    
    line = table[COL][line_no]
    
    while len(line) < 100:
        line_no += 1
        line = table[COL][line_no]

    new_line_nos.append(line_no)
    lines.append(line)
    new_filenames.append(filename)

benchmark = polars.from_dicts({"filename": new_filenames, "query": lines, "line_no": new_line_nos})
benchmark.write_parquet("substring_benchmark.parquet")

