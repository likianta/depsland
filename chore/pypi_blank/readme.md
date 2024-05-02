manually do this:

enter python interactive shell (or ipython):

```sh
import os
from lk_utils import dumps
os.chdir('chore/pypi_blank/index')
dumps({}, 'id_2_paths.pkl')
dumps({}, 'id_2_paths.json')
dumps({}, 'name_2_ids.pkl')
```
