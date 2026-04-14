# Arthas Workflows

This reference keeps the main skill lean. Load it when the user asks for concrete Arthas troubleshooting steps.

## High CPU

Suggested path:

1. Use the tools that correspond to `dashboard` and `thread` to find busy threads and CPU-heavy activity.
2. If one or two business methods stand out, inspect the owning class and method definitions.
3. Use the smallest possible `trace` scope on the suspected method.
4. If arguments or return values matter, add a narrow `watch`.

Guidance:

- Prefer a single suspected class or method over wildcard matching.
- Limit observation duration and sample counts.
- Avoid broad tracing across hot frameworks unless the user explicitly accepts the overhead.

## Thread Blocking Or Deadlock

Suggested path:

1. Start with the tool corresponding to `thread`.
2. Focus on blocked, waiting, or deadlocked threads.
3. Capture the blocking owner and the relevant stack traces.
4. If needed, inspect the suspect classes with `jad` or related inspection tools.

What to report:

- blocked thread names and states
- owning lock or monitor when available
- top business frames

## Slow Request / Slow Method

Suggested path:

1. Confirm the exact entry method or service method.
2. Inspect bytecode / method signatures with `jad`, `sc`, or `sm`.
3. Use `trace` for latency breakdown on one method.
4. Use `stack` if you need the upstream caller chain.
5. Use `watch` if the slowdown depends on arguments, return values, or exceptions.

Good narrowing prompts:

- one class
- one method
- one request pattern
- a condition expression if the tool supports it

## Exceptions And Unexpected Results

Suggested path:

1. Identify the exact suspect method.
2. Use a `watch`-style tool that captures parameters, return values, and thrown exceptions.
3. Add conditions if only some invocations are problematic.
4. If code understanding is needed, inspect the compiled class with `jad`.

Safety notes:

- Start with low-frequency or conditional observation.
- Avoid dumping large object graphs unless required.

## Class / Classloader Problems

Suggested path:

1. Use inspection tools corresponding to `sc`, `sm`, `jad`, and classloader-related views.
2. Confirm which class was loaded and from where.
3. Check whether duplicate loading or unexpected classloader boundaries exist.
4. Only then move into runtime tracing if behavior still needs proof.

## Baseline Investigation Order

When the user gives only a vague symptom, this order is usually safe:

1. target discovery
2. runtime overview
3. threads / hotspots
4. class and method inspection
5. narrow watch / stack / trace
6. summarize evidence and next step

## Reporting Template

Use a concise structure:

- Symptom: what the user reported
- Probe: which Arthas MCP tool you used
- Scope: target JVM, class, method, condition, limits
- Evidence: the key factual findings
- Inference: what those findings likely mean
- Next step: the safest useful follow-up
