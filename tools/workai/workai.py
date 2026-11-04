"""WorkAI client (workai.horusjsc.com, API at workai-be).

Token lives only in tools/workai/.env (WORKAI_TOKEN=..., git-ignored). Never print it.

Usage:
  python -I tools/workai/workai.py get api/auth/me   (no leading slash: Git Bash rewrites it)
  python -I tools/workai/workai.py post /api/missions body.json
  python -I tools/workai/workai.py put /api/missions/123 body.json

Endpoints (read from the frontend JS bundle, 2026-11-04). {mid}=mission, {wid}=workflow, {tid}=workflow task.
  Missions
    GET    api/missions?page=N            GET api/missions/{mid}
    POST   api/missions                   (project_id, epic_id, assignee_id, summary, description, additional_instructions)
    PUT    api/missions/{mid}             DELETE api/missions/{mid}
    POST   api/missions/{mid}/workflow/generate   body {} -> 202, workflow status pending -> generated (async, ~1-3 min)
    GET    api/missions/{mid}/workflow    (404 "chưa có workflow AI" if none)
    GET    api/missions/{mid}/attachments   DELETE api/mission-attachments/{id}
  Workflows
    GET    api/mission-workflows/{wid}    (tasks, stages, sprint, deadline, status)
    POST   api/mission-workflows/{wid}/tasks            create task
    POST   api/mission-workflows/{wid}/tasks/attach-issue
    GET    api/mission-workflows/{wid}/attachable-issues
    POST   api/mission-workflows/{wid}/approve          (locks mission content; ask the user first)
    POST   api/mission-workflows/{wid}/reject | cancel  DELETE api/mission-workflows/{wid} (purge)
    PATCH  api/mission-workflows/{wid}/sprint
    POST   api/mission-workflows/{wid}/check-acceptance
  Workflow tasks
    PATCH  api/mission-workflow-tasks/{tid}             edit task (summary, assignee, hours, deps...)
    DELETE api/mission-workflow-tasks/{tid}
    PATCH  api/mission-workflow-tasks/{tid}/acceptance  toggle "Yêu cầu nghiệm thu" / reviewer
    POST   api/mission-workflow-tasks/{tid}/acceptance/approve | reject
    POST   api/mission-workflow-tasks/{tid}/feedback
  Epics
    GET    api/projects/{pid}/epics       GET/PUT/DELETE api/epics/{eid}  (PUT also sets current_status = Hiện trạng)
    PATCH  api/epic-acceptance-criteria/{cid}   criterion status / evidence
    POST/GET api/epics/{eid}/mission-suggestions   POST api/mission-suggestion-items/{id}/accept|dismiss
    PATCH  api/epics/{eid}/attach-missions  POST api/epics/{eid}/move-issues
    GET    api/projects/{pid}/members     GET api/epics/{eid}/attachments
  Users / members
    GET    api/users?search=<name>        (user ids; Trần Quang Tùng = 402)
    GET    api/projects/{pid}/members/search?q=   POST api/projects/{pid}/members (add; body likely {user_id, role_ids})
    PUT    api/projects/{pid}/members/{uid} {role_ids}   ("Member" role id in project 81 = 1861)
    A task assignee must be a project member (422 "Người được gán phải là thành viên của dự án").
    DELETE api/missions/{mid} deletes its workflow too; DELETE workflow alone -> 422 unless cancelled.
  Sprints: PUT/DELETE api/sprints/{id}, POST api/sprints/{id}/start|complete, POST api/projects/{pid}/sprints
Frontend pages need cookie sessionToken=<token> (same token); /missions, /projects/{pid}, /dashboard exist.
Bodies (zod schemas in the bundle):
  POST tasks:   {summary*, description, role, final_assignee_user_id, estimated_hours, depends_on_task_ids,
                 dependent_task_ids, insert_on_edge:{source_task_id,target_task_id}}
  PATCH task:   {summary, description, final_assignee_user_id, depends_on_task_ids, estimated_hours,
                 remaining_hours, priority_score}
  PATCH task acceptance: {requires_acceptance: bool, acceptance_reviewer_user_id}
  POST approve: approves AT ONCE (no preview step via API) and ignores `deadline` (tested 2026-11-04: even an
                 invalid value approves). Creates issues (QLDH-…) in the workflow's sprint or Backlog and auto-schedules.
                 Set the deadline on the issues instead: PUT api/issues/{issue_id} {due_date: "YYYY-MM-DD"}.
                 Issue id = task.resulting_issue.id.   PATCH sprint: {sprint_id}
  POST reject/cancel: {reason}   acceptance/reject: {reason*}   feedback: {value: "pass"|"fail"}
Workflow tasks have stage, role, reason, suggested_assignee (AI pick from project members), final_assignee.
Weekly-report subtasks are issues created after approval (not workflow tasks):
  POST api/issues/{issue_id}/subtasks {summary, estimated_hours}  -> subtask takes the parent's assignee
  PUT  api/issues/{id} {description (HTML <p>), due_date}   DELETE api/issues/{id} (subtask)
  After approval an issue's assignee is locked ("đã phân bổ vào lịch"); change it with
  PATCH api/mission-workflow-tasks/{tid} {final_assignee_user_id} (updates the issue). Subtasks do NOT follow
  that change: delete and recreate them. List of created reports: work/workai/weekly_reports.json.
Issue result ("Kết quả") + status:
  PUT  api/issues/{id} {result: "<p>…</p>"}  (or {no_result: true, no_result_reason})
  POST api/issues/{id}/result-links {url, label}   PUT/DELETE api/issue-result-links/{lid}
  GET  api/issues/{id}/transitions -> ids like wf_to_do_done; POST api/issues/{id}/transition {transition_id}
  Issues with requires_result=true need a result before Done. Find an issue: GET api/issues?search=GSDR-1407.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _env():
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def call(method, path, body=None):
    env = _env()
    base = env.get("WORKAI_BASE", "https://workai-be.horusjsc.com").rstrip("/")
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(base + path, data=data, method=method.upper())
    req.add_header("Authorization", "Bearer " + env["WORKAI_TOKEN"])
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "AI-Animation-workai/1.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"raw": txt[:500]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    method, path = sys.argv[1], "/" + sys.argv[2].lstrip("/")
    body = None
    if len(sys.argv) > 3:
        body = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    code, out = call(method, path, body)
    print(code)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
