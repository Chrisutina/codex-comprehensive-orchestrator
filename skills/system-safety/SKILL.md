---
name: system-safety
description: Triage suspicious files, system behavior, malware indicators, and security hygiene using safe, authorized, non-executing inspection. Use for requests to scan a computer for viruses or trojans, investigate alerts, inspect persistence/network indicators, or prepare a defensive incident report.
---

# Perform defensive system triage

Treat this as defensive assistance, not a promise of antivirus-grade detection. Confirm the authorized machine and scope. Do not scan private or third-party systems without permission.

## Safe workflow

1. Preserve context: time, symptoms, recent downloads/installations, user account, and suspected paths. Avoid deleting or "cleaning" evidence.
2. Start read-only: inventory files/processes/services/startup entries/scheduled tasks/network connections/logs using trusted OS tools. Record hashes, timestamps, signer information, and exact commands.
3. Use an installed trusted scanner such as Microsoft Defender or the organization's approved endpoint tool when available. Let the scanner produce the authoritative detection result; do not substitute regex heuristics for a scan.
4. Correlate indicators: unusual paths, unsigned binaries, unexpected persistence, suspicious parent/child processes, anomalous outbound connections, mismatched hashes, and recently changed files. Label each as confirmed, suspicious, or benign explanation.
5. Recommend containment, backup, password rotation, isolation, quarantine, or professional incident response in priority order. Get explicit confirmation before killing processes, deleting files, quarantining, disabling services, or changing network/account settings.
6. If the user authorizes remediation, preserve a log and verify the post-action state. If the scanner cannot run, say so plainly and do not claim the machine is clean.

## Report format

- Scope and authorization
- Symptoms and timeline
- Scanner/tool and exact result
- Confirmed detections
- Suspicious indicators with paths, hashes, and confidence
- Benign explanations considered
- P0/P1/P2 containment and remediation
- Evidence preserved and limitations

Never execute a suspicious file for behavioral testing. Do not provide evasion, persistence, credential theft, or destructive malware instructions.
