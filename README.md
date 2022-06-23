<div style="text-align: center;">
<img src="resources/images/Argus Badge.png" alt="drawing" style="width:100%;"/>
</div>

<br>

Setting up this bot is easy. All you have to do is create a `config.toml` in the root directory like this:

```toml
[bot]

# Bot Token
token = "OaA2MfMzMsgzMTg3MDA5YRE2.trjisg.sI0ds5dX3abh5acbqkLJUQOjseo"

# Whether you want to see more verbose logs.
debug = false
log_type = "Timed"
log_level = "INFO"
sentry = "https://5636365a78d3344a9b0445536b792440447a@o141345.ingest.sentry.io/4747464"


[database]
enabled = true
driver= "mongo"

# This bot requires a URI from a MongoDB you set up.
uri = "mongodb+srv://argus:password123@argus-alpha.abcd.mongodb.net/argus?retryWrites=true&w=majority"
database = "argus"

[global]
name = "Argus"
guild_id = 729148350156134416


```

Then add an .env file with these contents:
```dotenv
STRUCTLOG_SENTRY_LOGGER_LOCAL_DEVELOPMENT_LOGGING_MODE_ON=
STRUCTLOG_SENTRY_LOGGER_CLOUD_SENTRY_INTEGRATION_MODE_ON=
```


Once this is done you can easily start this bot by installing the project locally using `pip`.

```bash
pip install -e .
```

To start the bot simply do this:

```bash
argus start --config config.toml
```

Finally initialize the server by doing:

```
/setup roles
/setup channels
```

If you server is Level 2 boosted then also do:

```
/setup icons
```

Once the channels, roles and icons are set up, you can enable the debating module with this command:

```
/global enable
```

The rest of the commands are self-explanatory, but you can find the [user manual here](https://wiki.opendebates.net/en/argus/manual).

