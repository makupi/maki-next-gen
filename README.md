# Maki - *Next Generation*
Rewrite of the current discord bot Maki with new database (PostgreSQL) and new features planned. 



### alembic database migration notes
1. alembic init alembic
2. open alembic/env.py
3. add the following after `fileConfig(config.config_file_name)`

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from maki.utils import config as my_config  # isort:skip
from maki.database import db  # isort:skip

config.set_main_option("sqlalchemy.url", my_config.database)
```
and set the `target_metadata` to `db`


[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/A0A015HXK)