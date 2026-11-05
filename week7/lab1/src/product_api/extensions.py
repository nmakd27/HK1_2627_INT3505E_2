from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
migrate = Migrate()
# Tách khỏi app giúp:
# - nhiều app cùng dùng
# - test tạo app riêng
# không leak config