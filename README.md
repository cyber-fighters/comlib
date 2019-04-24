# WARNING: DISCONTINUED
# Backyard Comlib

Module to manage data exchange of the pods.

## Development
For deploying a new version, change the hardcoded commit hashes in the `Pipfile.lock` files in the `modules` and `scaffolder` projects.
```bash
sed -i 's\OLDHASH\NEWHASH\g' modules/**/Pipfile.lock
sed -i 's\OLDHASH\NEWHASH\g' scaffolder/main.go
```
