#!/usr/bin/bash
HOME="/home/skopp/work/2gmail/sympa/"
for list in `cat ${HOME}/lists_to_migrate.txt`;
do
        cd ${HOME}/archives/${list}@lists.native-instruments.de
        for year in *;
        do
                cd ${year}/arctxt
                echo "doing list: ${list} for year: ${year}"
                rename -v -- 's/(\d+)/sprintf("%03d",$1)/e' *
                ${HOME}/gg_migrate_mail.py ${list}@lists.native-instruments.de
                cd ../..
        done
done
