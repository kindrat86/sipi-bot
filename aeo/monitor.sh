#!/bin/bash
# sipi.bot AEO PR Monitor — checks status of all MCP directory submissions
# Usage: bash ~/projects/sipi-bot/aeo/monitor.sh

echo "=== sipi.bot MCP Directory PRs ==="
echo ""

declare -A PRS=(
  ["punkpeye/awesome-mcp-servers"]="10386"
  ["TensorBlock/awesome-mcp-servers"]="1273"
  ["YuzeHao2023/Awesome-MCP-Servers"]="364"
  ["MobinX/awesome-mcp-list"]="353"
  ["AlexMili/Awesome-MCP"]="155"
)

merged=0; open=0
for repo in "${!PRS[@]}"; do
  pr="${PRS[$repo]}"
  result=$(gh pr view "$pr" --repo "$repo" --json state,mergedAt 2>/dev/null)
  state=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state','UNKNOWN'))" 2>/dev/null)
  merged_at=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('mergedAt') or 'not merged')" 2>/dev/null)
  case "$state" in
    MERGED) merged=$((merged+1)); emoji="✅";;
    OPEN)   open=$((open+1));     emoji="⏳";;
    CLOSED) emoji="❌";;
    *)      emoji="❓";;
  esac
  printf "%-40s %s #%s %s %s\n" "$repo" "$emoji" "$pr" "$state" "$([ "$state" = "MERGED" ] && echo "merged at $merged_at" || echo "")"
done

echo ""
echo "Smithery: $(curl -sL -o /dev/null -w '%{http_code}' https://smithery.ai/servers/kindrat86/sipi-bot 2>/dev/null) — https://smithery.ai/servers/kindrat86/sipi-bot"
echo ""
echo "Summary: $merged merged, $open pending"
