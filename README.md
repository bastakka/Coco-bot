# Coco-bot
Discord bot written in [pycord](https://github.com/Pycord-Development/pycord) API Wrapper

<p align="center">
  <img src="https://img.shields.io/github/workflow/status/bastakka/Coco-bot/Pylint?style=for-the-badge" alt="Build"/>
  <img src="https://img.shields.io/github/license/bastakka/Coco-bot?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge" alt="Python"/>
  <img src="https://img.shields.io/badge/code%20style-black-black?style=for-the-badge" alt="Black" />
</p>

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
- Run bot as a systemd service (configurated to /srv/Coco-bot path with venv called venv)
```
sudo cp resources/coco.service /etc/systemd/system/
sudo systemctl enable coco
```
## License
This project is licensed under the GNU GPL v.3 License.
