#!/usr/bin/env python3
"""Content OS command line.

    python cli.py doctor                       validate config and environment
    python cli.py seed                         load sample topics and experiments
HUMAN-LED PRODUCTION (the default workflow)

    python cli.py create-brief "Topic"         write a YAML brief template
    python cli.py import-brief briefs/x.yaml   load briefs into the backlog
    python cli.py approve-brief <brief-id>     approve for production
    python cli.py backlog                      show the backlog
    python cli.py produce <brief-id>           produce one approved brief
    python cli.py produce-approved             produce the whole approved backlog

DISCOVERY MODE (optional; suggests topics, never produces)

    python cli.py discover seeds/sources.json  find candidate topics from sources
    python cli.py mine                         generate topics from the brand
    python cli.py score                        score unscored topics
    python cli.py topics                       list topics with scores
    python cli.py plan --days 7 --posts 7      build a weekly portfolio
    python cli.py show-plan                    print the latest plan
    python cli.py create-reel <topic-id>       generate and QA a Reel
    python cli.py create-carousel <topic-id>   generate and QA a carousel
    python cli.py generate-plan                generate every item in the plan
    python cli.py show <content-id>            print a generated package
    python cli.py ingest-performance <csv>     load metrics snapshots
    python cli.py analyze                      run the performance analyst
    python cli.py leaderboard                  historical performance breakdown
    python cli.py ad-candidates                deterministic ad eligibility
    python cli.py approve <content-id>         record human approval
    python cli.py usage                        token and cost ledger
    python cli.py weekly                       score, plan, and report
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from content_os.config import (  # noqa: E402
    config_warnings,
    load_brand,
    load_experiments_config,
    load_models_config,
    load_scoring_config,
    validate_all,
)
from content_os.ids import new_id  # noqa: E402
from content_os.models.content import ContentStatus  # noqa: E402
from content_os.models.experiments import Experiment  # noqa: E402
from content_os.models.topics import TopicStatus  # noqa: E402
from content_os.storage.db import from_iso, get_db, loads, utcnow  # noqa: E402
from content_os.storage.repositories import Repositories  # noqa: E402
from content_os.tools import analytics as analytics_tools  # noqa: E402
from content_os.tools.ad_eligibility import rank_ad_candidates  # noqa: E402
from content_os.models.brief import BriefStatus  # noqa: E402
from content_os.tools.brief_loader import (  # noqa: E402
    BriefError,
    load_brief_file,
    scaffold,
)
from content_os.tools.source_ingestion import list_sources, load_sources  # noqa: E402
from content_os.tracking.run_logger import summarise_usage  # noqa: E402
from content_os.workflows.analyze import run_analysis  # noqa: E402
from content_os.workflows.create import run_generation  # noqa: E402
from content_os.workflows.discover import run_discovery  # noqa: E402
from content_os.workflows.ingest import ingest_csv  # noqa: E402
from content_os.workflows.mine import run_mining  # noqa: E402
from content_os.workflows.produce import (  # noqa: E402
    produce_approved,
    produce_brief,
)
from content_os.workflows.plan import run_planning  # noqa: E402
from content_os.workflows.score import run_scoring  # noqa: E402
from content_os.workflows.weekly import run_weekly  # noqa: E402

# ---------------------------------------------------------------- output


BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"
GREEN, RED, YELLOW, CYAN = "\033[32m", "\033[31m", "\033[33m", "\033[36m"


def _plain() -> bool:
    return not sys.stdout.isatty() or os.environ.get("NO_COLOR")


def c(text: str, colour: str) -> str:
    return text if _plain() else f"{colour}{text}{RESET}"


def header(text: str) -> None:
    print()
    print(c(text, BOLD))
    print(c("-" * len(text), DIM))


def kv(key: str, value: Any, width: int = 22) -> None:
    print(f"  {key.ljust(width)} {value}")


def wrap(text: str, indent: int = 4, width: int = 92) -> str:
    import textwrap

    return textwrap.fill(
        text or "", width=width,
        initial_indent=" " * indent, subsequent_indent=" " * indent,
    )


def repos_for(args: argparse.Namespace) -> Repositories:
    return Repositories(get_db(getattr(args, "db", None)))


def require_api_key() -> bool:
    if os.environ.get("OPENAI_API_KEY"):
        return True
    print(c("\n  OPENAI_API_KEY is not set.", RED))
    print("  Copy .env.example to .env and add your key, then re-run.\n")
    return False


# ---------------------------------------------------------------- commands


def cmd_doctor(args: argparse.Namespace) -> int:
    header("Configuration")
    problems = validate_all()
    if problems:
        for p in problems:
            print(c(f"  FAIL  {p}", RED))
    else:
        cfg = load_scoring_config()
        models = load_models_config()
        brand = load_brand()
        print(c("  OK    all config files valid", GREEN))
        kv("scoring version", cfg.version)
        kv("opportunity weights", "sum to 1.0")
        kv("performance weights", "sum to 1.0")
        kv("portfolio targets", "sum to 1.0")
        kv("brand-fit veto", f"< {cfg.brand_fit_veto.threshold}")
        kv("pillars", ", ".join(brand.pillar_keys))
        kv("agents", ", ".join(models.agents))

    for warning in config_warnings():
        print(c(f"  WARN  {warning}", YELLOW))

    header("Environment")
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        print(c(f"  OK    OPENAI_API_KEY set ({len(key)} chars)", GREEN))
    else:
        print(c("  FAIL  OPENAI_API_KEY not set. Copy .env.example to .env.", RED))

    header("Database")
    repos = repos_for(args)
    counts = {
        t: repos.conn.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"]
        for t in (
            "topics", "opportunity_scores", "content_items", "creative_variants",
            "qa_results", "post_performance", "experiments", "agent_runs",
        )
    }
    for table, n in counts.items():
        kv(table, n)

    header("Sources")
    for src in list_sources():
        mark = c("ready", GREEN) if src["implemented"] else c("stub ", YELLOW)
        print(f"  {mark}  {src['name'].ljust(16)} {src['note']}")

    header("Models")
    models = load_models_config()
    for name in models.agents:
        cfg_a = models.resolved(name)
        kv(name, f"{cfg_a.model}  prompt={cfg_a.prompt_version} "
                 f"effort={cfg_a.reasoning_effort}")

    print()
    return 1 if problems or not key else 0


def cmd_seed(args: argparse.Namespace) -> int:
    repos = repos_for(args)

    header("Seeding experiments")
    for spec in load_experiments_config():
        exp = Experiment(
            id=new_id("experiment"),
            name=spec["name"],
            hypothesis=spec["hypothesis"],
            variable=spec["variable"],
            control=str(spec["control"]),
            variant=str(spec["variant"]),
            primary_metric=spec["primary_metric"],
            secondary_metrics=spec.get("secondary_metrics", []),
            created_at=utcnow(),
        )
        _, created = repos.experiments.upsert(exp)
        print(f"  {'added  ' if created else 'exists '} {exp.name}")

    header("Brand memory snapshot")
    snap = repos.brand_snapshots.snapshot(load_brand(), source="config/brand.yaml")
    print(f"  {snap}")

    seed_file = Path("seeds/sources.json")
    if seed_file.exists():
        print()
        print(c(f"  Sample sources ready: {seed_file}", CYAN))
        print(f"  Next: python cli.py discover {seed_file}")
    print()
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    header("Source connectors")
    for src in list_sources():
        mark = c("ready", GREEN) if src["implemented"] else c("stub ", YELLOW)
        print(f"  {mark}  {src['name'].ljust(16)} {src['note']}")
    print()
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    sources = load_sources(args.file)
    if not sources:
        print(c(f"\n  No sources found in {args.file}\n", RED))
        return 1

    header(f"Trend discovery from {len(sources)} sources")
    result = asyncio.run(run_discovery(repos, sources, max_topics=args.max))

    print(c(f"  proposed {result['proposed']}  "
            f"new {len(result['created'])}  "
            f"duplicate {len(result['duplicates'])}", GREEN))
    for topic_id in result["created"]:
        topic = repos.topics.get(topic_id)
        if topic:
            print()
            print(f"  {c(topic.id, CYAN)}  {c(topic.title, BOLD)}")
            print(wrap(topic.why_it_matters or topic.summary))
            print(wrap(f"angle: {topic.discussion_angle}", indent=4))
            print(f"    {c(f'saturation {topic.estimated_saturation:.2f}', DIM)}  "
                  f"{c('pillars: ' + ', '.join(topic.content_pillars), DIM)}")

    if result.get("normalization_error"):
        print(c(f"\n  normalization skipped: {result['normalization_error']}", YELLOW))
        print(c("  Exact-match deduplication still ran.", DIM))

    if result.get("merged"):
        header("Merged as duplicates")
        for m in result["merged"]:
            print(f"  {m['title'][:60]}")
            print(c(f"    -> {m['duplicate_of']}: {m['note'][:100]}", DIM))

    if result["discarded_reasons"]:
        header("Discarded")
        for reason in result["discarded_reasons"]:
            print(wrap(f"- {reason}", indent=2))

    print()
    kv("tokens", result["tokens"])
    kv("cost", f"${result['cost']:.4f}")
    if result.get("trace_id"):
        kv("trace", result["trace_id"])
    print()
    return 0


def cmd_mine(args: argparse.Namespace) -> int:
    """Generate topics from the brand rather than from the news."""
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header("Brand mining")
    print(c("  Series episodes, identity content, and experiment formats.", DIM))
    result = asyncio.run(run_mining(repos, max_topics=args.max))

    print()
    print(c(f"  proposed {result['proposed']}  new {len(result['created'])}  "
            f"duplicate {len(result['duplicates'])}", GREEN))

    by_origin: dict[str, list] = {}
    for topic in result["topics"]:
        by_origin.setdefault(topic.origin, []).append(topic)

    for origin, topics in sorted(by_origin.items()):
        header(origin.replace("_", " ").title())
        for topic in topics:
            print()
            print(f"  {c(topic.title, BOLD)}")
            if topic.series_name:
                print(f"    {c('series: ' + topic.series_name, CYAN)}")
            print(wrap(topic.why_only_this_brand, indent=4))
            if topic.requires_work:
                print(c(f"    needs: {'; '.join(topic.requires_work[:3])}", YELLOW))
            print(c(f"    saturation {topic.estimated_saturation:.2f}", DIM))

    header("Rationale")
    print(wrap(result["rationale"], indent=2))
    print()
    kv("tokens", result["tokens"])
    kv("cost", f"${result['cost']:.4f}")
    if result.get("trace_id"):
        kv("trace", result["trace_id"])
    print()
    return 0


def cmd_create_brief(args: argparse.Namespace) -> int:
    """Write a YAML template for a human to fill in."""
    template = scaffold(args.topic, args.format)
    target = Path(args.out) if args.out else Path("briefs") / (
        "".join(ch if ch.isalnum() else "_" for ch in args.topic.lower())[:48] + ".yaml"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not args.force:
        print(c(f"\n  {target} already exists. Use --force to overwrite.\n", RED))
        return 1
    target.write_text(template, encoding="utf-8")

    header("Brief template created")
    kv("file", str(target))
    print()
    print("  Fill it in, then:")
    print(c(f"    python cli.py import-brief {target}", CYAN))
    print(c("    python cli.py approve-brief <brief-id>", CYAN))
    print(c("    python cli.py produce-approved", CYAN))
    print()
    return 0


def cmd_import_brief(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    try:
        briefs = load_brief_file(args.file)
    except BriefError as exc:
        print(c(f"\n  {exc}\n", RED))
        return 1

    header(f"Imported {len(briefs)} brief(s)")
    for brief in briefs:
        if args.approve:
            brief.status = BriefStatus.APPROVED
            brief.approved_by = args.by
            brief.approved_at = utcnow()
        repos.briefs.upsert(brief)

        status_colour = GREEN if brief.status == BriefStatus.APPROVED else YELLOW
        print()
        print(f"  {c(brief.brief_id, CYAN)}  {c(brief.status.value, status_colour)}")
        print(f"  {c(brief.topic, BOLD)}")
        print(f"    {brief.content_format} | {brief.brand_pillar} | "
              f"priority {brief.priority} | {brief.urgency}")
        print(wrap(f"thesis: {brief.core_thesis}", indent=4))
        print(wrap(f"learning: {brief.learning_objective}", indent=4))
        print(f"    {c(f'{len(brief.high_level_sections)} mandatory sections, '
                       f'{len(brief.approved_hook_points)} hook points', DIM)}")

    if not args.approve:
        print()
        print(c("  Briefs import as DRAFT. Only APPROVED briefs are produced.", DIM))
        print(c(f"  Approve with: python cli.py approve-brief <brief-id>", CYAN))
    print()
    return 0


def cmd_approve_brief(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    if args.all:
        pending = [
            b for b in (repos.briefs.get(r["brief_id"])
                        for r in repos.briefs.backlog())
            if b and b.status in (BriefStatus.DRAFT, BriefStatus.HUMAN_REVIEW)
        ]
        if not pending:
            print(c("\n  No briefs awaiting approval.\n", YELLOW))
            return 0
        header(f"Approving {len(pending)} briefs")
        for brief in pending:
            repos.briefs.approve(brief.brief_id, args.by, args.note or "")
            repos.approvals.record(
                subject_type="brief", subject_id=brief.brief_id, action="produce",
                decision="APPROVED", approved_by=args.by, notes=args.note or "",
            )
            print(f"  {c('approved', GREEN)}  {brief.topic[:64]}")
        print()
        return 0

    brief = repos.briefs.get(args.brief_id)
    if brief is None:
        print(c(f"\n  Brief not found: {args.brief_id}\n", RED))
        return 1
    repos.briefs.approve(brief.brief_id, args.by, args.note or "")
    repos.approvals.record(
        subject_type="brief", subject_id=brief.brief_id, action="produce",
        decision="APPROVED", approved_by=args.by, notes=args.note or "",
    )
    print(c(f"\n  Approved by {args.by}: {brief.topic}", GREEN))
    print(c(f"  Produce with: python cli.py produce-approved\n", CYAN))
    return 0


def cmd_backlog(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    header("Content backlog")
    counts = repos.briefs.counts_by_status()
    if not counts:
        print(c("  Empty. Create one with: python cli.py create-brief \"Topic\"\n",
                YELLOW))
        return 0

    for status, n in sorted(counts.items()):
        colour = {"APPROVED": GREEN, "READY": GREEN, "REJECTED": RED,
                  "IN_PRODUCTION": CYAN}.get(status, DIM)
        print(f"  {c(status.ljust(15), colour)} {n}")

    print()
    print(f"  {'pri':>3}  {'status':<15} {'format':<10} {'pillar':<16} topic")
    print(c("  " + "-" * 96, DIM))
    for row in repos.briefs.backlog(status=args.status, limit=args.limit):
        colour = {"APPROVED": GREEN, "READY": GREEN, "REJECTED": RED,
                  "IN_PRODUCTION": CYAN}.get(row["status"], DIM)
        print(f"  {row['priority']:>3}  {c(row['status'][:15].ljust(15), colour)} "
              f"{row['content_format'][:10]:<10} {row['brand_pillar'][:16]:<16} "
              f"{row['topic'][:44]}")
        print(c(f"       {row['brief_id']}", DIM))
    print()
    return 0


def _print_produced(result: dict[str, Any]) -> None:
    package, qa = result["package"], result["qa"]
    fmt = result["format"]

    header(f"{fmt.upper()}  {package.title}")
    hook_label = "HOOK" if fmt == "reel" else "COVER"
    strategy = result["hook_strategy"]
    variant_id = result["hook_variant_id"]
    print(f"  {c(hook_label, BOLD)}  {c(result['hook'], GREEN)}")
    print("        " + c(f"strategy: {strategy} ({variant_id})", DIM))

    header("Learning payoff")
    print(wrap(package.learning_payoff, indent=2))
    print()
    kv("save reason", package.save_reason[:70])
    kv("share reason", package.share_reason[:70])

    if fmt == "reel":
        header("Script")
        print(wrap(package.script, indent=2))
        header("Scenes")
        for scene in package.scene_plan:
            print(f"  {c(f'{scene.start_second:.0f}-{scene.end_second:.0f}s', CYAN)}  "
                  f"{c(scene.production_mode, DIM)}")
            print(wrap(scene.voiceover, indent=6))
    else:
        header(f"Slides ({len(package.slides)})")
        for slide in package.slides:
            print()
            print(f"  {c(f'{slide.index}. {slide.headline}', BOLD)}  "
                  f"{c(slide.role, DIM)}")
            print(wrap(slide.body, indent=5))

    header("Brief compliance")
    covered = len(qa.sections_covered)
    total = covered + len(qa.sections_missing)
    mark = GREEN if not qa.sections_missing else RED
    print(f"  sections covered   {c(f'{covered}/{total}', mark)}")
    if qa.sections_missing:
        for section in qa.sections_missing:
            print(c(f"    missing: {section}", RED))
    drift = c("YES", RED) if qa.thesis_drift else c("no", GREEN)
    print(f"  thesis drift       {drift}")
    if qa.thesis_drift_explanation:
        print(wrap(qa.thesis_drift_explanation, indent=4))

    header("QA")
    verdict = c("APPROVED", GREEN) if qa.approved else c("REJECTED", RED)
    print(f"  {verdict}   composite {qa.composite:.2f}")
    for key in ("learning_value", "execution_against_brief", "hook_strength",
                "technical_accuracy", "originality"):
        if key in qa.scores:
            print(f"    {key.replace('_', ' '):<26} {qa.scores[key]:.1f}")
    if qa.failed_gates:
        print(c(f"  failed gates: {', '.join(qa.failed_gates)}", RED))
    if qa.issues:
        print()
        for issue in qa.issues[:6]:
            print(wrap(f"- {issue}", indent=4))

    if result.get("warnings"):
        header("Warnings")
        for warning in result["warnings"]:
            print(c(f"  {warning}", YELLOW))

    plan = result.get("plan")
    if plan and plan.alternate_format_recommendation:
        header("Alternate format suggested (not applied)")
        print(f"  {c(plan.alternate_format_recommendation, YELLOW)}")
        print(wrap(plan.alternate_format_reason or "", indent=4))
        print(c("  Format is human-owned. Change the brief if you agree.", DIM))


def cmd_produce(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    brief = repos.briefs.get(args.brief_id)
    if brief is None:
        print(c(f"\n  Brief not found: {args.brief_id}\n", RED))
        return 1

    header(f"Producing {brief.content_format}: {brief.topic}")
    result = asyncio.run(produce_brief(repos, brief))
    if result.get("error"):
        print(c(f"  {result['error']}\n", RED))
        return 1

    _print_produced(result)
    print()
    kv("content_id", result["content_id"])
    kv("status", result["status"])
    kv("cost", f"${result['cost']:.4f}")
    if result.get("trace_id"):
        kv("trace", result["trace_id"])
    print()
    return 0


def cmd_produce_approved(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header("Producing approved briefs")
    result = asyncio.run(produce_approved(repos, limit=args.limit))
    if result.get("message"):
        print(f"  {result['message']}\n")
        return 0

    approved = rejected = 0
    for item in result["produced"]:
        qa = item["qa"]
        if qa.approved:
            approved += 1
            mark = c("ready   ", GREEN)
        else:
            rejected += 1
            mark = c("QA fail ", RED)
        print(f"  {mark} {item['title'][:58]}")
        print(c(f"           {item['format']}  composite {qa.composite:.2f}  "
                f"${item['cost']:.4f}  {item['content_id']}", DIM))
        if qa.failed_gates:
            print(c(f"           {', '.join(qa.failed_gates[:3])}", RED))

    for failure in result["failed"]:
        print(c(f"  error    {failure['brief_id']}: {failure['error'][:90]}", RED))

    usage = summarise_usage(repos, result["run_id"])
    print()
    kv("ready for review", approved)
    kv("qa rejected", rejected)
    kv("errored", len(result["failed"]))
    kv("tokens", usage["total_tokens"])
    kv("cost", f"${usage['total_cost']:.4f}")
    print()
    print(c("  Nothing is published. Review, then: python cli.py approve <content-id>",
            DIM))
    print()
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header("Opportunity scoring")
    result = asyncio.run(
        run_scoring(repos, rescore_all=args.all, limit=args.limit,
                    concurrency=args.concurrency)
    )
    if result.get("message"):
        print(f"  {result['message']}\n")
        return 0

    print(f"  {'score':>6}  {'base':>5}  {'brand':>5}  {'pen':>5}  title")
    print(c("  " + "-" * 88, DIM))
    for row in result["scored"]:
        flag = c(" VETO", RED) if row["vetoed"] else ""
        print(f"  {row['adjusted_score']:>6.2f}  {row['base_score']:>5.2f}  "
              f"{row['brand_fit']:>5.1f}  {row['saturation_penalty']:>5.2f}  "
              f"{row['title'][:56]}{flag}")

    if result["vetoed"]:
        header("Vetoed (trending but off-brand)")
        for row in result["vetoed"]:
            print(f"  {row['title'][:70]}")
            print(c(f"    brand_fit {row['brand_fit']:.1f} -> {row['veto_flag']}", DIM))

    if result["failed"]:
        header("Failed")
        for row in result["failed"]:
            print(c(f"  {row['title'][:60]}: {row['error']}", RED))

    print()
    kv("tokens", result["total_tokens"])
    kv("cost", f"${result['total_cost']:.4f}")
    print()
    return 0


def cmd_topics(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    header("Topics")
    rows = repos.scores.ranked(include_vetoed=True, limit=args.limit)
    unscored = repos.topics.unscored(limit=args.limit)

    if rows:
        print(f"  {'score':>6}  {'status':<14} {'id':<28} title")
        print(c("  " + "-" * 104, DIM))
        for scored in rows:
            status = "VETOED" if scored.score.vetoed else scored.topic.status.value
            colour = RED if scored.score.vetoed else GREEN
            print(f"  {scored.score.adjusted_score:>6.2f}  "
                  f"{c(status.ljust(14), colour)} {scored.topic.id:<28} "
                  f"{scored.topic.title[:50]}")

    if unscored:
        header(f"Unscored ({len(unscored)})")
        for topic in unscored:
            print(f"  {topic.id:<28} {topic.title[:60]}")
        print(c("\n  Run: python cli.py score", DIM))
    print()
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header(f"Weekly content plan: {args.posts} posts over {args.days} days")
    result = asyncio.run(
        run_planning(repos, target_posts=args.posts, horizon_days=args.days)
    )
    if result.get("error"):
        print(c(f"  {result['error']}\n", RED))
        return 1
    _print_plan(result)
    return 0


def _print_plan(result: dict[str, Any]) -> None:
    for index, item in enumerate(result["items"], start=1):
        urgency = item["urgency"]
        colour = RED if urgency == "publish_24_48h" else (
            YELLOW if urgency == "publish_this_week" else DIM
        )
        print()
        print(f"  {c(str(index) + '.', BOLD)} {c(item['title'], BOLD)}")
        print(f"     {c(item['format'].upper(), CYAN)}  {item['pillar']}  "
              f"{item['strategic_role']}  {c(urgency, colour)}  "
              f"score {item['score']:.2f}  {c(item['planned_date'], DIM)}")
        print(f"     {c('hook:', DIM)} {item['hook']}")
        for alt in item["alternate_hooks"][:2]:
            print(f"     {c('alt: ', DIM)} {alt}")
        print(wrap(item["reasoning"], indent=5))
        print(f"     {c(item['content_id'], DIM)}")

    report = result["balance_report"]
    header("Portfolio balance")
    for pillar, share in sorted(report["distribution"].items()):
        deviation = report["deviations"].get(pillar, 0.0)
        mark = c("ok", GREEN) if abs(deviation) <= 0.15 else c("off", YELLOW)
        print(f"  {pillar.ljust(18)} {share:>6.0%}  ({deviation:+.0%})  {mark}")
    kv("formats", report["format_counts"])
    kv("distinct pillars", report.get("distinct_pillars", 0))
    if report["violations"]:
        print(c(f"  violations: {report['violations']}", YELLOW))
    else:
        print(c("  no guardrail violations", GREEN))

    header("Strategist rationale")
    print(wrap(result["portfolio_rationale"], indent=2))

    if result.get("deferred"):
        header("Deferred")
        for topic_id, reason in result["deferred"][:8]:
            print(wrap(f"- {topic_id}: {reason}", indent=2))

    print()
    kv("tokens", result["tokens"])
    kv("cost", f"${result['cost']:.4f}")
    if result.get("trace_id"):
        kv("trace", result["trace_id"])
    print()


def cmd_show_plan(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    plan = repos.plans.latest()
    if plan is None:
        print(c("\n  No plan yet. Run: python cli.py plan\n", YELLOW))
        return 1

    header(f"Plan {plan['id']}  ({plan['created_at'][:10]})")
    rows = repos.content.by_plan(plan["id"])
    for index, row in enumerate(rows, start=1):
        status_colour = {
            "PLANNED": DIM, "GENERATED": CYAN, "READY_FOR_REVIEW": GREEN,
            "QA_FAILED": RED, "APPROVED": GREEN, "PUBLISHED": GREEN,
        }.get(row["status"], DIM)
        print()
        print(f"  {index}. {c(row['title'], BOLD)}")
        print(f"     {c(row['format'].upper(), CYAN)}  {row['pillar']}  "
              f"{c(row['status'], status_colour)}  "
              f"{c(row['planned_publish_date'][:10] if row['planned_publish_date'] else '', DIM)}")
        print(f"     {c('hook:', DIM)} {row['hook']}")
        print(f"     {c(row['id'], DIM)}")

    balance = loads(plan["balance_report_json"], {})
    header("Balance")
    kv("distribution", balance.get("distribution"))
    kv("violations", balance.get("violations") or "none")
    print()
    return 0


def _print_package(fmt: str, package: Any, qa: Any) -> None:
    if fmt == "reel":
        header(f"REEL  {package.title}")
        print(f"  {c('HOOK', BOLD)}  {c(package.hook, GREEN)}")
        for variant in package.hook_variants:
            print(f"  {c('alt ', DIM)}  {variant}")
        kv("duration", f"{package.estimated_duration_seconds}s")
        kv("visual hook", package.visual_hook)

        header("Script")
        print(wrap(package.script, indent=2))

        header("Scenes")
        for scene in package.scene_plan:
            print(f"  {c(f'{scene.start_second:.0f}-{scene.end_second:.0f}s', CYAN)}  "
                  f"{c(scene.production_mode, DIM)}")
            print(wrap(f"visual: {scene.visual}", indent=6))
            print(wrap(f"voice:  {scene.voiceover}", indent=6))
            if scene.on_screen_text:
                print(wrap(f"text:   {scene.on_screen_text}", indent=6))

        if package.b_roll_requirements:
            header("B-roll required")
            for item in package.b_roll_requirements:
                print(f"  - {item}")
        if package.avatar_requirements:
            header("Avatar requirements")
            for item in package.avatar_requirements:
                print(f"  - {item}")
    else:
        header(f"CAROUSEL  {package.title}")
        print(f"  {c('COVER', BOLD)}  {c(package.cover_hook, GREEN)}")
        header(f"Slides ({len(package.slides)})")
        for slide in package.slides:
            print()
            print(f"  {c(f'{slide.index}. {slide.headline}', BOLD)}  "
                  f"{c(slide.role, DIM)}")
            print(wrap(slide.body, indent=5))
            print(wrap(f"visual: {slide.visual_direction}", indent=5))
        print()
        kv("save reason", package.save_reason)
        kv("share reason", package.share_reason)

    header("Caption")
    print(wrap(package.caption, indent=2))
    if package.cta:
        kv("CTA", package.cta)

    if package.factual_claims_to_verify:
        header("Claims to verify before publishing")
        for claim in package.factual_claims_to_verify:
            print(wrap(f"- {claim}", indent=2))

    header("QA")
    verdict = c("APPROVED", GREEN) if qa.approved else c("REJECTED", RED)
    print(f"  {verdict}   composite {qa.composite:.2f}")
    scores = "  ".join(f"{k.replace('_', ' ')[:12]} {v:.0f}" for k, v in qa.scores.items())
    print(wrap(scores, indent=2))
    if qa.failed_gates:
        print(c(f"  failed gates: {', '.join(qa.failed_gates)}", RED))
    if qa.issues:
        print()
        print(c("  Issues", BOLD))
        for issue in qa.issues:
            print(wrap(f"- {issue}", indent=4))
    if qa.required_changes:
        print()
        print(c("  Required changes", BOLD))
        for change in qa.required_changes:
            print(wrap(f"- {change}", indent=4))
    print()
    print(wrap(qa.verdict_rationale, indent=2))


def _generate(args: argparse.Namespace, fmt: str) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header(f"Generating {fmt}")
    result = asyncio.run(
        run_generation(repos, args.topic_id, fmt, content_id=getattr(args, "content_id", None))
    )
    if result.get("error"):
        print(c(f"  {result['error']}\n", RED))
        return 1

    _print_package(fmt, result["package"], result["qa"])
    print()
    kv("content_id", result["content_id"])
    kv("variants", len(result["variant_ids"]))
    kv("status", result["status"])
    kv("tokens", result["tokens"])
    kv("cost", f"${result['cost']:.4f}")
    if result.get("trace_id"):
        kv("trace", result["trace_id"])
    print()
    return 0


def cmd_create_reel(args: argparse.Namespace) -> int:
    return _generate(args, "reel")


def cmd_create_carousel(args: argparse.Namespace) -> int:
    return _generate(args, "carousel")


def cmd_generate_plan(args: argparse.Namespace) -> int:
    """Generate every PLANNED item in the latest plan."""
    if not require_api_key():
        return 1
    repos = repos_for(args)
    plan = repos.plans.latest()
    if plan is None:
        print(c("\n  No plan yet. Run: python cli.py plan\n", YELLOW))
        return 1

    rows = [r for r in repos.content.by_plan(plan["id"]) if r["status"] == "PLANNED"]
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print(c("\n  Nothing left to generate in the latest plan.\n", YELLOW))
        return 0

    header(f"Generating {len(rows)} items from plan {plan['id']}")
    run_id = repos.runs.create("generate_plan", {"plan_id": plan["id"], "n": len(rows)})
    approved = failed = 0

    for index, row in enumerate(rows, start=1):
        fmt = "carousel" if row["format"] == "carousel" else "reel"
        print(f"\n  [{index}/{len(rows)}] {row['title'][:64]}  ({fmt})")
        try:
            result = asyncio.run(
                run_generation(
                    repos, row["topic_id"], fmt,
                    content_id=row["id"], run_id=run_id,
                )
            )
        except Exception as exc:  # noqa: BLE001 - one failure must not stop the batch
            failed += 1
            print(c(f"      failed: {type(exc).__name__}: {str(exc)[:160]}", RED))
            continue

        qa = result["qa"]
        if qa.approved:
            approved += 1
            print(c(f"      approved  composite {qa.composite:.2f}", GREEN))
        else:
            failed += 1
            print(c(f"      QA failed  composite {qa.composite:.2f}  "
                    f"{', '.join(qa.failed_gates[:2])}", RED))
        print(c(f"      {result['content_id']}  ${result['cost']:.4f}", DIM))

    repos.runs.complete(run_id, "COMPLETED")
    usage = summarise_usage(repos, run_id)
    print()
    kv("approved", approved)
    kv("rejected or failed", failed)
    kv("tokens", usage["total_tokens"])
    kv("cost", f"${usage['total_cost']:.4f}")
    print()
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    row = repos.content.get(args.content_id) or repos.content.find_by_prefix(
        args.content_id
    )
    if row is None:
        print(c(f"\n  Content not found: {args.content_id}\n", RED))
        return 1

    body = loads(row["body_json"], {})
    header(f"{row['format'].upper()}  {row['title']}")
    kv("content_id", row["id"])
    kv("topic_id", row["topic_id"])
    kv("pillar", row["pillar"])
    kv("status", row["status"])
    kv("generated by", f"{row['generator_agent']} / {row['generator_model']} "
                       f"/ {row['generator_prompt_version']}")
    if row["qa_composite"] is not None:
        kv("QA", f"{'approved' if row['qa_approved'] else 'rejected'} "
                 f"({row['qa_composite']:.2f})")

    cost = repos.agent_runs.cost_per_content(row["id"])
    if cost and cost["estimated_cost"]:
        kv("generation cost", f"${cost['estimated_cost']:.4f} "
                              f"({cost['total_tokens']} tokens, "
                              f"{cost['invocations']} calls)")

    header("Variants")
    for variant in repos.variants.for_content(row["id"]):
        mark = c("control", GREEN) if variant.is_control else c(variant.label, DIM)
        print(f"  {mark:<20} {variant.hook[:78]}")

    header("Package")
    print(json.dumps(body, indent=2)[:6000])

    qa_history = repos.qa.history(row["id"])
    if qa_history:
        header("QA history")
        for qa in qa_history:
            verdict = c("pass", GREEN) if qa["approved"] else c("fail", RED)
            print(f"  rev {qa['revision_number']}  {verdict}  "
                  f"composite {qa['composite']:.2f}  "
                  f"{c(qa['qa_model'] + ' / ' + qa['qa_prompt_version'], DIM)}")
            for issue in loads(qa["issues_json"], [])[:5]:
                print(wrap(f"- {issue}", indent=6))
    print()
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    header("Ingesting performance snapshots")
    result = ingest_csv(repos, args.file)
    if result.get("error"):
        print(c(f"  {result['error']}\n", RED))
        return 1
    kv("inserted", result["inserted"])
    kv("skipped duplicates", result["skipped_duplicates"])
    for error in result["errors"][:20]:
        print(c(f"  {error}", YELLOW))
    print()
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header("Performance analysis")
    result = asyncio.run(run_analysis(repos))
    if result.get("message"):
        print(f"  {result['message']}\n")
        return 0

    analysis = result["analysis"]
    kv("measured posts", result["measured_posts"])

    for label, findings, colour in (
        ("Observations", analysis.observations, GREEN),
        ("Hypotheses", analysis.hypotheses, YELLOW),
        ("Recommendations", analysis.recommendations, CYAN),
    ):
        if not findings:
            continue
        header(label)
        for finding in findings:
            print(f"  {c('[' + finding.confidence + ']', colour)} "
                  f"n={finding.sample_size}")
            print(wrap(finding.statement, indent=4))
            print(wrap(f"metric: {finding.supporting_metric}", indent=6))
            for caveat in finding.caveats[:3]:
                print(wrap(f"caveat: {caveat}", indent=6))

    if analysis.proposed_experiments:
        header("Proposed experiments")
        for experiment in analysis.proposed_experiments:
            print(wrap(f"- {experiment}", indent=2))

    header("Summary")
    print(wrap(analysis.summary, indent=2))
    print()
    kv("findings stored", result["findings_stored"])
    kv("tokens", result["tokens"])
    kv("cost", f"${result['cost']:.4f}")
    print()
    return 0


def _print_group(title: str, group: dict[str, Any], metric: str) -> None:
    if not group:
        return
    header(title)
    print(f"  {'bucket':<20} {'n':>3}  {'perf':>7}  {metric.replace('_', ' '):>14}")
    print(c("  " + "-" * 52, DIM))
    for bucket, stats in sorted(
        group.items(), key=lambda kv: kv[1]["performance_score"]["median"], reverse=True
    ):
        print(f"  {bucket[:20]:<20} {stats['count']:>3}  "
              f"{stats['performance_score']['median']:>7.1f}  "
              f"{stats[metric]['median']:>14.4f}")


def cmd_leaderboard(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    board = analytics_tools.leaderboard(repos, n=args.limit)
    if not board["measured_posts"]:
        print(c("\n  No performance data yet. Run: python cli.py ingest-performance <csv>\n",
                YELLOW))
        return 0

    header(f"Leaderboard ({board['measured_posts']} measured posts)")
    print(f"  {'perf':>6}  {'pct':>5}  {'fmt':<9} {'pillar':<16} title")
    print(c("  " + "-" * 92, DIM))
    for row in board["top"]:
        print(f"  {row['performance_score']:>6.1f}  "
              f"{row['performance_percentile']:>5.0f}  "
              f"{row['format'][:9]:<9} {row['pillar'][:16]:<16} {row['title'][:38]}")

    _print_group("By pillar", board["by_pillar"], "save_rate")
    _print_group("By format", board["by_format"], "share_rate")
    _print_group("By hook type", board["by_hook_type"], "share_rate")
    _print_group("By delivery mode", board["by_delivery"], "follow_per_reach")
    _print_group("By duration", board["by_duration"], "watch_ratio")

    correlation = analytics_tools.scoring_dimension_correlation(repos)
    header("Scoring dimension vs performance")
    if not correlation.get("sufficient_data"):
        print(c(f"  {correlation.get('note')}", DIM))
    else:
        for dimension, stats in correlation["correlations"].items():
            r = stats["pearson_r"]
            print(f"  {dimension.ljust(20)} "
                  f"{'n/a' if r is None else f'{r:+.3f}'}  (n={stats['n']})")
    print()
    return 0


def cmd_ad_candidates(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    header("Ad eligibility (deterministic, human approval always required)")
    candidates = rank_ad_candidates(repos, limit=args.limit)
    if not candidates:
        print(c("  No content currently passes the eligibility gates.", YELLOW))
        print(c("  This is the expected result until enough posts have been measured.\n",
                DIM))
        return 0
    for candidate in candidates:
        row = repos.content.get(candidate.content_id)
        print()
        print(f"  {c(row['title'][:70] if row else candidate.content_id, BOLD)}")
        kv("organic percentile", f"{candidate.organic_performance_percentile:.0f}")
        kv("profile visit pct", f"{candidate.profile_visit_percentile:.0f}")
        kv("follow conversion", f"{candidate.follow_conversion_percentile:.0f}")
        kv("suggested budget", f"${candidate.suggested_test_budget:.2f}/day")
        kv("approval", c("REQUIRED", YELLOW))
    print()
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    row = repos.content.get(args.content_id) or repos.content.find_by_prefix(
        args.content_id
    )
    if row is None:
        print(c(f"\n  Content not found: {args.content_id}\n", RED))
        return 1
    if row["status"] not in ("READY_FOR_REVIEW", "QA_FAILED", "GENERATED"):
        print(c(f"\n  Content is {row['status']}, nothing to approve.\n", YELLOW))
        return 1

    repos.approvals.record(
        subject_type="content", subject_id=row["id"], action="publish",
        decision="APPROVED", approved_by=args.by, notes=args.note or "",
    )
    repos.content.set_status(row["id"], ContentStatus.APPROVED)
    print(c(f"\n  Approved for publishing by {args.by}: {row['title']}", GREEN))
    print(c("  Publishing itself is not automated in v1.\n", DIM))
    return 0


def cmd_usage(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    usage = summarise_usage(repos, args.run_id)
    header("Token and cost ledger" + (f" for {args.run_id}" if args.run_id else ""))
    if not usage["by_agent"]:
        print(c("  No agent runs recorded yet.\n", YELLOW))
        return 0

    print(f"  {'agent':<20} {'model':<15} {'eff':<7} {'calls':>5} "
          f"{'in':>8} {'cached':>8} {'write':>7} {'out':>8} {'reason':>7} "
          f"{'cost':>9} {'fail':>5}")
    print(c("  " + "-" * 116, DIM))

    totals = {k: 0 for k in ("input", "cached", "write", "output", "reasoning")}
    for row in usage["by_agent"]:
        totals["input"] += row["input_tokens"] or 0
        totals["cached"] += row["cached_input_tokens"] or 0
        totals["write"] += row["cache_write_tokens"] or 0
        totals["output"] += row["output_tokens"] or 0
        totals["reasoning"] += row["reasoning_tokens"] or 0
        print(f"  {row['agent_name'][:20]:<20} {row['model'][:15]:<15} "
              f"{(row['reasoning_effort'] or '-')[:7]:<7} {row['invocations']:>5} "
              f"{row['input_tokens'] or 0:>8} {row['cached_input_tokens'] or 0:>8} "
              f"{row['cache_write_tokens'] or 0:>7} {row['output_tokens'] or 0:>8} "
              f"{row['reasoning_tokens'] or 0:>7} "
              f"${row['estimated_cost'] or 0:>8.4f} {row['failures']:>5}")

    print(c("  " + "-" * 116, DIM))
    print(f"  {'TOTAL':<44} {totals['input']:>8} {totals['cached']:>8} "
          f"{totals['write']:>7} {totals['output']:>8} {totals['reasoning']:>7} "
          f"${usage['total_cost']:>8.4f}")

    if totals["input"]:
        hit_rate = totals["cached"] / totals["input"]
        print()
        kv("cache hit rate", f"{hit_rate:.1%} of prompt tokens served from cache")
        kv("total tokens", usage["total_tokens"])

    # Cost split by how tokens were billed. A spike here says whether to fix
    # prompt stability, reasoning effort, or output length.
    split = repos.conn.execute(
        "SELECT SUM(uncached_input_cost) AS uncached, SUM(cached_input_cost) AS cached, "
        "SUM(cache_write_cost) AS write, SUM(output_cost) AS output FROM agent_runs"
        + (" WHERE run_id = ?" if args.run_id else ""),
        (args.run_id,) if args.run_id else (),
    ).fetchone()
    if split and (split["uncached"] or split["output"]):
        header("Cost by billing class")
        for label, value in (
            ("uncached input", split["uncached"] or 0.0),
            ("cached input", split["cached"] or 0.0),
            ("cache writes", split["write"] or 0.0),
            ("output", split["output"] or 0.0),
        ):
            share = value / usage["total_cost"] if usage["total_cost"] else 0.0
            print(f"  {label.ljust(18)} ${value:>8.4f}  {share:>6.1%}")

    if usage["total_tokens"] and usage["total_cost"] == 0.0:
        print()
        for warning in config_warnings():
            print(c(f"  WARN  {warning}", YELLOW))

    rows = repos.conn.execute(
        "SELECT c.id, c.title, c.format, SUM(a.estimated_cost) AS cost, "
        "SUM(a.total_tokens) AS tokens FROM content_items c "
        "JOIN agent_runs a ON a.content_id = c.id "
        "GROUP BY c.id ORDER BY cost DESC LIMIT 10"
    ).fetchall()
    if rows:
        header("Cost per content item")
        for row in rows:
            print(f"  ${row['cost'] or 0:>7.4f}  {row['tokens'] or 0:>7} tok  "
                  f"{row['format'][:9]:<9} {row['title'][:44]}")
    print()
    return 0


def cmd_weekly(args: argparse.Namespace) -> int:
    if not require_api_key():
        return 1
    repos = repos_for(args)
    header("Weekly cycle")
    result = asyncio.run(
        run_weekly(repos, target_posts=args.posts, horizon_days=args.days)
    )

    mining = result.get("mining")
    if mining and not mining.get("error"):
        print(f"  mined {len(mining['created'])} brand topics "
              f"(series, identity, experiments), ${mining['cost']:.4f}")
    elif mining and mining.get("error"):
        print(c(f"  brand mining skipped: {mining['error']}", YELLOW))

    scoring = result["scoring"]
    if scoring.get("scored"):
        print(f"  scored {len(scoring['scored'])} topics, "
              f"{len(scoring['vetoed'])} vetoed, ${scoring['total_cost']:.4f}")
    else:
        print(f"  {scoring.get('message', 'no new topics scored')}")

    planning = result["planning"]
    if planning.get("error"):
        print(c(f"\n  {planning['error']}\n", RED))
        return 1

    header(f"Recommended posting plan ({len(planning['items'])} posts)")
    _print_plan(planning)
    print(c("  Next: python cli.py generate-plan\n", CYAN))
    return 0


def cmd_runs(args: argparse.Namespace) -> int:
    repos = repos_for(args)
    header("Workflow runs")
    rows = repos.conn.execute(
        "SELECT r.*, COUNT(a.id) AS calls, SUM(a.estimated_cost) AS cost "
        "FROM runs r LEFT JOIN agent_runs a ON a.run_id = r.id "
        "GROUP BY r.id ORDER BY r.started_at DESC LIMIT ?",
        (args.limit,),
    ).fetchall()
    for row in rows:
        colour = {"COMPLETED": GREEN, "FAILED": RED, "RUNNING": YELLOW}.get(
            row["status"], DIM
        )
        started = from_iso(row["started_at"])
        print(f"  {c(row['status'][:9].ljust(9), colour)} "
              f"{row['workflow'][:18]:<18} "
              f"{started.strftime('%m-%d %H:%M') if started else '':<12} "
              f"{row['calls'] or 0:>3} calls  "
              f"${row['cost'] or 0:>7.4f}  {c(row['id'], DIM)}")
        if row["notes"]:
            print(wrap(f"note: {row['notes'][:200]}", indent=4))
    print()
    return 0


# ---------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Content OS: agentic content intelligence for an AI personal brand.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--db", help="Path to the SQLite database.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Validate config and environment.").set_defaults(
        func=cmd_doctor
    )
    sub.add_parser("seed", help="Seed experiments and brand snapshot.").set_defaults(
        func=cmd_seed
    )
    sub.add_parser("sources", help="List source connectors.").set_defaults(
        func=cmd_sources
    )

    p = sub.add_parser("discover", help="Find candidate topics from source material.")
    p.add_argument("file", help="JSON or JSONL file of sources.")
    p.add_argument("--max", type=int, default=20, help="Maximum topics to propose.")
    p.set_defaults(func=cmd_discover)

    # --- human-led production (the default workflow) ---------------------
    p = sub.add_parser("create-brief", help="Write a YAML brief template.")
    p.add_argument("topic")
    p.add_argument("--format", default="carousel",
                   choices=["reel", "carousel", "trial_reel"])
    p.add_argument("--out", help="Where to write the template.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create_brief)

    p = sub.add_parser("import-brief", help="Load briefs from a YAML file.")
    p.add_argument("file")
    p.add_argument("--approve", action="store_true",
                   help="Import directly as APPROVED.")
    p.add_argument("--by", default=os.environ.get("USER", "human"))
    p.set_defaults(func=cmd_import_brief)

    p = sub.add_parser("approve-brief", help="Approve a brief for production.")
    p.add_argument("brief_id", nargs="?", default="")
    p.add_argument("--all", action="store_true", help="Approve every pending brief.")
    p.add_argument("--by", default=os.environ.get("USER", "human"))
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_approve_brief)

    p = sub.add_parser("backlog", help="Show the content backlog.")
    p.add_argument("--status")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_backlog)

    p = sub.add_parser("produce", help="Produce one approved brief.")
    p.add_argument("brief_id")
    p.set_defaults(func=cmd_produce)

    p = sub.add_parser("produce-approved",
                       help="Produce every approved brief in the backlog.")
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=cmd_produce_approved)

    # --- discovery mode (optional; suggests, never produces) --------------
    p = sub.add_parser("mine", help="Generate topics from the brand itself.")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=cmd_mine)

    p = sub.add_parser("score", help="Score topics on six dimensions.")
    p.add_argument("--all", action="store_true", help="Rescore already-scored topics.")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--concurrency", type=int, default=4)
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("topics", help="List topics with scores.")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_topics)

    p = sub.add_parser("plan", help="Build a balanced content portfolio.")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--posts", type=int, default=7)
    p.set_defaults(func=cmd_plan)

    sub.add_parser("show-plan", help="Print the latest plan.").set_defaults(
        func=cmd_show_plan
    )

    p = sub.add_parser("create-reel", help="Generate and QA a Reel.")
    p.add_argument("topic_id")
    p.add_argument("--content-id", dest="content_id")
    p.set_defaults(func=cmd_create_reel)

    p = sub.add_parser("create-carousel", help="Generate and QA a carousel.")
    p.add_argument("topic_id")
    p.add_argument("--content-id", dest="content_id")
    p.set_defaults(func=cmd_create_carousel)

    p = sub.add_parser("generate-plan", help="Generate every item in the latest plan.")
    p.add_argument("--limit", type=int, default=0, help="Only the first N items.")
    p.set_defaults(func=cmd_generate_plan)

    p = sub.add_parser("show", help="Print a generated content package.")
    p.add_argument("content_id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("ingest-performance", help="Load metrics from CSV.")
    p.add_argument("file")
    p.set_defaults(func=cmd_ingest)

    sub.add_parser("analyze", help="Run the performance analyst.").set_defaults(
        func=cmd_analyze
    )

    p = sub.add_parser("leaderboard", help="Historical performance breakdown.")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_leaderboard)

    p = sub.add_parser("ad-candidates", help="Deterministic ad eligibility.")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_ad_candidates)

    p = sub.add_parser("approve", help="Record human approval to publish.")
    p.add_argument("content_id")
    p.add_argument("--by", default=os.environ.get("USER", "human"))
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("usage", help="Token and cost ledger.")
    p.add_argument("--run-id", dest="run_id")
    p.set_defaults(func=cmd_usage)

    p = sub.add_parser("runs", help="Recent workflow runs.")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_runs)

    p = sub.add_parser("weekly", help="Score, plan, and print the posting plan.")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--posts", type=int, default=7)
    p.set_defaults(func=cmd_weekly)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(c("\n  interrupted\n", YELLOW))
        return 130


if __name__ == "__main__":
    sys.exit(main())
