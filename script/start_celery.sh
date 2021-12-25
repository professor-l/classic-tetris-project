#!/bin/sh

CELERY_WORKER_RUNNING=1 celery -A classic_tetris_project_django worker -l INFO
