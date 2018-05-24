
Actual steps
------------

### Requirements:

*   working GAM for domain. (see [Managing Google services (gman.berlin.native)](/pages/viewpage.action?pageId=186770616))
*   access to Sympa's mysql DB
*   access to Sympa WebUI as admin user (listadmin)

### Steps:

#### Export list of mailing lists

on list server local

mysql --database=sympa -e "select name\_list from list\_table where status\_list = 'open'"  | awk '{print $1}' > /var/tmp/sympa-exports/ALL\_LISTS

#### Export owners and editors

```sh
for LIST in \`cat /var/tmp/sympa-exports/ALL\_LISTS\`; do mysql --database=sympa -e "SELECT user\_admin FROM admin\_table WHERE list\_admin = '$LIST' AND role\_admin = 'owner'" |grep -vE 'user\_admin|listsadmin' >> /var/tmp/sympa-exports/owners/${LIST} ; done
```
```sh
for LIST in \`cat /var/tmp/sympa-exports/ALL\_LISTS\`; do mysql --database=sympa -e "SELECT user\_admin FROM admin\_table WHERE list\_admin = '$LIST' AND role\_admin = 'editor'" |grep -vE 'user\_admin|listsadmin' >> /var/tmp/sympa-exports/editors/${LIST} ; done
```
#### Merge editors and owners
```sh
cd /var/tmp/sympa-exports/
diff --brief -r editors owners > diff_lists
awk '{print $2}' diff\_lists |sed -e 's/editors\\///g' > diff\_lists2
for LIST in \`cat diff\_lists2\`; do cat editors/$LIST  owners/$LIST > owners/${LIST}\_2; sort -n owners/${LIST}\_2|uniq > owners/$LIST; rm -vf owners/${LIST}\_2;  done
```
#### Export subscribers

Generate curl link for dumping subscribers, to do that install [https://addons.mozilla.org/de/firefox/addon/cliget/](https://addons.mozilla.org/de/firefox/addon/cliget/) , go to any lists _Admin → Manage Subscribers → right-click on "Dump" → cliget → Copy curl for link_

_

Modify that link: remove "-O" option and single quotes for URL, so it look like this:
```sh
curl --header 'Host: lists.native-instruments.de' --header 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86\_64; rv:52.0) Gecko/20100101 Firefox/52.0' --header 'Accept: */*' --header 'Accept-Language: en-US,en;q=0.5' --header 'Content-Type: application/x-www-form-urlencoded' --header 'Cookie: optimizelyEndUserId=oeu1462546749413r0.4123976101699025; optimizelySegments=%7B%22201635888%22%3A%22ff%22%2C%22202942620%22%3A%22false%22%2C%22202978022%22%3A%22direct%22%2C%223161070189%22%3A%22false%22%2C%223165770183%22%3A%22ff%22%2C%223169660191%22%3A%22direct%22%7D; optimizelyBuckets=%7B%7D; \_ga=GA1.2.646528587.1468846522; mp\_15a0742b5b1954f15f838ce06b01dba4\_mixpanel=%7B%22distinct\_id%22%3A%20%22159a7bea45a30-0090298016b05f8-74256751-1fa400-159a7bea45b93%22%2C%22%24initial\_referrer%22%3A%20%22%24direct%22%2C%22%24initial\_referring\_domain%22%3A%20%22%24direct%22%7D; sympa\_session=96514011538505; sympa\_session=96514011538505' https://lists.native-instruments.de/wws/dump/apple/light -J -L
```
Now export all members using a loop
```sh
for list in \`cat active\_lists.txt\`; do curl --header 'Host: lists.native-instruments.de' --header 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86\_64; rv:52.0) Gecko/20100101 Firefox/52.0' --header 'Accept: */*' --header 'Accept-Language: en-US,en;q=0.5' --header 'Content-Type: application/x-www-form-urlencoded' --header 'Cookie: optimizelyEndUserId=oeu1462546749413r0.4123976101699025; optimizelySegments=%7B%22201635888%22%3A%22ff%22%2C%22202942620%22%3A%22false%22%2C%22202978022%22%3A%22direct%22%2C%223161070189%22%3A%22false%22%2C%223165770183%22%3A%22ff%22%2C%223169660191%22%3A%22direct%22%7D; optimizelyBuckets=%7B%7D; \_ga=GA1.2.646528587.1468846522; wt\_rla=150537973375578%2C2%2C1485267666570; mp\_15a0742b5b1954f15f838ce06b01dba4\_mixpanel=%7B%22distinct\_id%22%3A%20%22159a7bea45a30-0090298016b05f8-74256751-1fa400-159a7bea45b93%22%2C%22%24initial\_referrer%22%3A%20%22%24direct%22%2C%22%24initial\_referring\_domain%22%3A%20%22%24direct%22%7D; sympa\_session=78778869078926; sympa\_session=78778869078926' https://lists.native-instruments.de/wws/dump/${list}/light -J -L > subscribers/${list} ; done
```
#### Create mailinglists

Create mailings on [https://groups.google.com](https://groups.google.com), you need create them manually, if you're using API, LDAP sync will remove them.

#### Migrate owners

use this helper script, you need to be "owners" dir, e.g.
```sh
ni-admin@gman:~/sympa$ tree -L 1
.
├── all2.txt
├── migrate_members.sh
├── migrate_owners.sh
├── owners
├── remove_members.sh
└── subscribers

ni-admin@gman:~/sympa$ cd owners/
ni-admin@gman:~/sympa/owners$ ../migrate_owners.sh

```

**migrate_owners.sh**

#!/bin/bash
for list in \`cat /var/tmp/sympa-exports/ALL_LISTS\`;
do
        for owner in \`cat $list\`
        do
                echo "adding to: $list"
                /home/ni-admin/bin/gam/gam update group ${list}@lists-test.native-instruments.de add owner user $owner
        done
done

#### Migrate subscribers

use this helper script, you need to be "subscribers" dir, e.g.

ni-admin@gman:~/sympa$ tree -L 1
.
├── all2.txt
├── migrate_members.sh
├── migrate_owners.sh
├── owners
├── remove_members.sh
└── subscribers

ni-admin@gman:~/sympa$ cd subscribers/
ni-admin@gman:~/sympa/owners$ ../migrate_members.sh


you may see "ERROR: 409: Member already exists. - duplicate" errors, it's normal, because these users are already added as "owners" before, just ignore them.

this can take a while, at me it was 100 min.

#### Migrate archive mails

copy symp archive dirs to somewhere, cause we will modify the mails, e.g.

cd /home/skopp/work/2gmail/sympa/archives/
for list in \`cat ../lists\_to\_migrate.txt\`; do rsync -avPh root@lists.berlin.native:/var/lib/sympa/wwsarchive/${list}@lists.native-instruments.de . ; done

for migrating to google, we should use this [custom script](https://git-it.bln.native-instruments.de:9999/misc/2gmail/blob/master/group_test.py)

the usage is simple, go "$LIST/$year-month/arctxt" and run script as

group_test.py <LIST MAIL>

e.g. for "apple" mailing lists

cd /home/skopp/work/2gmail/sympa/archives/apple@lists.native-instruments.de/2011-11/arctxt
group_test.py apple@lists.native-instruments.de

To automate these steps this simple bash script can be used, you should run it within "/home/skopp/work/2gmail/sympa/archives/" directory ("rename" tool is used to rename mails from "1" --> "001" so we have better sorting)

**migrate\_mails\_to_sympa.sh**

#!/bin/bash
for list in \`cat /home/skopp/work/2gmail/sympa/lists\_to\_migrate.txt\`;
do
        cd /home/skopp/work/2gmail/sympa/archives/${list}@lists.native-instruments.de
        for year in *;
        do
                cd ${year}/arctxt
                echo "doing list: ${list} for year: ${year}"
                rename -v -- 's/(\\d+)/sprintf("%03d",$1)/e' *
                /home/skopp/work/2gmail/sympa/group_test.py ${list}@lists.native-instruments.de
                cd ../..
        done
done

