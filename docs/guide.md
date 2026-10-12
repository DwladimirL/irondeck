# How IronDeck works

This guide explains the pieces of IronDeck, the Claude Code orchestrator for Windows, and how a job moves from start to finish. IronDeck is in development: what's described here already exists in the code, and details may change before launch.

[Versión en español](guia.md) · [Back to the start](../README.md)

## Who it's for

For people who already work with Claude Code and want to hand off long jobs: building part of an app, tuning a skill, reviewing a project. You decide what gets done and review the finished work. IronDeck runs the tasks, waits, retries, watches your plan, and tells you when it needs you.

## The pieces

| Piece | What it is |
|---|---|
| **Project** | A repository you work in, with its own window in IronDeck. |
| **Flow** | The steps of a job, in order. For example: research, design, build, review. |
| **Step** | One part of a flow, with its own model (Sonnet, Opus…), effort, permissions and the context it may read. |
| **Task** | One run of Claude Code for a step. Each task works in its own copy of the project, so it never steps on your work. |
| **Inbox** | Where the decisions that are yours wait: merging a change, going past the weekly cap, what to do after a second failure. |
| **Library** | Your skills and templates, with every version. |
| **Evaluation** | A comparison between two versions of a skill on the same cases. |
| **Billing guard** | The check that decides what can be billed: your plan only, or also your account's extra usage up to your cap. |

## A job from start to finish

1. **You pick a project and a flow.** You can start from a template; it adapts to your project.
2. **IronDeck runs the first task.** It prepares a working copy and runs Claude Code with that step's model and effort. It can run up to four tasks at once. Steps run in order; passing each step's result to the next comes in the current phase.
3. **If something fails, it retries.** A task fails when it ends with an error or a partial delivery. The second attempt uses a larger model when there is one; a denied permission stops it without a retry. If that fails too, the decision goes to your inbox.
4. **When a step finishes with changes, it proposes merging them.** Nothing reaches your main branch without your yes.
5. **If you hit your plan limit, it pauses.** That isn't a failure: it resumes on its own after the reset. If you allowed extra usage, it keeps going up to your cap.
6. **If you close IronDeck or the PC shuts down, you don't lose progress.** When you open it again, it reruns the interrupted step; finished steps aren't repeated.

## How it controls spend

- **You choose how it's paid.** By default, plan only: before running it checks which account Claude Code will use, and while the task runs it stops it as soon as it sees an API key or Claude Code reports usage that would be billed separately. If you'd rather it not stop, you'll be able to allow your account's extra usage up to a spending cap; that mode arrives before launch. IronDeck doesn't use API keys.
- **It shows your usage.** Your 5-hour and weekly limits, with the same numbers you see on claude.ai. It reads them from the rate-limit events Claude Code itself emits while it works.
- **It respects your cap.** You can set a weekly cap. When you reach it, IronDeck asks before going on.
- **No task runs forever.** Each one has a 6-hour limit.

## The library and versions

- **Import your `.skill` packages** without losing earlier versions.
- **Version numbers never go down.** Restoring an old version creates a new one, with a note saying which one it restored.
- **A/B evaluations** run each case three times with each version, because a model's answer varies between runs, and Opus judges the results.
- **Before packaging**, IronDeck checks the skill against the official validator's rules. It only exports what passes.

## What you'll need

Provisional list; the final one ships with the first release.

- Windows, native (no WSL).
- Claude Code installed, signed in with your Claude account.
- A Claude plan that includes Claude Code: Pro or Max, or a Team or Enterprise plan. Extra usage is optional.
- Git and Node.js.

## What IronDeck doesn't do

- It doesn't store your password or send your session to any server.
- It doesn't merge anything into your project without your approval. What tasks publish depends on the permissions you give them.
- It doesn't run in the cloud: everything happens on your PC.

---

More questions? They're on the [website](https://dwladimirl.github.io/irondeck/#preguntas).

IronDeck is an independent project and is not affiliated with Anthropic. Claude and Claude Code are trademarks of Anthropic, PBC.
