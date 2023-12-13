#!/bin/bash -v

tmp_dir=$(uuidgen)
src_repo="https://github.com/skosyi/ha-core"
src_branch="nanoleaf_panels"
src_folder="homeassistant/components/nanoleaf_panels"
src_repo_alias="ha-core"
dst_folder="custom_components"

mkdir $tmp_dir
cd $tmp_dir
git clone --depth 1 --branch $src_branch --no-checkout $src_repo
cd $src_repo_alias
git sparse-checkout set $src_folder
git checkout
cd ../..
rsync -r $tmp_dir/$src_repo_alias/$src_folder $dst_folder
rm -rf $tmp_dir
