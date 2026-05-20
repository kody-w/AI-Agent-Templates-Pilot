# AI Agent Templates — Pilot Library

A focused subset of [`kody-w/AI-Agent-Templates`](https://github.com/kody-w/AI-Agent-Templates),
shipped as a separate repository so it can be used as an independent test
target for a small group of rapp agent stacks.

This library follows the exact same layout, metadata schema, agent contract,
and manifest pipeline as the parent — see [`STACK_LIBRARY_SPEC.md`](STACK_LIBRARY_SPEC.md).

## Stacks in this pilot

| Industry | Stack | Agents | Synopsis |
|---|---|---|---|
| Energy & Utilities | `field_crew_safety_and_work_permit_management_stack` | 8 | Digitises the permit-to-work process: request capture → RAMS → isolation validation → digital sign-off → live DMS confirmation → crew acceptance → clearance → KPIs. |
| Energy & Utilities | `predictive_asset_maintenance_intelligence_stack` | 8 | Aggregator → health scorer → failure-probability ranker → work-order drafter → parts planner → field-execution capture → register write-back → lifecycle capex planner. |
| Energy & Utilities | `procurement_and_supplier_collaboration_portal_stack` | 8 | Demand-signal → procurement strategy → RFQ builder → bid intake → bid evaluation → PO approval/issuance → delivery tracking → three-way match. |
| Financial Services | `payments_operations_excellence_stack` | 8 | Scheme-rule validation → sanctions screening → exception repair → nostro reconciliation → correspondent monitoring → pre-release fraud scoring → status tracker → KPIs. |

Each stack ships with:

- `metadata.json` — schema described in `STACK_LIBRARY_SPEC.md`
- `agents/*.py` — focused BasicAgent sub-agents, no orchestrator
- `tests/test_agents.py` — pytest suite (BasicAgent shim auto-installed)
- `README.md` — overview + data flow

## Browse the catalogue

`index.html` is a static-site catalogue identical to the parent repo.
GitHub Pages will serve it if enabled. The catalogue fetches `manifest.json`
at runtime — regenerate after any change:

```bash
python3 update_manifest.py
git add manifest.json agents/index.json
git commit -m "Refresh manifest"
```

## Run a stack locally

```bash
cd agent_stacks/energy_stacks/predictive_asset_maintenance_intelligence_stack
python3 agents/asset_sensor_aggregator_agent.py        # self-test, prints JSON
python3.11 -m pytest -xvs tests/test_agents.py         # full suite
```

## Drop a stack into rapp_ai

```bash
cp agent_stacks/.../agents/*.py /path/to/rapp_ai/agents/
cd /path/to/rapp_ai && func start
```

The agents register automatically — they `from agents.basic_agent import BasicAgent`.

## Why a separate pilot repo?

So a small set of stacks can be validated, demoed, and iterated on without
churning the parent catalogue. Add stacks here when you want them in the
pilot; promote them to the parent repo when they're production-ready.
