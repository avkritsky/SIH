/usr/local/bin/python -m pip install --upgrade pip
pip install --root-user-action=ignore -r /var/www/html/sihe/requirements.txt
python /var/www/html/sihe/bot_main.py