# voltex-takeout

voltex-takeout is a work-in-progress save data management tool.

### help wanted!
Due to issues with the stock song database file's encoding there's quite a few songs with rendering issues in their name strings. For example:

* `Love♡sicK` renders as `Love齶sicK`
* `Xroniàl Xéro` renders as `Xroni曦l X齷ro`
* and so on

There's also a few songs whose titles are different when exported to .csv, for example:

* `Alice Maestera feat. nomico` exports as `Alice Maestera`
* `SACRIFICE feat. ayame` exports as `SACRIFICE feat.ayame`
* ... you get the idea, there are quite a few of these

I've fixed any issues using a translation table, but my play data isn't comprehensive and I've probably missed *something*. This tool is still in active development and will be designed with these inconsistencies in mind, but for now, if you happen to spot any mismatches or encoding issues, let me know on the [issues page](https://github.com/lucs100/voltex-takeout/issues) and I'll fix it right away.

### Acknowledgements
* [music_db.json](data/music_db.json) from [sdvx@aspyxhia](https://github.com/asphyxia-core/plugins)
* [songdata.json](data/songdata.json) pulled from [zetaraku's arcade-songs page](https://arcade-songs.zetaraku.dev/sdvx/songs/) (i was too lazy to use their [script](https://github.com/zetaraku/arcade-songs-fetch))
* translation table in [songdb_transform.py](data/songdb_transform.py) from @norikawa's [issue post](https://github.com/22vv0/asphyxia_plugins/issues/14) and @22vv0's [base translation table](https://github.com/22vv0/asphyxia_plugins/blob/kfc/webui/asset/js/songslist.js#L48)