#!/usr/bin/env bash
# Commit + push tu dong hang ngay (cron 17:25). Bo qua work/store/_sys/watch (file tam theo may).
# Log: work/store/_sys/auto_commit.log
cd "$(dirname "$0")/.." || exit 1
LOG=work/store/_sys/auto_commit.log
mkdir -p "$(dirname "$LOG")"
exec 9>.git/auto_commit.lock
flock -n 9 || { echo "$(date '+%F %T') ban: dang chay" >> "$LOG"; exit 0; }
{
  echo "== $(date '+%F %T')"
  [ -e .git/index.lock ] && { echo "git dang ban (index.lock), bo qua"; exit 0; }
  git add -A -- . ':!work/store/_sys/watch' ':!work/store/_sys/auto_commit.log'
  if git diff --cached --quiet; then
    echo "khong co thay doi"
  else
    git commit -q -m "Auto commit $(date '+%F %H:%M')

Co-Authored-By: Claude Code <noreply@anthropic.com>" && git log --oneline -1
  fi
  git push 2>&1 | tail -2
} >> "$LOG" 2>&1
