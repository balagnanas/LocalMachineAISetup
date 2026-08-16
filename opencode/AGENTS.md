# Global OpenCode Instructions

After changing user-authored OpenCode or Codex configuration, run
`/Users/balasekar/LocalMachineAISetup/scripts/sync-local-ai-setup.sh`, inspect the complete diff, and
commit only portable configuration directly to `main` in `balagnanas/LocalMachineAISetup`. Push with
the configured SSH remote. The user has granted standing authorization for this configuration-only
workflow.

Exclude credentials, authentication state, memories, logs, caches, browser state, machine-generated
files, and sensitive customer data. Preserve unrelated working-tree changes and untracked files.
Stop and report when validation or secret checks fail, local `main` is not synchronized with remote
`main`, branch protection rejects the push, or the requested scope is broader than portable AI
configuration.
