#!/usr/bin/env bash


GITHUB_API="https://api.github.com"

# Array of programming languages
languages=("JavaScript" "C" "Go" "Python")

# Clone top repository by stars for each specified programming language
# for lang in "${languages[@]}"; do
#     echo "Fetching top repository for language: $lang..."
#     repo=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
#                  "$GITHUB_API/search/repositories?q=language:$lang&sort=stars&order=desc&per_page=1" \
#                  | jq -r '.items[0] | .clone_url')
#
#     if [ -n "$repo" ]; then
#         echo "Cloning top $lang repository: $repo"
#         git clone "$repo"
#     else
#         echo "No repository found for $lang."
#     fi
# done

# Clone top 10 repositories by stars for each specified programming language
for lang in "${languages[@]}"; do
    echo "Fetching top repository for language: $lang..."
    repos=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                 "$GITHUB_API/search/repositories?q=language:$lang&sort=stars&order=desc&per_page=10" \
                 | jq -r '.items[] | .clone_url')

    for repo in $repos; do
        git clone "$repo"
    done

done
