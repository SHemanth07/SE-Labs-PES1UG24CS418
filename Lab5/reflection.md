# Lab 5: Reflection

## 1. Which issues were the easiest to fix and which were the hardest?

The easiest were the Flake8 style issues: removing unused imports and
variables, splitting the semicolon line, adding blank lines and wrapping long
lines. They were mechanical and the tool told me the exact line. Pylint
naming and docstring warnings were also easy, just tedious because there were
so many.

The hardest were the problems that needed an understanding of the code. The
new-regime tax used one flat rate on the whole income instead of calculating
slab by slab, and fixing that meant rewriting the logic with a slab table and
checking the results by hand (12,75,000 should give 0 and 18,00,000 should
give 150800). Replacing ECB with AES-GCM was also harder than the other
security fixes because the key had to move out of the source code into an
environment variable and the program had to handle the key being missing.

## 2. Did the tools report any false positives, or miss any real problems?

Bandit flagged `CGIHandler` as High severity (B412, httpoxy). That check is
about importing the handler, and Python's `wsgiref` handler ignores the
`HTTP_PROXY` header, so the risk does not apply here. I documented the reason
in a comment and used `# nosec B412` instead of changing the code. Pylint's
"too many return statements" warning on the slab function was also more about
style than a bug.

More importantly, the tools missed real problems. None of them reported that
the tax figures were wrong. They did not catch `age > 80` instead of `>= 80`,
the PAN regex accepting extra characters (`re.match` without an end anchor),
the regime comparison returning the more expensive regime, the missing 80C
cap, or the rebate leaving cess charged. Bandit also did not flag the
hardcoded AES key. I only found these by running the program and checking
whether the output made sense.

## 3. How does static analysis contribute to code quality and maintainability?

The Pylint score went from 4.57/10 to 10.00/10, Flake8 went from 23 warnings
to 0, and Bandit went from 6 findings to none. The code is now consistent
(PEP 8 and snake_case), documented with docstrings, free of dead code, and
safer (stronger key size, authenticated encryption, safe XML parsing). Those
changes make the file easier to read and review, and they catch security
mistakes before the program is ever run. Running the tools in separate steps
also showed me which kind of problem each tool is good at: Bandit for
security, Flake8 for formatting, Pylint for design and quality.

## 4. How would you use static analysis in a real project, and what are its limits?

I would run all three tools automatically on every commit or pull request
(for example in a CI pipeline or a pre-commit hook), and fail the build on
High or Medium Bandit findings or a drop in the Pylint score. That catches
problems early, when they are cheap to fix.

The limit I saw in this lab is that static analysis cannot know what the
program is supposed to do. A clean report does not mean the code is correct,
because the wrong tax calculation passed all three tools. So static analysis
has to be combined with unit tests, code review and manual checking of the
output. Findings also need judgement: each warning has to be fixed, or
suppressed with a written reason, as with the `# nosec` comments.
