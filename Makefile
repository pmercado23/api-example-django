# Hackathon-Peter Makefile
# Maintained by: Peter

CURDIR = $(realpath $(dir $(firstword $(MAKEFILE_LIST))))

# Rules
all:: install

create_env:
	cd ${CURDIR}
	virtualenv -p python env

install_requirements:
	(. ${CURDIR}/env/bin/activate && pip install -r requirements.txt)

devinstall:	create_env install_requirements

clean:
	rm -rf ${CURDIR}/build ${CURDIR}/dist ${CURDIR}/*.egg-info

cleanall:	clean
	# Nuke the env
	rm -rf ${CURDIR}/env

test:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py test

run:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py runserver

run-docker:
	docker-compose up

migrations:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py makemigrations

migrate:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py migrate

showmigrations:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py showmigrations

shell:
	${CURDIR}/env/bin/python ${CURDIR}/manage.py shell
