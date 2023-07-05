<div style="text-align: center;">
<img src="resources/images/Argus Badge.png" alt="drawing" style="width:100%;"/>
</div>

<br>

<b>Disclaimer: Project <u>Not Maintained</u></b>

Setting up this bot is easy. Invite the bot account to your server first. Then keep note of the guild `id`.
Make sure the server is empty and has the community option enabled. You also have to give the bot admin and the highest role in the server (if you invited the bot with admin permission, drag the role to the top).

Finally make sure you set a rules channel named "rules" and a community updates channel called "community-updates".

Now we can truly begin.

First you have to create a `config.toml` in the root directory of this repository like this:

```toml
[bot]

# Bot Token
token = "OaA2MfMzMsgzMTg3MDA5YRE2.trjisg.sI0ds5dX3abh5acbqkLJUQOjseo"

# Whether you want to see more verbose logs.
debug = false

# When you'r ready to release.
# Logs will be larger and last longer in production.
production = true

[logs]

# Default Logging Level
level = "INFO"

# Sentry DSN
sentry = "https://5636365a78d3344a9b0445536b792440447a@o141345.ingest.sentry.io/4747464"


[database]

# This bot requires a URI from a MongoDB you set up.
uri = "mongodb+srv://argus:password123@argus-alpha.abcd.mongodb.net/argus?retryWrites=true&w=majority"

# Name of the database.
name = "argus"

[global]

# Name of the bot you want rendered.
name = "Argus"

# The Discord Snowflake for the guild the bot is in.
guild_id = 729148350156134416
```

Once this is done you can easily start this bot by installing the project locally using `pip`.

```bash
pip install -e .
```

To start the bot simply enter this:

```bash
argus
```

Sync commands to the server by sending this in any channel:

```
$sync
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

