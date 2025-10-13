# RepoMan

RepoMan is a repository manager for Lliurex and other debian-based distros.
It's focused on simplicity and it lacks some advanced features for repository management.

## Features

RepoMan's main page consists on a simply list of the target distro's main repositories. It lets the user to add new repositories and enable/disable any of them (including the distro's default repositories).

### Enabling/Disabling Repos

As simple as switch on/off the repo.

### Adding a repo

In order to add a repo simply provide name, descriptive text of the repo (optional) and the url. One of RepoMan's amazing powers is to explore an url and get the available repositories from it. Per example, if we need to add LliureX's repositories in the url we could write "http://lliurex.net/xenial" and RepoMan we'll capable of get all the information for us. We can also be more specific writing the target version "http://lliurex.net/bionic bionic-updates" or put the full url of a repo "deb http://lliurex.net/xenial xenial main universe multiverse preschool restricted partner"
