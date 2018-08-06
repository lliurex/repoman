# RepoMan API

The API of repoman is mainly focused on RepoMan but it could be used from other projects that need to manipulate repositories in some way.

## list_default_repos()

Lists the default repos from the included json

## list_sources()

Reads the sources.list.d folder and merges it with RepoMan's own information returning a list with all available repos.

## add_repo(name,description,url)

Adds a repo where:

 - name: The name that will be shown in RepoMan

 - description: As the name, it's for informational purposes only

 - url: The url for the repo. The library explores the content of the url and extracts the repository information from it. Valid urls are:

    * http://lliurex.net/xenial
    * http://lliurex.net/xenial xenial-updates
    * deb http://lliurex.net/xenial xenial-updates main
    * ppa:llxdev/xenial

And so on... virtually any possible combination.

## update_repos()

Updates the apt cache through policy kit

## write_repo(repo_data_dict)

Writes the repo to a valid *list file.
It takes a repo_data_dict as input. This dict must have the folowwing structure:

{'name':{'desc':'optional description','url':['list','of',repository','valid','lines']}}

## write_repo_json(repo_data_dict)

As write_repo but for generate the json with the info for RepoMan
