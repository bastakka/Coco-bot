# Coco-bot
Discord bot written in [pycord](https://github.com/Pycord-Development/pycord) API Wrapper

## Instalation
- Create a discord bot application on [discord developer portal](https://discord.com/developers/applications), you can use [this guide](https://discordpy.readthedocs.io/en/latest/discord.html)
- Clone this repository
```
git clone https://github.com/bastakka/Coco-bot.git && cd Coco-bot
```
- Install pip requiremenets (venv recommended)
```
pip install -r requirements.txt
```
- Run bot localy in terminal
```
python3 bot.py
```
or
- Run bot as a systemd service (configurated to /srv/Coco-bot path)
```
sudo cp resources/coco.service /etc/systemd/system/
sudo systemctl enable coco
```
## License
This project is licensed under the GNU GPL v.3 License.
