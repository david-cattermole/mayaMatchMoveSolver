#!/usr/bin/env bash

# NOTE: We pretend to be firefox because otherwise the server won't allow us to download.
cd ./external/archives
wget --user-agent="Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0" \
     --output-document=sparselm-1.3.tgz \
     http://users.ics.forth.gr/~lourakis/sparseLM/sparselm-1.3.tgz

