#!/usr/bin/env bash
for list in *;
do
        for member in `cat $list`
        do
 
                echo "adding member to: $list"
                /home/ni-admin/bin/gam/gam update group ${list}@lists-test.native-instruments.de add member user $member
        done
done
