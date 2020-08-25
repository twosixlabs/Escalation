#!/usr/bin/env bash
#make sure your python path is on escos/escalation
python database/csv_to_sql.py penguin_size tests/test_data/penguin_size/penguin_size.csv replace
python database/csv_to_sql.py penguin_size tests/test_data/penguin_size/penguin_size_2.csv append
python database/csv_to_sql.py mean_penguin_stat tests/test_data/mean_penguin_stat/mean_penguin_stat.csv replace
python database/csv_to_sql.py penguin_size_small tests/test_data/penguin_size_small/penguin_size_small.csv replace

sqlacodegen postgresql+pg8000://escalation_os:escalation_os_pwd@localhost:54320/escalation_os --outfile database/models.py



