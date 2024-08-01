PROJECT_DIR="/root/projects/board2gram"
cd $PROJECT_DIR

source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart board2gram_bot.service
