# STUDIO_ONLY_BOUNDARY

Write scope: **Eaubin08/obsidia-studio only**.

- Do not edit, patch, commit, push, or run mutation scripts against Jarvis,
  Brody, kernel, or any sibling checkout.
- Other repositories are read-only references; integration uses their existing
  public interfaces only.
- `patch_local_os_trad.py` and `patch_local_unknown_surface.py` are
  **RETIRED**. Do NOT use their `--apply` action again.
- `studio_local_cleanup.py` is a one-time exact-byte recovery tool. It requires
  a successful dry run and rejects any external changes beyond the original
  Studio-created patch. Once the local rollback is confirmed, retire these
  scripts entirely.
- Do not treat unit tests as an end-to-end editorial generation result.
- There is **no** license to bypass HOLD, alter kernel authority, or turn
  unresolved semantic debt into a fictitious sufficient result.
- A dependency that requires modifying a sibling repository is an integration
  defect to solve **inside Studio** (or report as unsupported), not an invitation
  to change that dependency.
