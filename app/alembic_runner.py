# app/alembic_runner.py

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")