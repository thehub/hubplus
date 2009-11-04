#! /bin/sh

python manage.py syncdb

python manage.py execfile psn_import/groups.py
python manage.py execfile psn_import/users.py
python manage.py execfile patch_groups_and_users.py
python manage.py execfile psn_import/passwords.py

#python manage.py execfile psn_import/folders.py
python manage.py execfile psn_import/files.py
python manage.py execfile psn_import/make_admins.py
python manage.py execfile psn_import/patch_tags.py
python manage.py execfile psn_import/documents.py
python manage.py execfile psn_import/strip_stop_tags.py
python manage.py execfile psn_import/group_permissions.py