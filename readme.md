Mysql only.

## As context manager

    from dblock import database_wide_lock as lock

    with lock(connection, 'rebuild_city_profiles_count') as acquired:
        if acquired:
            City.objects.all().rebuild_profiles_count()

## As decorator

    @lock('rebuild_city_profiles_count')
    def rebuild_city_profiles_count(acquired):
        """Some function used in cron job on cluster (2+ servers)"""
        if acquired:
            City.objects.all().rebuild_profiles_count()

## Skipping if already acquired

    # skip if could not acquire lock (by default is false)
    with lock('rebuild_city_profiles_count', is_skip_if_could_not_acquire=True):
        # this section will be skiped if 'rebuild_city_profiles_count' is already acquired by another thread
        City.objects.all().rebuild_profiles_count()

# Django management command mixin
You can use dblock with django management command. Just create mixin like this
    
    # /common_app/utils.py
    import time
    from django.db import connections
    from django.conf import settings


    class LockCommandMixin(object):
        def handle(self, *args, **kwargs):
            if settings.IS_TEST:
                return super(LockCommandMixin, self).handle(*args, **kwargs)
            else:
                with database_wide_lock(
                    lock_name=self.lock_name,
                    connection=connections['default'],
                ) as acquired:
                    time.sleep(3)
                    if acquired:
                        return super(LockCommandMixin, self).handle(*args, **kwargs)

And now you can reimplement syncdb --migrate command:
    
    # /app/management/commands/syncdb_with_lock.py
    from south.management.commands.syncdb import Command as BaseCommand
    from common_app.utils import LockCommandMixin


    class Command(LockCommandMixin, BaseCommand):
        lock_name = 'south_syncdb_with_lock'

Running "./manage.py syncdb_with_lock --migrate" same time in different threads will prevent migrating database by locking this proccess only for one thread.


## Todo: setup.py

## Todo: tests. How to run tests using vagrant

$ cd dblock/
$ va up
$ ./tests/runtests.sh
