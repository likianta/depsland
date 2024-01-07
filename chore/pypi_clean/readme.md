manually do this:

enter python interactive shell (or ipython):

```sh
import os
from lk_utils import dumps
os.chdir('chore/pypi_clean/index')
dumps({}, 'index.pkl')
dumps({}, 'index.json')
dumps({}, 'name_2_ids.pkl')
```
