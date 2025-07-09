# st-andrews-dvsvc

A web crawler to discover UK-based domestic violence support services.

## Requirements

 * Charity Register, stored in `resource` folder, with path updated in the `__SCOT_CHARITIES_PATH` variable in `heuristics/dvdvsc_scorers.py`. Retrieved from the [OSCR](https://www.oscr.org.uk/about-charities/search-the-register/download-the-scottish-charity-register/).  © Crown Copyright and database right [2025]. Contains information from the Scottish Charity Register supplied by the Office of the Scottish Charity Regulator and licensed under the Open Government Licence v.3.0. (http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

## Use with Docker

After building the image with `docker compose build`, run `docker compose up` to start four containers:

* `app` (the crawler)
* `db` (the PostgreSQL database server)
* `pgadmin`
* `ollama` (requires nvidia GPU, but other containers should run even if this doesn't)

This automatically loads environment variables from `.env` in the project directory. Set one up as per `example.env`.

To ensure use of `schema_dump.sql` to initialise database, need to remove `db_data` volume using `docker volume rm st-andrews-dvsvc_db_data` before using `up` command.

`docker compose run db pgadmin` will only spin up the database and pgAdmin containers. Access pgAdmin from a browser at port 5051, as specified in `compose.yaml`. The hostname of the database will be the container ID of db container (found by `docker compose ps`).

## Run just the crawler (without Docker)
First, create a virtual environment.
`python3.10 -m venv <env name>`

Then activate the environment.

(MacOS/Linux) `source <env name>/bin/activate>`
(Windows - cmd) `<env name>\Scripts\activate.bat`

Use `deactivate` to exit the environment afterwards. 

In the environment, install requirements.txt (on Lab PCs use psycopg2-binary instead of psycopg2 as PostgresSQL is not installed).

`pip install -r requirements.txt`

Also ensure environment variables in .env are loaded, including DB_HOST = 127.0.0.1. By adding for each environment variable:

(Linux) `export <VAR>=<VALUE>`  to the end of `<env name>/bin/activate` file

(Windows - cmd) `set <VAR>=<VALUE>`  to the end of `<env name>/Scripts/activate.bat` file

and

`unset <VAR>` to the `deactivate` function, if present in the same file as above.
(as seen [here](https://stackoverflow.com/questions/9554087/setting-an-environment-variable-in-virtualenv)).

Specify `./simple-run.sh <output-file>` (Linux/MacOS) or `scrapy crawl dvsvc -o <output-file>`(Windows cmd) for a crawl with plain CSV output. For particular features like job [persistence](https://docs.scrapy.org/en/latest/topics/jobs.html), run using `scrapy crawl dvsvc <args...>`. 

Note: CSV output is only viewable once the crawler has finished. To see in batches, add
`FEED_EXPORT_BATCH_ITEM_COUNT = N` to `dvsvc_crawl/settings.py`, 
and run with file name of format `%(batch_id)d-filename%(batch_time)s.csv`.


## Use in the CS labs

`podman` should be a direct replacement for Docker. `podman-compose` should be installable using `pip`.

## Running LLM on P&N cluster

Follow instructions provided by ITS to access cluster, and set up an interactive job.
Set up python venv and install `scripts/requirements.txt`, again following as advised by ITS, or using the instructions given in the `Run Just the Crawler` section .

Ensuring `starting_links.txt` is in the `resource` folder, run `scripts/download_starting_page_texts.py` to download the page to `resource/starting_page_texts`.

Then run the ollama container in the background, using docker or equivalent, again described in the ITS instructions. Alternatively, you can use apptainer instead, using the instructions [here](https://wiki.cs.st-andrews.ac.uk/index.php?title=Apptainer#Nvidia_container_images), replacing the commands to run llama with the ones in `run_model.sh`.

Finally run `scripts/submit_pages_to_model.py`, which will output the llm responses to `resource/llm_response`.

Export llm responses from cluster to local PC as required.
On the local PC, to convert JSON responses to a collective CSV file, set `directory` and `output_file` paths as appropriate in `scripts/database_reformat.py`, and run that script.

## Cleaned LLM output database
 See README in `llm_out_db` folder.

