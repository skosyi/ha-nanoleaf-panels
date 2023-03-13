current_branch=`git rev-parse --abbrev-ref HEAD`
echo current branch: $current_branch

src_repo=https://github.com/skosyi/ha-core
src_branch=nanoleaf_panels
src_folder=homeassistant/components/nanoleaf_panels
dst_folder=custom_components/nanoleaf_panels

# check out the src repo into a new branch
git remote add src_repo $src_repo
git fetch src_repo
git branch src_repo_branch src_repo/$src_branch

# split desired folder into a branch
git checkout -f src_repo_branch
git subtree split --prefix=$dst_folder -b split_folder_branch

# # check out target branch and add all commits in temp branch to the correct folder
git checkout -f $current_branch
git subtree add --prefix=$dst_folder split_folder_branch

# clean up
git branch -d split_folder_branch
git branch -d src_repo_branch
git remote remove src_repo
