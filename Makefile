SYS_NAME = sys_django
SYS_VERSION = 3.0
HABOR = evergreen.guardians.one/da1/

.PHONY: bash start start_django


bash:
		docker run -it --rm --name rm_system_DEV \
			-v ${HOME}/dev/rm_sys_django:/rm_sys_django \
			-w /rm_sys_django \
			-e DJANGO_SETTINGS_MODULE=rmsys.settings.deploy_int \
			${HABOR}${SYS_NAME}:${SYS_VERSION} \
			bash


start:
		docker run -d --rm --name rm_system_DEV -p 18000:18000 \
			-v ${HOME}/dev/rm_sys_django:/rm_sys_django -w /rm_sys_django \
			-e DJANGO_SETTINGS_MODULE=rmsys.settings.dev \
			${HABOR}${SYS_NAME}:${SYS_VERSION} \
			/venv/bin/python manage.py runserver 0.0.0.0:18000 &

# run on Official server
start_django:
		docker run -d --rm --name rm_sys_dev --privileged -p 8002:8000 \
			-v ${HOME}/dev/rm_sys_django:/rmsys -v redis_conn:/redis_conn \
			-w /rmsys -e DJANGO_SETTINGS_MODULE=rmsys.settings.dev_official \
			${HABOR}${SYS_NAME}:${SYS_VERSION} \
			/venv/bin/python manage.py runserver 0.0.0.0:8000 &
