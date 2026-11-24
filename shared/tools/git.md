# Known pitfalls: local git clones

Read by skills and agents that read a `code` tool from a local clone, declared as `file:<path>` or used as the
fallback when the hosting service's CLI cannot be reached. A clone gives commits only, with no pull requests or
reviews, and only as fresh as its last fetch.

- **Find the clones.** The git repositories in the project folder and below it, up to three levels
  (`find <folder> -maxdepth 4 -name .git`; `.git` is a file in worktrees and submodules), and the paths the tools
  register or the instruction files name. A clone matches `github:<owner>/<repo>` when `git -C <dir> remote -v`
  lists `github.com/<owner>/<repo>` or `github.com:<owner>/<repo>`, with or without `.git`, in any case.
- **Read, never write.** No `git fetch`, `pull`, `checkout` or any other command that changes the clone. One `git`
  command per call, pointed at the folder with `-C`, without pipes.
- **Freshness.** `git -C <dir> log -1 --all --format=%cI` is the date of the newest commit the clone holds; report it.
- **Counts.** Per author for the window, by commit date: `git -C <dir> shortlog -sne --all --no-merges --since=<start>`
  (take the numbers as they are, never count lines yourself); latest date per author:
  `git -C <dir> log --all --no-merges --since=<start> --format=%cs%x09%aE`.
- **Attribution.** Map an author email, in any case, to the team member whose `Git` column lists it, or whose GitHub
  login it carries as a no-reply address (`<login>@users.noreply.github.com`,
  `<digits>+<login>@users.noreply.github.com`). Never map by author name. Leave out bots (names or emails containing
  `[bot]`, and `noreply@github.com`).
- **Report it as such.** A source read from a clone is `local git: <path>, newest commit <date>, commits only`, not
  `ok`: commits leave out reviews, and the clone may be stale.
