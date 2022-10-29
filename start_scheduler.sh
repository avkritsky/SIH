pip install --upgrade pip >/dev/null 2>&1
pip install --no-cache-dir --root-user-action=ignore -r /var/www/html/sihe/requirements.txt
#tail -f /var/www/html/sihe/requirements.txt
#python /var/www/html/sihe/bot_main.py
taskiq scheduler scheduler:scheduler