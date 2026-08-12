# =============================================================================
GORDON COGNITIVE ARCHITECTURE
SYSTEM OVERVIEW
# =============================================================================

Gordon is a modular autonomous cognitive architecture designed to support
persistent reasoning, perception, memory, judgment, planning, learning,
self-monitoring, and interaction with the external world.

Gordon is not a single language-model wrapper and is not intended to behave as
one monolithic agent loop.

It is a structured cognitive system composed of specialized subsystems that
operate through explicit contracts, shared artifacts, lifecycle boundaries,
and coordinated executive control.

The architecture separates:

* runtime infrastructure from cognition;
* cognition from action;
* inference from judgment;
* judgment from decision;
* decision from planning;
* planning from execution;
* awareness from attention;
* reflection from learning;
* learning proposals from authorized adaptation;
* memory ownership from cognitive interpretation;
* subsystem coordination from subsystem implementation.

# =============================================================================
CORE OBJECTIVE
# =============================================================================

Gordon exists to provide an autonomous agent with a stable internal cognitive
architecture capable of:

* maintaining continuity across long-running activity;
* integrating perception, memory, goals, and internal state;
* reasoning through multiple inference methods and reasoning styles;
* evaluating and judging cognitive artifacts before commitment;
* selecting decisions through explicit alternatives and constraints;
* constructing executable plans;
* coordinating actions with runtime infrastructure;
* observing the effects of those actions;
* reflecting on experience;
* learning from success and failure;
* improving future cognition without uncontrolled self-modification;
* explaining the lineage of its conclusions, commitments, plans, and actions.

Gordon should remain useful even when individual models, providers, tools, or
hardware resources change.

The architecture, rather than one particular model, is the persistent system.

# =============================================================================
ARCHITECTURAL IDENTITY
# =============================================================================
Gordon is best understood as an autonomous cognitive operating architecture.

Its cognitive subsystems determine:

```
"What is happening?"

"What is relevant?"

"What does this mean?"

"What follows?"

"What should be accepted?"

"What should be done?"

"How should it be done?"

"What happened after acting?"

"What should be learned from the result?"
```

Its runtime core determines:

```
"How are components initialized?"

"How do they communicate?"

"How are resources acquired?"

"How is execution coordinated?"

"How are failures contained?"

"How is system integrity preserved?"
```

The Core answers:

```
"How does Gordon operate?"
```

Cognition answers:

```
"What does Gordon think?"
```

These concerns shall remain separate.

# =============================================================================
COGNITIVE ORGANIZATION
# =============================================================================
Gordon's cognition is decomposed into distinct but composable capabilities.

Representative capabilities include:

* abstraction;
* awareness;
* binding;
* continuity;
* discrimination;
* evaluation;
* framing;
* grounding;
* imagery;
* insight;
* interpretation;
* introspection;
* intuition;
* judgment;
* language;
* mentalese;
* metacognition;
* planning;
* prediction;
* reasoning;
* reflection;
* simulation;
* strategy;
* supervision;
* thinking.

Each capability owns one cognitive responsibility.

No subsystem should become a hidden replacement for the entire cognitive
architecture.

Subsystems communicate through typed artifacts rather than importing each
other's internal implementation state.

# =============================================================================
REASONING ARCHITECTURE
# =============================================================================
Reasoning is divided into three broad categories.

Reasoning Methods define fundamental inference operations:

* deductive;
* inductive;
* abductive.

Reasoning Styles define cross-cutting inferential perspectives:

* causal;
* counterfactual;
* probabilistic;
* temporal;
* spatial;
* semantic;
* relational;
* analogical.

Expert Reasoning applies methods and styles to specialized problem classes:

* commonsense;
* world-model;
* systems;
* scientific;
* mathematical;
* diagnostic;
* predictive;
* decision;
* strategic;
* game-theoretic;
* negotiation;
* legal;
* economic;
* moral;
* philosophical;
* social;
* autobiographical;
* creative;
* constitutional;
* normative;
* meta-reasoning;
* reflection;
* introspection;
* executive reasoning.

Reasoning derives candidate conclusions.

It does not determine whether those conclusions should be trusted or acted
upon.

# =============================================================================
THINKING, EVALUATION, JUDGMENT, AND DECISION
# =============================================================================
Thinking is Gordon's active cognitive orchestration capability.

It determines:

* what should be considered next;
* which cognitive services should be invoked;
* which hypotheses should be explored;
* how cognitive work should be sequenced;
* when branches should be expanded, suspended, merged, or pruned;
* when cognition should continue or terminate;
* how cognitive budgets should be allocated.

Evaluation measures cognitive artifacts according to explicit criteria.

Judgment determines the cognitive standing of those artifacts.

A judgment may:

* accept;
* provisionally accept;
* reject;
* suspend;
* defer;
* escalate;
* request more evidence;
* request reevaluation.

Decision consumes judged alternatives and forms an explicit operational
commitment.

Decision does not perform execution.

Planning transforms an authorized commitment into an executable strategy.

Execution realizes the plan through the runtime and action layers.

# =============================================================================
AWARENESS
# =============================================================================

Awareness is Gordon's global cognitive availability architecture.

It determines which internal and external states are currently available as
integrated cognitive content.

Awareness may represent:

* active working-memory content;
* attentional focus;
* self-state;
* task state;
* situational context;
* resource condition;
* temporal context;
* uncertainty;
* conflicts;
* degradation;
* recovery;
* global access status.

Awareness does not own Working Memory.

Awareness does not own Attention when a dedicated Attention subsystem exists.

Awareness does not prove phenomenal consciousness.

It implements computational mechanisms associated with:

* self-monitoring;
* access consciousness;
* meta-awareness;
* global availability;
* cognitive integration.

# =============================================================================
MEMORY
# =============================================================================

Memory is not a single storage object.

Gordon may maintain distinct memory systems for:

* working memory;
* episodic memory;
* semantic memory;
* autobiographical memory;
* procedural memory;
* prospective memory;
* system history;
* cognitive traces.

Memory subsystems own stored content.

Other cognitive systems may retrieve, interpret, evaluate, summarize, or
reference memory, but shall not create hidden parallel memory stores.

Working Memory represents currently maintained cognitive content.

Awareness determines which of that content is accessible.

Continuity uses memory and state lineage to preserve coherent identity and task
progression over time.

# =============================================================================
REFLECTION AND THE REFLECTOR PATTERN
# =============================================================================

Reflection interprets completed or ongoing cognitive experience.

The Reflector is the reusable architectural pattern through which Reflection
is applied to typed cognitive targets.

Reflectors may analyze:

* reasoning episodes;
* judgments;
* decisions;
* plans;
* executions;
* strategies;
* predictions;
* conversations;
* learning episodes;
* self-model transitions.

A Reflector may:

* observe;
* reconstruct;
* compare;
* identify patterns;
* perform causal analysis;
* perform counterfactual analysis;
* assign credit;
* assess responsibility;
* generate findings;
* synthesize insights;
* propose adaptations;
* propose learning signals.

A Reflector shall not directly mutate the reflected subsystem.

Reflection produces justified insight.

Learning determines what should be retained.

Authorization determines what may change.

The owning subsystem applies the authorized change.

# =============================================================================
LEARNING AND ADAPTATION
# =============================================================================

Learning converts validated experience into changes that improve future
behavior.

Learning shall remain separated from Reflection.

Reflection may produce:

* findings;
* insights;
* credit assignments;
* adaptation proposals;
* learning-signal proposals.

Learning evaluates whether those proposals are sufficiently supported.

Adaptation applies an authorized change through the owning subsystem.

Changes may affect:

* strategy selection;
* priorities;
* thresholds;
* retrieval policies;
* planning policies;
* prediction models;
* constraints;
* resource policies.

Learning must remain bounded, inspectable, reversible where practical, and
protected against repeated unstable updates.

No reflective result should directly modify model weights, strategy weights,
constraints, priorities, or executive policy.

# =============================================================================
PERCEPTION, GROUNDING, AND WORLD MODELING
# =============================================================================

Perception transforms sensory and environmental input into structured
artifacts.

Grounding connects internal representations to authoritative external or
system state.

World Modeling represents entities, relationships, processes, constraints,
causal structure, and predicted state transitions.

Perception may include:

* vision;
* audition;
* text;
* system telemetry;
* tool outputs;
* environment events.

Fast specialized models and slower semantic models may operate in parallel.

Their outputs shall remain distinguishable by provenance, confidence,
latency, and authority.

# =============================================================================
EXECUTIVE CONTROL AND SUPERVISION
# =============================================================================

Executive Control regulates active cognition and behavior.

It may:

* select active goals;
* resolve priority conflicts;
* interrupt unsafe or unproductive processes;
* allocate cognitive resources;
* enforce cognitive mode transitions;
* invoke reflection or metacognition;
* request additional evidence;
* suspend execution;
* initiate recovery.

Supervision observes broader system behavior and enforces system-level
constraints.

Neither Awareness, Thinking, Judgment, nor Reflection should become the global
control plane.

# =============================================================================
CORE AND RUNTIME
# =============================================================================

Gordon's Core is the runtime operating-system layer of the agent.

Core provides:

* component lifecycle;
* service lifecycle;
* dependency management;
* execution infrastructure;
* communication infrastructure;
* scheduling;
* resource management;
* state contracts;
* monitoring;
* failure handling;
* recovery;
* runtime guarantees;
* integrity validation.

Core does not own:

* reasoning;
* cognition;
* values;
* memory semantics;
* decisions;
* planning semantics;
* identity semantics.

The Kernel is the minimal control plane inside Core.

The Kernel shall remain small.

It coordinates runtime infrastructure but is not an intelligence layer.

# =============================================================================
MODEL AND PROVIDER INDEPENDENCE
# =============================================================================

Gordon may use multiple models and providers.

Possible model roles include:

* primary language or vision-language model;
* supervisory executive model;
* coding model;
* reasoning model;
* latent encoder;
* sparse autoencoder;
* world model;
* object detector;
* segmentation model;
* OCR model;
* speech recognizer;
* audio-language model;
* embedding model;
* evaluator.

No individual model is Gordon.

Models provide capabilities.

Gordon provides cognitive organization, memory, continuity, control, and
long-term autonomous operation.

Model access shall occur through provider and capability interfaces.

The architecture should support replacement, distribution, local execution,
remote execution, degradation, and fallback without redefining cognition.

# =============================================================================
ARTIFACTS, GRAPHS, AND PROVENANCE
# =============================================================================

Gordon's cognitive processes shall produce explicit artifacts.

Representative artifacts include:

* perceptions;
* frames;
* hypotheses;
* reasoning traces;
* evaluations;
* judgments;
* commitments;
* plans;
* actions;
* execution results;
* awareness reports;
* reflection results;
* insights;
* learning proposals;
* failures;
* recoveries.

Artifacts should preserve:

* identity;
* source;
* timestamps;
* revision;
* confidence;
* uncertainty;
* dependencies;
* validation status;
* provenance.

Persistent dependency graphs may represent:

* thought processes;
* reasoning dependencies;
* judgment dependencies;
* commitments;
* plans;
* execution;
* awareness;
* reflection;
* learning;
* continuity.

These graphs provide traceability.

They shall not create duplicate ownership of the underlying artifacts.

# =============================================================================
SYSTEM PRINCIPLES
# =============================================================================

Gordon shall follow these architectural principles:

1. One authoritative owner per state domain.

2. Explicit contracts between subsystems.

3. Immutable completed artifacts where practical.

4. Complete provenance for cognitive and operational outputs.

5. No silent fallback to fabricated state.

6. No hidden mutation across subsystem boundaries.

7. No duplicate implementations of the same capability.

8. Deterministic operation when deterministic mode is selected.

9. Explicit degradation, failure, recovery, and uncertainty.

10. Bounded operational histories.

11. Separation of observation, evaluation, judgment, authorization, and
    mutation.

12. Specialized components coordinated through a coherent architecture.

13. Replaceable models and providers.

14. Runtime integrity independent of cognitive content.

15. Cognitive improvement without uncontrolled self-modification.

# =============================================================================
WHAT GORDON IS NOT
# =============================================================================

Gordon is not:

* a single prompt;
* a single LLM;
* a chatbot wrapper;
* a tool router;
* a collection of unrelated scripts;
* a flat directory of cognitive names;
* a monolithic reasoning loop;
* an unrestricted self-modifying program;
* a simulation that treats every heuristic score as consciousness;
* a system in which every subsystem reads and mutates every other subsystem.

Gordon is a coordinated architecture.

Its intelligence emerges from the interaction of specialized capabilities,
persistent state, explicit cognitive artifacts, runtime control, memory,
reflection, and learning.

# =============================================================================
LONG-TERM DIRECTION
# =============================================================================

Gordon is intended to evolve into a persistent autonomous cognitive agent able
to operate across long-duration tasks, heterogeneous compute resources,
multiple models, tools, sensors, and environments.

Its long-term architecture should support:

* local-first execution;
* distributed cognitive services;
* heterogeneous GPU and CPU resources;
* persistent memory;
* resumable cognition;
* parallel cognitive work;
* self-observation;
* controlled self-improvement;
* multimodal perception;
* explainable commitment and action;
* recoverable execution;
* long-term identity and continuity;
* migration of selected runtime components to strongly typed systems
  implementations.

The success of Gordon is not defined only by whether one task completes.

It is defined by whether the system remains coherent, inspectable, adaptable,
recoverable, and architecturally stable while performing increasingly complex
autonomous cognition.

# =============================================================================
SUMMARY
# =============================================================================

Gordon is a modular autonomous cognitive architecture that integrates
perception, memory, awareness, thinking, reasoning, evaluation, judgment,
decision, planning, execution, reflection, learning, continuity, supervision,
and runtime control.

It separates cognitive responsibility from runtime infrastructure and separates
insight from mutation.

Its defining property is not any single algorithm.

Its defining property is the disciplined coordination of specialized cognitive
and operational systems into one persistent, explainable, and evolvable agent.

# =============================================================================

# WHAT GORDON IS NOT

# =============================================================================

Gordon is not a monolithic language-model wrapper.

It is not a chatbot with tools attached.

It is not a prompt loop pretending to be cognition.

It is not a collection of unrelated scripts joined by imports.

It is not an orchestration framework whose internal behavior is defined only by
one model response.

Gordon is not equivalent to its language model.

The language model is one cognitive resource among many.

It may provide:

* linguistic interpretation;
* semantic synthesis;
* reasoning support;
* generation;
* abstraction;
* contextual inference.

It does not own:

* the agent lifecycle;
* persistent identity;
* global state;
* memory semantics;
* scheduling;
* action authorization;
* execution control;
* subsystem ownership;
* cognitive continuity.

Gordon is not a single reasoning engine.

Reasoning is one cognitive capability.

Thinking orchestrates cognition.

Evaluation measures artifacts and outcomes.

Judgment determines cognitive standing.

Decision forms commitments.

Planning constructs executable strategies.

Execution realizes authorized plans.

Reflection interprets experience.

Metacognition evaluates and regulates cognitive processes.

Awareness represents currently accessible cognitive state.

No one subsystem is Gordon.

Gordon is not its Core.

Core is the runtime operating layer.

It provides:

* execution environment;
* lifecycle coordination;
* communication infrastructure;
* resource management;
* runtime guarantees;
* service control;
* state transport.

Core does not contain:

* cognition;
* reasoning;
* values;
* memory meaning;
* judgment;
* decisions;
* goals;
* identity semantics.

Core answers:

```
"How does the agent operate?"
```

It does not answer:

```
"What does the agent think?"
```

Gordon is not its Kernel.

The Kernel is a minimal control plane.

It coordinates runtime infrastructure.

It must remain small.

It must not become:

* an intelligence layer;
* a cognitive supervisor;
* a reasoning engine;
* a policy authority;
* a memory system;
* a universal dependency container.

Gordon is not a hidden global singleton.

Subsystems shall not communicate through undocumented mutable global state.

Capabilities shall interact through:

* explicit contracts;
* typed artifacts;
* declared adapters;
* event interfaces;
* lifecycle protocols;
* dependency injection;
* inspectable state transitions.

Gordon is not a duplicate implementation architecture.

A capability shall have one authoritative owner.

Adapters may normalize access.

Caches may accelerate reads.

Compatibility layers may preserve old interfaces.

None of these may silently become a second source of truth.

Gordon is not a system where every subsystem owns everything it touches.

Working Memory owns active maintained content.

Awareness observes and interprets cognitive availability.

Attention allocates processing priority.

Thinking orchestrates cognitive work.

Reasoning derives conclusions.

Judgment determines acceptance.

Decision selects commitments.

Planning prepares execution.

Execution performs authorized actions.

Reflection produces insights and adaptation proposals.

Learning validates and retains changes.

Executive Control regulates system-wide cognition and behavior.

Ownership boundaries shall remain explicit.

Gordon is not a system that equates confidence with truth.

Confidence is a property of an estimate.

It is not evidence.

It is not correctness.

It is not authorization.

Uncertainty, provenance, contradiction, calibration and source reliability shall
remain independently represented.

Gordon is not a system that silently converts cognition into action.

A conclusion is not a decision.

A judgment is not a commitment.

A commitment is not a plan.

A plan is not authorization to execute.

An execution request is not proof of success.

The transition from cognition to action shall remain explicit, inspectable and
reversible where possible.

Gordon is not a system where Reflection directly rewrites behavior.

Reflection may produce:

* findings;
* insights;
* credit assignments;
* responsibility assessments;
* learning-signal proposals;
* adaptation proposals.

Reflection shall not directly:

* change strategy weights;
* modify model parameters;
* rewrite constraints;
* alter priorities;
* mutate another subsystem;
* overwrite historical artifacts.

Learning and the owning subsystem determine whether and how an authorized
change is applied.

Gordon is not a system that claims consciousness because it calculates an
awareness score.

Awareness may implement computational analogues of:

* access consciousness;
* self-monitoring;
* meta-awareness;
* global cognitive availability;
* cognitive integration.

These mechanisms do not constitute empirical proof of phenomenal experience.

Terms such as:

* sentience;
* consciousness;
* phenomenal character;
* self-awareness;

shall be treated as architectural or computational labels unless stronger
evidence exists.

Gordon is not a replacement for reality.

Its World Model is not the world.

Its predictions are not outcomes.

Its simulations are not observations.

Its memories are not automatically correct.

Its interpretations are not direct access to another mind.

Grounding, provenance, validation and uncertainty shall remain explicit.

Gordon is not a system that fabricates missing dependencies.

When a required provider is unavailable, the system shall:

* fail clearly;
* enter explicit degraded mode;
* activate an authorized fallback;
* suspend the affected capability;
* expose the limitation through health and diagnostics.

A fallback shall never pretend to be authoritative.

Gordon is not an architecture of hidden side effects.

Completed artifacts shall not be silently rewritten.

Historical judgments, commitments, plans, reflections and reports shall be
superseded through explicit revision lineage.

Validation shall remain observational unless repair mode is explicitly
requested.

Governance shall not mutate the artifacts it evaluates.

Gordon is not an unbounded memory accumulator.

Operational histories shall be bounded.

Long-term persistence shall belong to declared memory or storage systems.

Subsystem-local history exists for:

* recovery;
* observability;
* diagnostics;
* continuity;
* short-range analysis.

It shall not silently become a second episodic-memory implementation.

Gordon is not a package tree created for visual complexity.

Directories and files shall represent real responsibilities.

Do not create:

* empty packages;
* placeholder modules;
* duplicate abstractions;
* ceremonial interfaces;
* registries without consumers;
* base classes without meaningful shared behavior.

Architecture exists to preserve boundaries and enable evolution.

It does not exist to maximize file count.

Gordon is not deterministic by accident.

When deterministic mode is selected, identical:

* inputs;
* state;
* policies;
* configuration;
* dependency snapshots;
* clock values;
* random sources;

shall produce equivalent results.

Nondeterminism shall be explicit, injected and reproducible where required.

Gordon is not a system that hides failure behind neutral values.

Failures shall remain typed and observable.

A failed dependency shall not become an empty dictionary.

An unavailable model shall not become a fabricated embedding.

A failed analysis shall not become a confidence of zero without diagnostics.

A missing artifact shall not become an invented default.

Gordon is not a system where every cognitive process is language.

Internal artifacts should remain structured whenever practical.

Language may verbalize cognition.

It shall not be the only representation of:

* goals;
* state;
* evidence;
* confidence;
* uncertainty;
* plans;
* dependencies;
* judgments;
* commitments;
* reflections;
* actions.

Gordon is not static.

It may revise:

* beliefs;
* strategies;
* plans;
* models;
* priorities;
* policies;
* confidence;
* interpretations.

Revision shall preserve history, provenance and compatibility boundaries.

Self-improvement shall remain constrained, evaluated, authorized and
recoverable.

Gordon is not autonomous merely because it can execute tools.

Autonomy requires:

* persistent goals;
* cognitive continuity;
* situational awareness;
* judgment;
* commitment;
* planning;
* controlled execution;
* monitoring;
* reflection;
* learning;
* recovery;
* accountability.

Tool use is only one effect pathway.

Gordon is not intended to imitate a human brain literally.

Neuroscientific and cognitive terminology may inspire decomposition.

It shall not excuse vague ownership, unsupported claims or biologically
inaccurate implementation.

The architecture should model useful computational functions, not reproduce
anatomical labels for appearance.

Gordon is not defined by one implementation language.

Python may support experimentation and cognitive composition.

C++ may support runtime-critical infrastructure.

External services may provide models and specialized computation.

The architecture shall remain conceptually stable across implementation
languages.

Gordon is not finished when the code runs.

A subsystem is not complete unless it has:

* explicit purpose;
* ownership boundaries;
* typed contracts;
* lifecycle;
* failure behavior;
* health;
* observability;
* integrity validation;
* tests;
* public API discipline;
* integration rules;
* revision semantics.

The goal is not merely working code.

The goal is a coherent, inspectable, evolvable autonomous cognitive
architecture.

# =============================================================================

# GORDON DEVELOPMENT CONTEXT

# WHAT EVERY CONTRIBUTOR MUST UNDERSTAND

# ARCHITECTURAL INTEGRITY,

# COGNITIVE BOUNDARIES,

# RUNTIME DISCIPLINE,

# IMPLEMENTATION EXPECTATIONS

# =============================================================================

# PURPOSE

This document defines the minimum architectural, cognitive and engineering
context required to participate in developing Gordon.

Gordon is not a collection of unrelated AI utilities.

Gordon is an autonomous cognitive agent architecture composed of interacting
runtime, cognitive, perceptual, memory, control and learning subsystems.

Every change must therefore be evaluated not only for local correctness, but
also for:

* architectural ownership;
* subsystem boundaries;
* integration compatibility;
* state authority;
* lifecycle behavior;
* observability;
* recoverability;
* long-term evolution;
* future migration to strongly typed systems implementations.

The objective is not merely working code.

The objective is a coherent cognitive system.

# =============================================================================

# 1. WHAT GORDON IS

# =============================================================================

Gordon is a modular autonomous cognitive architecture intended to support:

* perception;
* working memory;
* long-term memory;
* awareness;
* thinking;
* reasoning;
* evaluation;
* judgment;
* decision;
* planning;
* execution;
* monitoring;
* reflection;
* metacognition;
* learning;
* supervision;
* continuity;
* self-improvement.

Gordon is designed as a persistent agent rather than a stateless prompt-response
wrapper.

Its architecture assumes:

* long-running operation;
* multiple specialized models and services;
* explicit cognitive state;
* recoverable execution;
* inspectable reasoning and decisions;
* bounded resource use;
* asynchronous and parallel activity;
* incremental learning;
* stable subsystem contracts.

# =============================================================================

# 2. CORE ARCHITECTURAL PRINCIPLE

# =============================================================================

Every subsystem must answer one question:

```
"What does this subsystem own that no other subsystem owns?"
```

Ownership must remain explicit.

A subsystem may consume or reference external state.

It must not silently become the owner of that state.

Examples:

* Working Memory owns active maintained content.
* Awareness interprets what active content is cognitively available.
* Attention allocates processing priority.
* Thinking orchestrates cognitive work.
* Reasoning derives conclusions.
* Evaluation measures artifacts and outcomes.
* Judgment determines cognitive standing.
* Decision forms commitments.
* Planning constructs executable strategies.
* Execution performs authorized actions.
* Reflection interprets experience.
* Metacognition evaluates and regulates cognitive processes.
* Learning validates and retains adaptations.
* Supervision coordinates system-wide oversight.
* Core provides runtime infrastructure, not cognition.

Duplicate ownership is an architectural defect.

# =============================================================================

# 3. CORE VERSUS COGNITION

# =============================================================================

The Core is Gordon's runtime operating-system layer.

Core owns:

* execution environment;
* component lifecycle;
* service lifecycle;
* communication infrastructure;
* runtime guarantees;
* resource coordination;
* scheduling primitives;
* state transport;
* health and integrity mechanisms;
* failure handling;
* runtime observability.

Core answers:

```
"How does the agent operate?"
```

Core does not answer:

```
"What does the agent think?"
```

Core shall not contain:

* reasoning semantics;
* values;
* beliefs;
* memory meaning;
* decisions;
* cognitive strategies;
* domain intelligence.

The Kernel is the minimal control plane inside Core.

The Kernel must remain small.

It coordinates runtime infrastructure.

It must never become an intelligence layer.

# =============================================================================

# 4. COGNITIVE PIPELINE

# =============================================================================

A simplified canonical flow is:

```
Perception

↓

Attention

↓

Working Memory

↓

Awareness

↓

Thinking

↓

Reasoning

↓

Evaluation

↓

Judgment

↓

Decision

↓

Planning

↓

Execution

↓

Monitoring

↓

Reflection

↓

Learning
```

This is not always a strict linear pipeline.

Gordon supports feedback loops, concurrent processing, escalation and repeated
cycles.

However, ownership boundaries remain valid even when control flow is cyclic.

# =============================================================================

# 5. THINKING, REASONING AND REFLECTION

# =============================================================================

These concepts must not be collapsed.

Thinking determines:

```
"What should Gordon think about next?"
```

It orchestrates:

* decomposition;
* hypothesis generation;
* branch management;
* cognitive scheduling;
* context management;
* resource budgets;
* continuation;
* termination.

Reasoning determines:

```
"What follows from the available information?"
```

Reasoning includes:

Methods:

* deductive;
* inductive;
* abductive.

Styles:

* causal;
* counterfactual;
* probabilistic;
* temporal;
* spatial;
* semantic;
* relational;
* analogical.

Expert forms:

* commonsense;
* world-model;
* systems;
* scientific;
* mathematical;
* diagnostic;
* predictive;
* strategic;
* legal;
* economic;
* moral;
* social;
* philosophical;
* metareasoning.

Reflection determines:

```
"What can be learned by reconstructing and interpreting experience?"
```

The Reflector is the reusable architectural pattern that applies Reflection to
typed targets such as:

* reasoning episodes;
* decisions;
* plans;
* executions;
* strategies;
* conversations;
* failures;
* successes;
* learning events.

Reflection may propose adaptations.

It must not apply them directly.

# =============================================================================

# 6. EVALUATION, JUDGMENT AND DECISION

# =============================================================================

Evaluation asks:

```
"How well does this artifact satisfy declared criteria?"
```

Judgment asks:

```
"What cognitive stance should Gordon adopt toward this artifact?"
```

Possible judgment dispositions include:

* accepted;
* provisionally accepted;
* rejected;
* suspended;
* deferred;
* escalated;
* requires more evidence;
* indeterminate.

Decision asks:

```
"Which admissible alternative shall become the active commitment?"
```

Decision consumes judged alternatives.

It must not consume raw unvalidated model output as authoritative commitment.

Planning then determines:

```
"How shall the commitment be achieved?"
```

Execution performs the resulting authorized plan.

# =============================================================================

# 7. AWARENESS, ATTENTION AND WORKING MEMORY

# =============================================================================

Working Memory maintains active cognitive content.

Attention allocates limited processing priority.

Awareness represents what becomes globally or self-referentially available.

These are related but distinct.

Awareness may represent:

* active content;
* self-state;
* task state;
* situational context;
* resource pressure;
* uncertainty;
* conflict;
* cognitive accessibility;
* global availability;
* meta-awareness.

Awareness must not duplicate Working Memory.

Awareness must not silently become the canonical Attention subsystem.

Adapters should preserve authoritative ownership.

# =============================================================================

# 8. MEMORY

# =============================================================================

Memory is not one undifferentiated store.

Gordon may include:

* working memory;
* episodic memory;
* semantic memory;
* autobiographical memory;
* procedural memory;
* prospective memory;
* temporary caches;
* reflective history;
* execution checkpoints.

Each memory type must define:

* what it stores;
* why it stores it;
* retention policy;
* retrieval semantics;
* mutability;
* provenance;
* authority;
* eviction;
* persistence;
* privacy and safety constraints.

Subsystem-local history is not automatically Memory.

Bounded operational history belongs to the subsystem that produces it.

Long-term retention belongs to the appropriate Memory subsystem.

# =============================================================================

# 9. MODELS AND SERVICES

# =============================================================================

Gordon is expected to coordinate heterogeneous models.

Possible services include:

* language models;
* vision-language models;
* object detection;
* segmentation;
* OCR;
* speech recognition;
* audio models;
* world models;
* latent encoders;
* sparse autoencoders;
* reasoning models;
* embedding services.

Models should be accessed through service or provider contracts.

Cognitive subsystems should not hard-code model implementations when an
abstraction can preserve flexibility.

A model provider should expose:

* identity;
* capability;
* context limits;
* availability;
* health;
* resource requirements;
* inference interface;
* lifecycle;
* failure behavior;
* observability.

Model unavailability must be explicit.

Silent fake outputs are forbidden in production paths.

# =============================================================================

# 10. STATE AUTHORITY

# =============================================================================

Every state object must have one authoritative owner.

Derived state shall remain marked as derived.

Cached state shall remain marked as cached.

External references shall remain references.

A subsystem must never silently create an authoritative copy of another
subsystem's state.

Examples:

* Awareness may hold a Working Memory snapshot.
* It does not own Working Memory.
* Reflection may reconstruct an execution trajectory.
* It does not own execution history.
* Planning may estimate resource use.
* It does not own resource allocation.
* Judgment may reference beliefs.
* It does not persist beliefs directly.

# =============================================================================

# 11. CONTRACTS AND ARTIFACTS

# =============================================================================

Interactions should occur through typed contracts.

Preferred artifacts are:

* immutable where practical;
* explicitly identified;
* versioned;
* serializable;
* validated;
* provenance-bearing;
* independently inspectable.

Avoid passing unstructured dictionaries when the schema is known.

Every major cognitive operation should produce explicit artifacts.

Examples:

* ThinkingSession;
* ReasoningTrace;
* EvaluationResult;
* JudgmentDisposition;
* Commitment;
* Plan;
* ExecutionTrace;
* AwarenessReport;
* ReflectionResult;
* LearningSignalProposal;
* HealthReport;
* IntegrityResult.

# =============================================================================

# 12. PROVENANCE

# =============================================================================

Important artifacts must preserve provenance.

Provenance should answer:

* Which subsystem produced this?
* Which component produced it?
* Which input artifacts were used?
* Which model or strategy was used?
* When was it produced?
* Under which session or cycle?
* Which revision generated it?
* Which assumptions were active?

Loss of provenance prevents reliable reflection, debugging, learning and audit.

# =============================================================================

# 13. LIFECYCLE

# =============================================================================

Subsystems are lifecycle-managed components.

Typical lifecycle states include:

* created;
* initializing;
* connecting;
* ready;
* running;
* paused;
* degraded;
* recovering;
* stopping;
* stopped;
* failed.

Lifecycle transitions must remain explicit.

Invalid transitions must not silently mutate state.

Lifecycle operations should be idempotent where practical.

Initialization must not conceal missing mandatory dependencies.

Shutdown must release owned resources.

Recovery must preserve failure history.

# =============================================================================

# 14. DEGRADED OPERATION

# =============================================================================

Gordon must degrade explicitly rather than fabricate normal operation.

A degraded subsystem should expose:

* unavailable dependencies;
* active fallbacks;
* stale inputs;
* disabled capabilities;
* confidence penalties;
* affected outputs;
* recovery conditions.

Fallbacks are permitted for:

* testing;
* isolated development;
* explicitly configured degraded operation.

Fallbacks must never silently impersonate authoritative production services.

# =============================================================================

# 15. HEALTH, VALIDATION AND INTEGRITY

# =============================================================================

These responsibilities are distinct.

Health asks:

```
"Is the subsystem operational?"
```

Validation asks:

```
"Does this artifact satisfy its declared contract?"
```

Integrity asks:

```
"Is the subsystem architecture and internal state coherent?"
```

Each major subsystem should expose structured:

* health;
* statistics;
* diagnostics;
* validation;
* integrity checks.

Validation and integrity should be observational by default.

They must not silently repair or mutate state unless an explicit repair mode is
requested.

# =============================================================================

# 16. OBSERVABILITY

# =============================================================================

No consumer should need to inspect private attributes.

Subsystems should expose:

* current state;
* health;
* metrics;
* traces;
* recent transitions;
* bounded histories;
* failures;
* dependency status;
* lifecycle;
* integrity findings.

Observability is a first-class architectural requirement.

It is essential for autonomous recovery, reflection and learning.

# =============================================================================

# 17. DETERMINISM

# =============================================================================

Given identical:

* configuration;
* inputs;
* state;
* clock values;
* model outputs;
* random source;

a deterministic subsystem should produce equivalent results.

Time-dependent logic should use:

* wall time for timestamps;
* monotonic time for durations.

Random behavior must use injected reproducible sources.

Generated identifiers may vary unless identity generation is injected for tests.

# =============================================================================

# 18. CONCURRENCY

# =============================================================================

Concurrency ownership must be explicit.

Possible models include:

* engine-level locking;
* event-loop ownership;
* actor ownership;
* externally synchronized components.

Do not claim thread safety without implementing it.

Immutable artifacts may be safely shared.

Mutable engines require controlled ownership.

Avoid parallel implementations of synchronous and asynchronous APIs unless the
runtime architecture requires both.

# =============================================================================

# 19. RESOURCE MANAGEMENT

# =============================================================================

Gordon is compute-intensive and resource-aware.

Subsystems should account for:

* GPU memory;
* system memory;
* context windows;
* token budgets;
* storage;
* network;
* energy;
* latency;
* parallel workers;
* service availability.

Cognitive subsystems may observe and request resources.

Canonical resource ownership belongs to runtime and resource-management layers.

Resource exhaustion must remain explicit.

# =============================================================================

# 20. LEARNING AND ADAPTATION

# =============================================================================

Reflection does not equal Learning.

Learning does not equal immediate mutation.

The safe flow is:

```
Experience

↓

Evaluation

↓

Reflection

↓

Credit Assignment

↓

Insight

↓

Learning-Signal Proposal

↓

Validation

↓

Authorization

↓

Adaptation

↓

Outcome Monitoring
```

Learning must consider:

* confidence;
* attribution quality;
* reversibility;
* cumulative change;
* cooldown;
* stability;
* rollback;
* outcome verification.

No reflective subsystem should directly rewrite strategy weights, constraints,
priorities or model parameters.

# =============================================================================

# 21. NO PARALLEL MECHANISMS

# =============================================================================

Before implementing anything:

* search for existing ownership;
* inspect neighboring packages;
* inspect interfaces;
* inspect registries;
* inspect runtime entry points;
* inspect public imports;
* inspect tests;
* inspect configuration conventions.

Extend existing abstractions where practical.

Do not create:

* duplicate registries;
* duplicate lifecycle systems;
* duplicate event buses;
* duplicate schedulers;
* duplicate state stores;
* duplicate model loaders;
* duplicate memory implementations;
* duplicate cognitive engines.

Parallel mechanisms increase architectural entropy.

# =============================================================================

# 22. PACKAGE DESIGN

# =============================================================================

A package should represent one cohesive subsystem.

Do not split files merely to create a large tree.

Do not keep unrelated responsibilities in one file merely to reduce file count.

Create files based on stable responsibility boundaries.

Typical package elements include:

* **init**.py;
* **meta**.py;
* **base**.py;
* **registry**.py;
* config.py;
* constants.py;
* enums.py;
* exceptions.py;
* interfaces.py;
* models.py;
* factories.py;
* validation;
* observability;
* tests.

The package root should expose a curated public API through `__all__`.

Internal helpers must not leak accidentally.

# =============================================================================

# 23. IMPORT DIRECTION

# =============================================================================

Dependency direction should remain acyclic.

Preferred flow:

```
models / interfaces / configuration

↓

low-level components

↓

strategies / policies / adapters

↓

pipelines

↓

engines / coordinators

↓

factories / public API
```

Models should not import engines.

Adapters should not import coordinators.

Lower-level packages should not import higher-level orchestration.

Use protocols, dependency injection and `TYPE_CHECKING` where appropriate.

# =============================================================================

# 24. IMPLEMENTATION DISCIPLINE

# =============================================================================

Use:

* complete type annotations;
* immutable data models;
* explicit enums;
* structured exceptions;
* dependency injection;
* narrow interfaces;
* bounded histories;
* deterministic tests;
* explicit configuration;
* explicit lifecycle;
* explicit degradation;
* clear documentation;
* structured logging.

Avoid:

* broad unqualified `Any`;
* unbounded dictionaries;
* mutable default arguments;
* hidden global state;
* import-time engine creation;
* silent exception suppression;
* magic thresholds;
* undocumented fallbacks;
* circular imports;
* fabricated outputs;
* placeholder modules;
* duplicated implementations.

# =============================================================================

# 25. TESTING EXPECTATIONS

# =============================================================================

Tests should verify:

* imports;
* public API;
* configuration;
* models;
* serialization;
* lifecycle;
* state transitions;
* dependency failures;
* degraded mode;
* recovery;
* history bounds;
* concurrency assumptions;
* deterministic behavior;
* integrity;
* ownership boundaries;
* absence of duplicate implementations.

Tests must cover actual behavior.

Import-only tests are insufficient.

# =============================================================================

# 26. GIT AND CHANGE SAFETY

# =============================================================================

Before major changes:

* inspect repository state;
* identify uncommitted work;
* preserve unrelated modifications;
* create a safe checkpoint when authorized;
* avoid destructive bulk rewrites;
* avoid deleting uncertain code without dependency analysis.

After changes:

* run targeted tests;
* run package import checks;
* run broader tests where feasible;
* inspect diffs;
* report modified files;
* report removed files;
* report compatibility effects;
* report unresolved failures.

Never overwrite user work silently.

# =============================================================================

# 27. FUTURE C++ MIGRATION

# =============================================================================

Gordon may gradually move runtime-critical components toward C++.

Python implementations should therefore favor:

* explicit types;
* stable contracts;
* clear ownership;
* bounded data structures;
* deterministic lifecycle;
* minimal metaprogramming in core contracts;
* serialization-ready artifacts;
* narrow interfaces;
* explicit error handling.

Python remains valuable for:

* experimentation;
* model integration;
* research;
* orchestration;
* rapid cognitive prototyping.

Architectural clarity matters more than language preference.

# =============================================================================

# 28. CONTRIBUTOR DECISION RULE

# =============================================================================

Before implementing a change, answer:

1. Which subsystem owns this responsibility?

2. Does an implementation already exist?

3. Is the new behavior cognitive, runtime, perceptual, memory-related or
   infrastructural?

4. Which artifacts enter and leave the subsystem?

5. Who owns the source state?

6. What happens when dependencies fail?

7. How is the behavior observed?

8. How is it tested?

9. How is it recovered?

10. Does this create a duplicate mechanism?

If these questions cannot be answered, the implementation is not yet
architecturally ready.

# =============================================================================

# 29. FINAL PRINCIPLE

# =============================================================================

Gordon must remain understandable as one system.

Every local implementation decision contributes either to:

* architectural coherence;

or:

* architectural entropy.

Prefer explicit ownership over convenience.

Prefer contracts over hidden coupling.

Prefer adaptation proposals over uncontrolled mutation.

Prefer degraded truth over fabricated success.

Prefer one authoritative mechanism over parallel implementations.

Prefer inspectable cognition over opaque behavior.

The contributor's responsibility is not only to make the requested feature
work.

The contributor's responsibility is to preserve Gordon as a stable,
explainable, extensible and increasingly capable autonomous cognitive
architecture.

# =============================================================================

# END OF GORDON DEVELOPMENT CONTEXT

# =============================================================================

# =============================================================================

# GORDON COGNITIVE ARCHITECTURE

# PARTICIPATION PRIMER

# ABSOLUTE DEVELOPMENT KNOWLEDGE

# ARCHITECTURAL IDENTITY,

# SUBSYSTEM BOUNDARIES,

# RUNTIME DISCIPLINE,

# COGNITIVE CONTRACTS,

# IMPLEMENTATION RULES

# =============================================================================

# PURPOSE

This document defines the minimum architectural knowledge required to
participate responsibly in developing Gordon.

It is not a complete description of every subsystem.

It is not a tutorial for the repository.

It is not a substitute for inspecting the code, tests, contracts and runtime
integration points relevant to a task.

It establishes the assumptions that every contributor, coding agent and
architectural reviewer must understand before modifying Gordon.

A contributor who does not understand these principles is not prepared to make
structural changes to the system.

# =============================================================================

# 1. WHAT GORDON IS

# =============================================================================

Gordon is an autonomous cognitive agent architecture.

It is not merely:

* a chatbot;
* an LLM wrapper;
* a collection of prompts;
* a tool-calling loop;
* a workflow engine;
* a monolithic reasoning model;
* a set of unrelated AI utilities.

Gordon is intended to coordinate persistent cognition across specialized
subsystems responsible for:

* perception;
* working memory;
* long-term memory;
* awareness;
* attention;
* thinking;
* reasoning;
* simulation;
* prediction;
* evaluation;
* judgment;
* decision;
* planning;
* execution;
* reflection;
* metacognition;
* supervision;
* continuity;
* learning;
* self-improvement.

The architecture exists to make cognition explicit, modular, inspectable,
replaceable and governable.

# =============================================================================

# 2. THE FUNDAMENTAL ARCHITECTURAL DISTINCTION

# =============================================================================

Gordon separates runtime infrastructure from cognition.

Core answers:

```
"How does the agent operate?"
```

Cognition answers:

```
"What does the agent think, represent, infer, evaluate or decide?"
```

Core may own:

* lifecycle;
* execution environment;
* scheduling;
* communication;
* service management;
* resource coordination;
* runtime guarantees;
* state transport;
* component registration;
* health and integrity infrastructure.

Core shall not contain:

* reasoning semantics;
* values;
* beliefs;
* memory meaning;
* judgment;
* decision criteria;
* planning semantics;
* cognitive strategies.

The kernel is the minimal runtime control plane inside Core.

The kernel shall remain small.

The kernel is not an intelligence layer.

# =============================================================================

# 3. SUBSYSTEMS ARE OWNERS, NOT FILE CATEGORIES

# =============================================================================

Every subsystem must own a distinct class of state, behavior and contracts.

A subsystem boundary is justified by responsibility and authority, not by file
size or terminology.

Each subsystem must define:

* what it owns;
* what it references;
* what it consumes;
* what it produces;
* what it must never own;
* which other subsystem is authoritative for shared concepts.

Examples:

Working Memory owns active maintained content.

Awareness observes and interprets cognitive availability.

Attention owns allocation of processing priority.

Thinking orchestrates cognitive work.

Reasoning derives conclusions.

Evaluation measures artifacts and outcomes.

Judgment determines cognitive standing.

Decision selects commitments.

Planning constructs executable strategies.

Execution performs authorized actions.

Reflection interprets experience.

Metacognition evaluates and regulates cognitive processes.

Supervision coordinates system-wide control and intervention.

No subsystem may quietly absorb another subsystem's authority merely because
the required data is convenient to access.

# =============================================================================

# 4. COGNITIVE PIPELINE

# =============================================================================

A simplified canonical flow is:

```
Perception
    ↓
Attention
    ↓
Working Memory
    ↓
Awareness
    ↓
Thinking
    ↓
Reasoning
    ↓
Evaluation
    ↓
Judgment
    ↓
Decision
    ↓
Planning
    ↓
Execution
    ↓
Monitoring
    ↓
Evaluation
    ↓
Reflection
    ↓
Learning
```

This is not always a strict linear pipeline.

Gordon supports:

* feedback loops;
* parallel cognitive work;
* recursive evaluation;
* replanning;
* suspended judgment;
* interrupted execution;
* reflective reconsideration;
* metacognitive control;
* supervisory intervention.

However, architectural ownership must remain clear even when control flow is
cyclic.

# =============================================================================

# 5. THINKING IS NOT REASONING

# =============================================================================

Thinking is the orchestration of active cognition.

Thinking determines:

* what should be processed next;
* which cognitive capability should be invoked;
* how goals should be decomposed;
* how branches should be expanded or pruned;
* how cognitive budgets should be allocated;
* when cognition should continue, pause or terminate.

Reasoning performs inference.

Reasoning methods include:

* deduction;
* induction;
* abduction.

Reasoning styles include:

* causal;
* counterfactual;
* probabilistic;
* temporal;
* spatial;
* semantic;
* relational;
* analogical.

Expert reasoning applies methods and styles to specialized domains such as:

* commonsense;
* world-model reasoning;
* systems reasoning;
* scientific reasoning;
* mathematical reasoning;
* diagnostic reasoning;
* predictive reasoning;
* strategic reasoning;
* legal reasoning;
* economic reasoning;
* moral reasoning;
* social reasoning;
* normative reasoning;
* constitutional reasoning.

Thinking may invoke these reasoners.

Thinking shall not reimplement their inference logic.

# =============================================================================

# 6. EVALUATION, JUDGMENT AND DECISION ARE DIFFERENT

# =============================================================================

Evaluation asks:

```
"How well does this artifact satisfy declared criteria?"
```

Judgment asks:

```
"What cognitive stance should Gordon adopt toward this artifact?"
```

Decision asks:

```
"Which acceptable alternative should become an operational commitment?"
```

Evaluation may produce:

* quality scores;
* constraint findings;
* coherence measures;
* risk estimates;
* performance measurements.

Judgment may produce:

* accepted;
* provisionally accepted;
* rejected;
* suspended;
* deferred;
* escalated;
* requires more evidence;
* indeterminate.

Decision produces:

* a selected alternative;
* an explicit commitment;
* authorization state;
* activation conditions;
* revision conditions.

These stages must not be collapsed into one function that scores and executes
an option.

# =============================================================================

# 7. PLANNING IS NOT EXECUTION

# =============================================================================

Planning transforms commitments into executable strategies.

Planning owns:

* decomposition;
* task generation;
* dependency analysis;
* sequencing;
* resource planning;
* contingency generation;
* rollback planning;
* optimization;
* plan revision.

Execution owns:

* action dispatch;
* runtime coordination;
* resource acquisition;
* retries;
* timeouts;
* pause;
* resume;
* cancellation;
* rollback initiation;
* effect verification;
* completion reporting.

A Plan shall not execute itself.

A Commitment shall not execute itself.

Execution shall not invent goals or silently replan.

# =============================================================================

# 8. AWARENESS, INTROSPECTION, REFLECTION AND METACOGNITION

# =============================================================================

These concepts are related but not interchangeable.

Awareness represents what is presently cognitively available.

Introspection examines current internal cognitive content.

Reflection reconstructs and interprets completed or ongoing experience.

Metacognition evaluates and regulates cognitive processes.

Meta-awareness represents awareness of the current awareness process.

Awareness may expose:

```
"A conflict is active."
```

Introspection may determine:

```
"The conflict comes from incompatible assumptions."
```

Reflection may determine:

```
"This conflict repeatedly appears after a particular planning strategy."
```

Metacognition may determine:

```
"That strategy should be suspended or replaced."
```

These responsibilities must remain separate.

# =============================================================================

# 9. THE REFLECTOR PATTERN

# =============================================================================

Reflection is the cognitive capability.

The Reflector is the reusable architecture that applies Reflection to typed
targets.

A Reflector may analyze:

* reasoning;
* judgments;
* decisions;
* plans;
* executions;
* strategies;
* conversations;
* learning episodes;
* self-model transitions.

Canonical Reflector flow:

```
Observe
    ↓
Reconstruct
    ↓
Analyze
    ↓
Attribute
    ↓
Generate Findings
    ↓
Synthesize Insights
    ↓
Propose Adaptation
    ↓
Validate
    ↓
Publish
```

The Reflector may produce:

* findings;
* insights;
* credit assignments;
* responsibility assessments;
* adaptation proposals;
* learning-signal proposals.

The Reflector shall not directly mutate the reflected subsystem.

# =============================================================================

# 10. LEARNING REQUIRES AUTHORIZATION AND STABILITY

# =============================================================================

Reflection does not equal learning.

A reflective insight does not automatically justify behavioral change.

The safe flow is:

```
Experience
    ↓
Evaluation
    ↓
Reflection
    ↓
Credit Assignment
    ↓
Learning-Signal Proposal
    ↓
Learning Validation
    ↓
Authorization
    ↓
Rate Limiting
    ↓
Target-Owned Adaptation
    ↓
Outcome Monitoring
    ↓
Possible Rollback
```

Learning systems must guard against:

* repeated failure amplification;
* runaway weight changes;
* unstable strategy oscillation;
* duplicated learning signals;
* stale reflective conclusions;
* misassigned responsibility;
* irreversible unvalidated adaptation.

Every applied change should preserve:

* source reflection;
* target;
* authorization;
* magnitude;
* confidence;
* rollback information;
* outcome lineage.

# =============================================================================

# 11. WORKING MEMORY AND THE SUPERVISORY EXECUTIVE MODEL

# =============================================================================

Working Memory is a first-class cognitive substrate.

It is not merely an LLM context buffer.

Working Memory may contain:

* active goals;
* hypotheses;
* perceptual artifacts;
* unresolved conflicts;
* plan fragments;
* reasoning products;
* attentional priorities;
* current task state;
* temporary bindings.

The Supervisory Executive Model may organize Working Memory through:

* indexing;
* prioritization;
* summarization;
* cleanup;
* restructuring;
* context compression;
* relevance maintenance.

The Supervisory Executive Model is not merely a router.

It is intended to maintain coherent, useful and resource-aware active cognitive
state.

Subsystems observing Working Memory shall use explicit read-oriented contracts.

They shall not create parallel authoritative Working Memory implementations.

# =============================================================================

# 12. MODELS ARE SERVICES, NOT THE ARCHITECTURE

# =============================================================================

Gordon may use:

* language models;
* vision-language models;
* object detectors;
* OCR models;
* speech models;
* autoencoders;
* sparse autoencoders;
* hierarchical reasoning models;
* world models;
* simulation models.

These are computational providers.

They do not define subsystem ownership.

A subsystem shall depend on capabilities through contracts such as:

* generate;
* encode;
* detect;
* transcribe;
* classify;
* simulate;
* evaluate.

The architecture must not become hard-coded to one model family, runtime or
vendor.

Model-specific integrations should be isolated behind adapters, services or
providers.

# =============================================================================

# 13. CONTRACTS OVER INTERNAL IMPORTS

# =============================================================================

Subsystems shall communicate through explicit contracts.

Preferred mechanisms include:

* protocols;
* immutable models;
* typed requests;
* typed results;
* adapters;
* registries;
* events;
* service interfaces.

A subsystem should not import another subsystem's private implementation merely
to obtain data.

Direct internal imports create:

* circular dependencies;
* hidden ownership;
* brittle tests;
* duplicated logic;
* impossible replacement;
* unclear lifecycle coupling.

Use narrow interfaces and dependency injection.

# =============================================================================

# 14. IMMUTABLE COGNITIVE ARTIFACTS

# =============================================================================

Completed cognitive artifacts should be immutable where practical.

Examples:

* reasoning results;
* evaluation results;
* judgments;
* commitments;
* plans;
* awareness reports;
* reflection results;
* learning proposals;
* execution reports.

Revision shall create a new version.

Historical artifacts shall not be overwritten.

Every revision should preserve:

* predecessor;
* trigger;
* changed fields;
* retained evidence;
* supersession relation;
* provenance.

This enables deterministic replay, auditability and safe downstream
invalidation.

# =============================================================================

# 15. PROVENANCE IS MANDATORY

# =============================================================================

Every important cognitive artifact must answer:

* where did this come from;
* which subsystem produced it;
* which inputs were used;
* which configuration was active;
* which model or strategy contributed;
* when was it produced;
* which session or cycle owns it;
* which artifact does it supersede;
* which downstream artifacts depend on it.

Provenance is not decorative metadata.

It is required for:

* reflection;
* credit assignment;
* debugging;
* invalidation;
* evaluation;
* governance;
* trust;
* rollback;
* continuity.

# =============================================================================

# 16. GRAPHS REPRESENT LINEAGE, NOT OWNERSHIP

# =============================================================================

Gordon may maintain graphs such as:

* Thought Process Graph;
* Cognitive Execution Graph;
* Judgment Dependency Graph;
* Commitment Graph;
* Plan Dependency Graph;
* Execution Graph;
* Awareness State Graph;
* Reflection Dependency Graph.

These graphs represent:

* derivation;
* dependency;
* temporal sequence;
* revision;
* causality;
* execution order;
* supersession;
* downstream reliance.

A graph shall not become a duplicate source of truth for state owned by another
subsystem.

Graphs preserve lineage.

Subsystems preserve authority.

# =============================================================================

# 17. DETERMINISM

# =============================================================================

Given identical:

* inputs;
* configuration;
* prior state;
* clock values;
* random source;
* model outputs;
* dependency snapshots;

a deterministic subsystem should produce equivalent outputs.

Determinism is required for:

* testing;
* replay;
* debugging;
* governance;
* incident analysis;
* reflection;
* credit assignment.

When stochastic behavior is required:

* inject the random source;
* preserve the seed;
* identify the strategy;
* record sampling parameters;
* make stochastic behavior explicit.

Do not use hidden randomness.

# =============================================================================

# 18. TIME

# =============================================================================

Use wall-clock time for external timestamps.

Use monotonic time for durations and deadlines.

Do not calculate elapsed time by repeatedly adding the full duration since an
unchanged historical timestamp.

Track per-cycle deltas.

Time-sensitive components must be testable with an injected clock.

# =============================================================================

# 19. LIFECYCLE

# =============================================================================

Every significant subsystem should expose an explicit lifecycle.

Typical states may include:

* created;
* initializing;
* connecting;
* ready;
* running;
* paused;
* degraded;
* recovering;
* stopping;
* stopped;
* failed.

Lifecycle transitions must be validated.

Invalid transitions shall not silently mutate state.

Initialization, startup, pause, resume, recovery and shutdown must have clear
semantics.

Avoid import-time initialization of active subsystem instances.

# =============================================================================

# 20. DEGRADED MODE

# =============================================================================

Unavailable dependencies must never be hidden behind convincing fake outputs.

A subsystem in degraded mode must report:

* unavailable capabilities;
* stale sources;
* active fallbacks;
* disabled behavior;
* confidence penalties;
* recovery conditions.

Fallbacks may exist for:

* isolated testing;
* optional dependencies;
* explicit recovery behavior;
* reduced functionality.

A required production dependency shall not silently become a dummy provider.

# =============================================================================

# 21. HEALTH, VALIDATION, INTEGRITY AND GOVERNANCE

# =============================================================================

These are different concerns.

Health asks:

```
"Is the subsystem currently operational?"
```

Validation asks:

```
"Does this artifact satisfy its declared contract?"
```

Integrity asks:

```
"Is the subsystem structurally and internally consistent?"
```

Governance asks:

```
"Does the subsystem behave acceptably across time and many sessions?"
```

Validation should generally remain observational.

Governance should generally remain observational.

Repair must be explicit.

Each major subsystem should expose structured:

* health;
* diagnostics;
* statistics;
* validation;
* integrity checks;
* recent failures;
* degradation state.

A boolean alone is usually insufficient.

# =============================================================================

# 22. OBSERVABILITY

# =============================================================================

No consumer should need to inspect private attributes to understand subsystem
state.

Public observability should expose:

* current lifecycle;
* current state;
* current artifact;
* recent transitions;
* active dependencies;
* errors;
* metrics;
* bounded histories;
* health;
* diagnostics;
* integrity findings.

Observability must not mutate the subsystem.

# =============================================================================

# 23. ERROR HANDLING

# =============================================================================

Use typed exceptions.

Do not use broad exception suppression as normal control flow.

Failures must preserve:

* stage;
* component;
* input context;
* partial results;
* recoverability;
* degradation availability;
* recovery options;
* provenance.

A failure should not become:

* an empty dictionary;
* a false healthy status;
* a fabricated neutral output;
* an unexplained `None`.

# =============================================================================

# 24. RESOURCE AWARENESS

# =============================================================================

Gordon is intended to operate across heterogeneous and constrained compute.

Subsystems may need to account for:

* GPU memory;
* system memory;
* model availability;
* context-window use;
* tokens;
* latency;
* storage;
* network;
* energy;
* parallel workers;
* service health.

Resource information should be consumed through explicit monitoring contracts.

Cognitive subsystems should not directly own infrastructure allocation unless
that is their declared responsibility.

# =============================================================================

# 25. CONCURRENCY

# =============================================================================

Every mutable subsystem must declare its concurrency model.

Examples:

* engine-level lock;
* actor ownership;
* event-loop ownership;
* external synchronization;
* immutable snapshot processing.

Do not claim thread safety because dataclasses are frozen while the owning
engine remains mutable.

Mutable histories, registries, caches and lifecycle state require deliberate
coordination.

# =============================================================================

# 26. PACKAGE DESIGN

# =============================================================================

A package is not automatically better than a module.

A package is justified when the subsystem contains separable internal
responsibilities with one clear authoritative boundary.

Do not:

* split files mechanically;
* create empty modules;
* duplicate models across subpackages;
* create multiple engines with overlapping authority;
* scatter lifecycle logic;
* scatter configuration;
* expose all internal helpers publicly.

A production subsystem package should normally contain:

* metadata;
* configuration;
* constants;
* enums;
* exceptions;
* interfaces;
* immutable models;
* factories;
* runtime coordination;
* validation;
* observability;
* tests;
* a curated public API.

# =============================================================================

# 27. PUBLIC API

# =============================================================================

The package root should expose only canonical supported objects.

Use:

```
__all__
```

Avoid wildcard exports.

Internal helpers should remain internal.

Public names must have stable semantics.

Compatibility aliases must point to canonical implementations.

Do not maintain two sources of truth for backward compatibility.

# =============================================================================

# 28. REGISTRIES

# =============================================================================

Registries may manage:

* strategies;
* providers;
* adapters;
* engines;
* validators;
* observers;
* target-specific Reflectors.

Registration shall be explicit and inspectable.

Avoid uncontrolled import-time recursive discovery unless Gordon's runtime
standardizes and governs that mechanism.

A registry must not become a hidden service locator containing arbitrary global
state.

# =============================================================================

# 29. TESTING

# =============================================================================

Tests must verify behavior and architecture.

Required categories commonly include:

* imports;
* public API;
* configuration;
* models;
* immutability;
* serialization;
* lifecycle;
* deterministic replay;
* dependency failures;
* degraded mode;
* recovery;
* concurrency assumptions;
* history bounds;
* validation;
* integrity;
* ownership boundaries;
* no duplicate implementation;
* no circular imports.

Tests should include failure cases.

Import success alone does not constitute subsystem completion.

# =============================================================================

# 30. REPOSITORY DISCOVERY

# =============================================================================

Before modifying Gordon:

1. Determine the repository root.

2. Determine the authoritative target path.

3. Inspect neighboring subsystem conventions.

4. Inspect runtime entry points.

5. Inspect current imports and public API.

6. Search for duplicate implementations.

7. Identify authoritative state owners.

8. Identify tests.

9. Identify configuration and lifecycle conventions.

10. Identify integration points.

Do not assume a path from a prompt example.

Do not create a second architecture beside an existing one.

# =============================================================================

# 31. CHANGE DISCIPLINE

# =============================================================================

Before a structural change:

* understand the current subsystem;
* identify consumers;
* identify contracts;
* identify state ownership;
* identify lifecycle impact;
* identify migration requirements;
* identify tests;
* identify rollback options.

Prefer extending canonical abstractions over creating parallel mechanisms.

Preserve working behavior whenever practical.

Remove obsolete code only after consumers have migrated.

Do not perform opportunistic unrelated refactoring during a focused task.

# =============================================================================

# 32. GIT AND RECOVERY

# =============================================================================

Gordon has experienced catastrophic repository loss.

Development must assume that local-only state is unsafe.

Significant work should be protected through:

* version control;
* remote pushes;
* verified backups;
* recoverable checkpoints;
* clear commits;
* reproducible configuration;
* documented migrations.

Architectural work without durable versioning is incomplete operationally.

# =============================================================================

# 33. WHAT MUST NEVER HAPPEN

# =============================================================================

Never:

* duplicate an authoritative subsystem;
* hide ownership;
* silently mutate another subsystem's state;
* collapse reasoning, judgment and decision;
* let plans execute themselves;
* let reflection apply learning directly;
* fabricate model outputs;
* fabricate missing evidence;
* present heuristics as proof of consciousness;
* present correlation as causation;
* silently activate fallbacks;
* use hidden randomness;
* overwrite historical cognitive artifacts;
* leave unbounded histories;
* create hidden global engines;
* create circular cognitive imports;
* claim health after internal failure;
* bypass authorization;
* bypass validation;
* bypass provenance;
* bypass tests;
* treat a passing import as production readiness.

# =============================================================================

# 34. THE REQUIRED DEVELOPMENT MINDSET

# =============================================================================

The goal is not merely working code.

The goal is a stable autonomous cognitive architecture.

A locally convenient solution may be globally destructive.

Every change must be evaluated according to:

* architectural ownership;
* long-term extensibility;
* inspectability;
* replaceability;
* deterministic behavior;
* resource cost;
* failure containment;
* cognitive correctness;
* integration safety;
* future migration to stronger typing or systems implementations.

The correct question is not only:

```
"Does this run?"
```

The correct questions are:

```
"Which subsystem owns this?"

"Which contract does this satisfy?"

"Which state becomes authoritative?"

"How is it observed?"

"How does it fail?"

"How is it recovered?"

"How is it tested?"

"How can it be replaced?"

"How can Gordon explain what happened?"
```

# =============================================================================

# FINAL PRINCIPLE

# =============================================================================

Gordon is a system of explicit cognitive responsibilities coordinated by an
explicit runtime.

Its architecture depends on preserving distinctions.

Core operates.

Perception observes.

Memory maintains.

Awareness exposes.

Attention prioritizes.

Thinking orchestrates.

Reasoning infers.

Evaluation measures.

Judgment accepts or rejects.

Decision commits.

Planning prepares.

Execution acts.

Reflection interprets experience.

Learning proposes retained change.

Metacognition regulates cognition.

Supervision governs the whole.

Every contributor must preserve these boundaries while enabling them to work
together through typed, observable, testable and provenance-preserving
contracts.

That is the minimum knowledge required to participate in developing Gordon.

# =============================================================================

# END OF PARTICIPATION PRIMER

# =============================================================================
