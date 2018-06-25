#!/usr/bin/env bash
for list in `cat /var/tmp/sympa-exports/ALL_LISTS`;
do
        for owner in `cat $list`
        do
                echo "adding to: $list"
                /home/ni-admin/bin/gam/gam update group ${list}@lists-test.example.com add owner user $owner
        done
done
