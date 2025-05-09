# Developer Guide

- [Building the docs](#building-the-docs)
- [Running tests](#running-tests)
- [Run tests the lazy way](#run-tests-the-lazy-way)
- [Bump a new version](#bump-a-new-version)

## Building the docs

Most of the documentation is static and does not need to be "built". That being said the jupyter notebooks that serve as demos need to be built whenever they are changed.

```
$ poe docs
```

## Running tests

Run tests using [`pytest`](https://docs.pytest.org/en/latest/).

Install dev dependencies:

```
poe develop
```

Run quick tests (skip slow and online):

```
poe test
```

Run all tests:

```
poe test-all
```

You can also run tests on the notebooks.

```
poe test-notebooks
```

Check `black` formatting:

```
poe lint
```

## Bump a new version

Make a new version of `osprey` in the following steps:

- Make sure everything is committed to GitHub.
- Update `CHANGES.md` with the next version.
- Dry Run: `bumpversion --dry-run --verbose --new-version 0.8.1 patch`
- Do it: `bumpversion --new-version 0.8.1 patch`
- ... or: `bumpversion --new-version 0.9.0 minor`
- Push it: `git push`
- Push tag: `git push --tags`

See the [bumpversion](https://pypi.org/project/bumpversion/) documentation for details.
