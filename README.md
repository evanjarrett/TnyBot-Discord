There are actually 2 bots in this repo.

The first is `tnyboy.py` which has most of the functionality.

The second is `imagebot.py` which can be used to download all embedded images on specified discord channels.

In order to use the bots, have a look at [sample_config](https://github.com/00firestar00/TnyBot-Discord/blob/master/sample_config).

The bots expect the config to be located at `../tnybot_config`.
I didn't want to risk accidentally committing credentials to github, so I put it put it outside this repo. 
TnyBot uses `[User2]` instead of `[User]`.
These can be quickly edited in the associated py files for now.


If you want to build your own bot, you can add or remove the Cogs from TnyBot as required.
Again, I'll make this more configurable in the future.

