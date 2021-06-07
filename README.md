# tap-builtwith

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [BuiltWith](https://api.builtwith.com/)
- Extracts the following resources:
  - [Trends](https://api.builtwith.com/trends-api)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

### Step 1: Create an API key

Create an API key in BuiltWith

### Step 2: Configure

Create a file called `builtwith_config.json` in your working directory, following [builtwith_config.json](builtwith_config.json). The required parameters is the `api_key`.

This requires a `state.json` file to let the tap know from when to retrieve data. For example:
```json
{
    "bookmarks": {
        "trends": {
            "start_date": "2021-05-26"
        }
    }
}
```
Will replicate data from those dates.

### Step 3: Install and Run

Create a virtual Python environment for this tap. This tap has been tested with Python 3.7, 3.8 and 3.9 and might run on future versions without problems.
```bash
python -m venv singer-builtwith
singer-builtwith/bin/python -m pip install --upgrade pip
singer-builtwith/bin/pip install git+https://github.com/Yoast/singer-tap-builtwith.git
```

This tap can be tested by piping the data to a local JSON target. For example:

Create a virtual Python environment with `singer-json`
```
python -m venv singer-json
singer-json/bin/python -m pip install --upgrade pip
singer-json/bin/pip install target-json
```

Test the tap:

```
singer-builtwith/bin/tap-builtwith --state state.json -c builtwith_config.json | singer-json/bin/target-json >> state_result.json
```

Copyright &copy; 2021 Yoast
