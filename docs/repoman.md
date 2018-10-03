# repoman-cli(1)

## SYNOPSYS
	repoman-cli [OPTIONS] 

## DESCRIPTION
	Manage system repositories.
	
	Mandatory arguments to long options are mandatory for short options too.

	-a, -add [repository url]
		Adds the repository given at repository_url. Repository_url must be:
		* The base url of a repository ( http://lliurex.net/xenial )
		* A partial component url of a repository ( http://lliurex.net/xenial xenial )
		* The full component url of a repository ( deb http://lliurex.net/xenial xenial main universe multiverse preschool restricted partner )
		* The url of a ppa ( ppa://llxdev/xenial )

	-d, --disable [repository name | repository_index]
		Given a repository name or a repositry index disables it

	-e, --enable [repository name | repository_index]
		Given a repository name or a repositry index enables it

	-u, --username [username]
		Repoman needs root privileges in order to modify system sources. If in Lliurex a valid username and password could be given for authenticating avoiding the use of root account.

	-p, --password [password]
		Repoman needs root privileges in order to modify system sources. If in Lliurex a valid username and password could be given for authenticating avoiding the use of root account.

	-s, --server [server_url]
		If in LliureX we can select the target server.

	-l, --list
		List the available repositories

	-ld, --list_disabled
		List the disabled repositories

	-le, --list_enabled
		List the enabled repositories

	-h, --help
		Shows the help message

	Repository indexes for enable and disable repositories are showed by the list options.

## EXAMPLES
	* Add LliureX's ppa:
	repoman-cli -a ppa:llxdev/xenial

	* Disable a repo by name
	repoman-cli -d "Ubuntu"

	* List available repositories
	repoman-cli -l

	* Based on list results enable a repository by index
	repoman-cli -e 1

	* Authenticate from one client to the server and show available repositories
	repoman-cli -s 10.2.1.240 -u netadmin -p netadmin_password --list


## REPORTING BUGS
	Lliurex Github: https://github.com/lliurex/repoman/issues

