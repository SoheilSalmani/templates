# A readiness set for a codebase

Read this for any set whose target is a repository the learner is about to work in.

## Contents

- What the set is for
- The stack
- The features
- Ranking
- The exercises
- Where the set goes
- The reply

## What the set is for

A readiness set answers one question: does the learner master the features this codebase relies on, well enough to read and change it without stopping at every line? It tests those features. It does not test the codebase: what a function does, how a module works, or why the design is what it is.

**Nothing from the repository goes into the set**: no code, no file or identifier names, no domain terms, no data, no secrets. The set lives in the learner's activities, which may be public; the repository may be private, and a client's code never leaves it.

## The stack

The manifests name the languages, frameworks and libraries; the lockfiles and toolchain files pin their versions.

| Ecosystem | Manifest | Versions |
| --- | --- | --- |
| Rust | `Cargo.toml`, workspace members included | `Cargo.lock`, `rust-toolchain.toml`, `rust-version` |
| Python | `pyproject.toml` | `uv.lock`, `.python-version` |
| JavaScript, TypeScript | `package.json` | the lockfile, `tsconfig.json` |
| Go | `go.mod` | `go.sum` |
| Java, Kotlin, Scala | `build.gradle.kts`, `pom.xml`, `build.sbt` | the wrapper, version catalogs |
| Infrastructure | `Dockerfile`, compose files, CI workflows, Terraform | image tags, provider versions |

The exercises target those versions, and the docs read are the docs for them.

## The features

List the features the code actually uses, and count each one with the search tool across the source, leaving out vendored, generated and fixture code. For Rust:

| Feature | Search for |
| --- | --- |
| traits and implementations | `trait `, `impl … for` |
| generics and bounds | `where`, `<T: ` |
| lifetimes | `&'a`, `<'a` |
| trait objects | `dyn ` |
| error handling | `-> Result<`, `?`, the error crates (`thiserror`, `anyhow`) |
| closures and iterators | `.map(`, `.filter(`, `.collect` |
| ownership and sharing | `Box<`, `Rc<`, `Arc<`, `RefCell<`, `Mutex<` |
| async | `async fn`, `.await`, the runtime crate |
| macros | `macro_rules!`, `#[derive(` |
| unsafe code and FFI | `unsafe`, `extern "C"`, `#[repr(C)]` |
| conditional compilation | `#[cfg(`, `[features]` in `Cargo.toml` |
| tests | `#[test]`, a `tests/` directory |

For another language, build the same table from its own feature list: for Python, decorators, context managers, generators, `async`, type hints with generics and protocols, dataclasses; for TypeScript, generics, union types and narrowing, `async`, modules. Then add each framework's core API and the libraries the code calls most, with the parts of their API it uses.

Counts are rough: a pattern also matches comments, strings and look-alike syntax. Read a sample of each feature's matches before ranking it.

## Ranking

Keep a feature when the code uses it often, when it sits in the core path rather than in a build script or a test helper, or when code that uses it is hard to read without knowing it. A single `unsafe` block in the core earns an exercise; a macro used once in a build script does not. Drop the rest, and say so.

Order what is kept by dependency, not by count: traits before trait objects, ownership before lifetimes, futures before the runtime that runs them.

## The exercises

- **A fresh project with a neutral domain of its own**, unrelated to the codebase's: a URL shortener, a log parser, a rate limiter, a key-value store.
- **Real tasks that combine the features the way the codebase does**: a worker pool on the runtime's tasks and channels that shuts down cleanly; a plugin registry of trait objects looked up by name; a parser that returns a custom error type through `?`.
- **A test of mastery, not a first lesson.** The learner is expected to know or study these features, so the items give little guidance and name a feature only when the task cannot make it inevitable; the solutions hold the tests that pin the behaviour.
- **A break or fix item for each feature that fails in a characteristic way**: a borrow-checker error, a deadlock, a future that never runs.
- **A capstone** combining the top features in one program the learner could imagine shipping.

## Where the set goes

In the learner's set for the language or framework, such as `rust-activities`, as a new part named after the features: `## Iterators, lifetimes and unsafe FFI`, never after the repository. Never in the repository itself, and never committed to it.

## The reply

It shows the inventory as a table, feature, count, decision, so the learner sees what the codebase needs and why each exercise exists:

| Feature | Uses | Decision |
| --- | --- | --- |
| closures and iterators | about 500 | exercise 2, inside a real task |
| lifetimes | about 400 | exercises 3 and 4 |
| trait objects | 4 | skipped: barely used |
| integer types | many | skipped: carded under `Tool:Rust` |
