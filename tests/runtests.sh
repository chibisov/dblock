#!/bin/bash
# todo: use vagrant for mysql running

function run_core_tests {
    cd core/
    export PYTHONPATH="$PYTHONPATH:../../../"
    initial_sql="
    CREATE TABLE IF NOT EXISTS test.man (
    	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    	name VARCHAR(100)
    );
	DELETE FROM test.man;
    "
    echo "$initial_sql" | mysql
    nosetests --nocapture
}

function run_django_tests {
    # pip install requirements from tests/django/requirements.txt
    cd django/test_project/
    ./manage.py test dblock_test_app
}


# start_mysql
run_core_tests