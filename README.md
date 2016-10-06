[![Build Status](https://travis-ci.org/00firestar00/TnyBot-Discord.svg?branch=master)](https://travis-ci.org/00firestar00/TnyBot-Discord)

This repository is a collection of "bots" with various utilities

The first is `tnyboy.py` which has most of the functionality.

The second is `imagebot.py` which can be used to download all embedded images on specified discord channels.

`oauthbot.py` is a sample of how to run an official discord bot with token.

Lastly `heroku.py` is what is executed if you were to install this on a heroku instance. It requires a Conf Var named `TOKEN` with your bot's token to run. 

In order to use the bots, have a look at [sample_config](https://github.com/00firestar00/TnyBot-Discord/blob/master/sample_config).

The bots expect the config to be located at `../tnybot_config`.
I didn't want to risk accidentally committing credentials to github, so I put it put it outside this repo. 
This can be quickly edited in the associated py files for now.


If you want to build your own bot, you can add or remove the Cogs from TnyBot as required.
Again, I'll make this more configurable in the future.

this is a test for a second commit
