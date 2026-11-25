#!/usr/bin/env bash
# Structural validation of the pm-skills plugin. Catches what `claude plugin validate --strict`
# does not: a skill directory without a SKILL.md, skill or agent names that differ from their
# directory or file, a `skills` field that would stop Claude Code from loading every skill, a
# stray marketplace.json, an invalid hooks.json or a UserPromptSubmit hook, a skill without its README.md or its
# Extension points section, a description over the design limit, a malformed glossary or a skill that does not
# point to it, and (when PM_SKILLS_FORBIDDEN_TERMS names a local file of terms) client names in the public
# repository.
#
# Usage: bash tests/validate.sh [repo-root]    (requires jq; bash 3.2 compatible)
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
MANIFEST="$ROOT/.claude-plugin/plugin.json"
RESERVED_PREFIX_RE='^(claude|anthropic|anthropics|cc-plugin)-'
NAME_RE='^[a-z0-9]+(-[a-z0-9]+)*$'
SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
MAX_NAME=64
MAX_DESCRIPTION=400
EXTENSION_POINTS_RE='^(format|scale|rules|steps|terms)$'
ERRORS=0

error() { echo "ERROR: $*"; ERRORS=$((ERRORS + 1)); }
fatal() { echo "ERROR: $*"; exit 1; }

# Prints a top-level scalar from a Markdown file's frontmatter; folded/literal blocks are joined.
frontmatter_value() {
    local key="$1" file="$2"
    awk -v key="$key" -v q="'" '
        NR == 1 { if ($0 != "---") exit; next }
        /^---[ \t]*$/ { exit }
        block && /^[ \t]/ { line = $0; sub(/^[ \t]+/, "", line); out = out (out == "" ? "" : " ") line; next }
        block { exit }
        index($0, key ":") == 1 {
            v = substr($0, length(key) + 2); sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v)
            if (v ~ /^[>|][-+]?$/) { block = 1; next }
            gsub("^[\"" q "]|[\"" q "]$", "", v); print v; exit
        }
        END { if (block) print out }
    ' "$file"
}

# check_component <file> <rel> <expected-name> <label>: frontmatter name and description.
check_component() {
    local file="$1" rel="$2" expected="$3" name description
    if [[ "$(head -1 "$file")" != "---" ]]; then error "$rel: no YAML frontmatter"; return; fi
    name="$(frontmatter_value name "$file")"
    description="$(frontmatter_value description "$file")"
    if [[ -z "$name" ]]; then
        error "$rel: frontmatter name missing"
    elif [[ "$name" != "$expected" ]]; then
        error "NAME MISMATCH $rel: name '$name' differs from '$expected'"
    fi
    if [[ -n "$name" ]] && { ! [[ "$name" =~ $NAME_RE ]] || [[ ${#name} -gt $MAX_NAME ]]; }; then
        error "$rel: name '$name' must be lowercase letters, digits and single hyphens, max $MAX_NAME"
    fi
    if [[ -z "$description" ]]; then
        error "$rel: frontmatter description missing"
    elif [[ ${#description} -gt $MAX_DESCRIPTION ]]; then
        error "$rel: description is ${#description} characters (max $MAX_DESCRIPTION)"
    fi
}

check_plugin() {
    local name version
    name="$(jq -r '.name // empty' "$MANIFEST")"
    version="$(jq -r '.version // empty' "$MANIFEST")"
    PLUGIN="$name@$version"
    if [[ -z "$name" ]]; then
        error "plugin.json: name missing"
    elif ! [[ "$name" =~ $NAME_RE ]]; then
        error "plugin.json: name '$name' must be lowercase letters, digits and single hyphens"
    elif [[ "$name" =~ $RESERVED_PREFIX_RE ]]; then
        error "plugin.json: name '$name' starts with a reserved prefix (claude-, anthropic-, anthropics-, cc-plugin-)"
    fi
    if ! [[ "$version" =~ $SEMVER_RE ]]; then error "plugin.json: version '$version' is not semver"; fi
    if [[ -z "$(jq -r '.description // empty' "$MANIFEST")" ]]; then error "plugin.json: description missing"; fi
    if jq -e 'has("skills")' "$MANIFEST" >/dev/null; then
        error "plugin.json: remove the skills field, so Claude Code loads every skill under skills/"
    fi
    if [[ -e "$ROOT/.claude-plugin/marketplace.json" ]]; then
        error "STRAY marketplace.json next to plugin.json: the marketplace lives in its own repository"
    fi
}

# Every skill ends with an "## Extension points" section: lines "- `<point>`: ..." from the fixed vocabulary, or "None.".
check_extension_points() {
    local file="$1" rel="$2" points point names
    if ! grep -q '^## Extension points[[:space:]]*$' "$file"; then
        error "$rel: no '## Extension points' section"; return
    fi
    points="$(awk '/^## /{ on = ($0 ~ /^## Extension points[ \t]*$/); next } on' "$file")"
    if printf '%s\n' "$points" | grep -q '^None\.'; then return; fi
    names="$(printf '%s\n' "$points" | sed -n 's/^- `\([^`]*\)`[[:space:]]*:.*/\1/p')"
    if [[ -z "$names" ]]; then
        error "$rel: Extension points lists no point as '- \`<point>\`: ...' and does not say 'None.'"; return
    fi
    while IFS= read -r point; do
        [[ -n "$point" ]] || continue
        if ! [[ "$point" =~ $EXTENSION_POINTS_RE ]]; then
            error "$rel: unknown extension point '$point' (format, scale, rules, steps, terms)"
        fi
    done <<< "$names"
}

check_skills() {
    local d
    SKILLS=0
    for d in "$ROOT"/skills/*/; do
        [[ -d "$d" ]] || continue
        d="${d%/}"
        SKILLS=$((SKILLS + 1))
        if [[ ! -f "$d/SKILL.md" ]]; then error "MISSING skills/$(basename "$d")/SKILL.md"; continue; fi
        check_component "$d/SKILL.md" "skills/$(basename "$d")/SKILL.md" "$(basename "$d")"
        check_extension_points "$d/SKILL.md" "skills/$(basename "$d")/SKILL.md"
        if [[ ! -f "$d/README.md" ]]; then error "MISSING skills/$(basename "$d")/README.md"; fi
        if [[ -f "$ROOT/shared/glossary/it.md" ]] && ! grep -qF 'shared/glossary/it.md' "$d/SKILL.md"; then
            error "skills/$(basename "$d")/SKILL.md: no Italian line pointing to shared/glossary/it.md"
        fi
    done
}

check_agents() {
    local f
    AGENTS=0
    for f in "$ROOT"/agents/*.md; do
        [[ -f "$f" ]] || continue
        AGENTS=$((AGENTS + 1))
        check_component "$f" "agents/$(basename "$f")" "$(basename "$f" .md)"
    done
}

check_hooks() {
    local f="$ROOT/hooks/hooks.json"
    [[ -f "$f" ]] || return 0
    if ! jq empty "$f" 2>/dev/null; then error "hooks/hooks.json: not valid JSON"; return; fi
    if jq -e '.hooks | has("UserPromptSubmit")' "$f" >/dev/null 2>&1; then
        error "hooks/hooks.json: no UserPromptSubmit hook, it would run on every prompt"
    fi
}

# Each shared/glossary/<language>.md: tables headed "| English | <Language> | Note |", rows of three cells with the
# first two filled, and no English term twice in the same file.
check_glossaries() {
    local f rel problems
    for f in "$ROOT"/shared/glossary/*.md; do
        [[ -f "$f" ]] || continue
        rel="shared/glossary/$(basename "$f")"
        problems="$(awk '
            function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
            /^\|/ {
                n = split($0, c, "|")
                if (n != 5 || trim(c[5]) != "") { printf "line %d: a row needs three cells\n", NR; next }
                a = trim(c[2]); b = trim(c[3])
                if (a ~ /^-+$/) next
                if (a == "English") { tables++; next }
                if (a == "" || b == "") { printf "line %d: English and translation must both be filled\n", NR; next }
                if (seen[a]++) printf "line %d: English term \"%s\" appears twice\n", NR, a
            }
            END { if (!tables) print "no table headed | English | ... | Note |" }
        ' "$f")"
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then error "$rel: $line"; fi
        done <<< "$problems"
    done
}

# Client names must never reach the public repository; the list itself lives outside it.
check_forbidden_terms() {
    local terms="${PM_SKILLS_FORBIDDEN_TERMS:-}" term hits
    if [[ -z "$terms" ]]; then
        echo "WARN: PM_SKILLS_FORBIDDEN_TERMS is not set: forbidden-term check skipped"
        return 0
    fi
    [[ -f "$terms" ]] || fatal "PM_SKILLS_FORBIDDEN_TERMS: no such file $terms"
    while IFS= read -r term || [[ -n "$term" ]]; do
        if [[ -z "$term" || "$term" == \#* ]]; then continue; fi
        hits="$(cd "$ROOT" && grep -RniF --exclude-dir=.git --exclude-dir=.superpowers --exclude-dir=__pycache__ -- "$term" . || true)"
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then error "FORBIDDEN TERM '$term' in ${line#./}"; fi
        done <<< "$hits"
    done < "$terms"
}

command -v jq >/dev/null 2>&1 || fatal "jq is required (brew install jq / apt-get install jq)"
[[ -f "$MANIFEST" ]] || fatal "missing $MANIFEST"
jq empty "$MANIFEST" 2>/dev/null || fatal "plugin.json is not valid JSON"
jq -e 'type == "object"' "$MANIFEST" >/dev/null || fatal "plugin.json must be a JSON object"

check_plugin
check_skills
check_agents
check_hooks
check_glossaries
check_forbidden_terms

if [[ $ERRORS -gt 0 ]]; then
    echo "FAILED: $ERRORS error(s)"
    exit 1
fi
echo "OK: plugin $PLUGIN with $SKILLS skill(s) and $AGENTS agent(s)"
