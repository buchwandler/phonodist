# Command-line interface

## Synopsis

```text
phonodist --version
phonodist compare LANGUAGE SOURCE TARGET [--explain] [--json]
phonodist diff SOURCE TARGET [--language LANGUAGE] [--explain] [--json]
```

The CLI accepts IPA strings as positional arguments. Quote them when your shell might interpret punctuation or whitespace.

## `phonodist compare`

`compare` requires a language/profile tag as its first positional argument and uses the `feature-align/1` metric. Stress is ignored. Add `--explain` to include alignment operations.

```bash
phonodist compare de-DE 'n̩' 'ən' --explain
```

Use `--json` to emit the serialized `DistanceResult` dataclass structure instead of the human-readable summary.

## `phonodist diff`

`diff` uses `ipa-compare/1` to report structural differences. A language profile is optional with `--language`; stress is preserved and compared structurally. Ordinary pronunciation differences are diagnostic results and do not make the command fail.

```bash
phonodist diff 'wɪɹ' 'wˈɪɹ'
phonodist diff --language de-DE 't͡s' 'ts'
phonodist diff --explain 'ˌa' 'ˈa'
phonodist diff --json 'p' 'b'
```

`--explain` adds stress and segment alignment operations. `--json` emits the serialized `PronunciationComparison` structure, including its embedded segmental result.

## JSON output

Both commands serialize their result dataclasses as JSON when `--json` is supplied. The structure contains nested result and pronunciation data; use the Python API when you need typed objects rather than serialized output.

## Exit status and errors

Package/domain errors are printed as concise `phonodist: ...` messages and exit with status `2` through `argparse`. This includes unsupported IPA segments, unknown profiles, and requests for the unimplemented stress-sensitive distance mode. A normal `diff` classification is not an error and exits successfully. Diagnostic text formatting is not a stable machine-readable interface; use `--json` for structured output.

## Version

```bash
phonodist --version
```

This prints the installed package version.
