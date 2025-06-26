# Contributing

N.B. -- UNDER CONSTRUCTION -- The following is desirable but not yet implemented. Subject to change -- incomplete -- some of it may be wrong.

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

🚀 Future Evolution of this doc...

* Formalize a branch naming convention (feature/, bugfix/, etc.)
* Add GitHub issue and PR templates
* Use GitHub Projects or milestones for roadmap planning
* Mention GitHub Discussions or where casual Q&A should happen
* Clarify review/approval process for PRs (if you’ll use one)
* If you decide to keep a changelog manually, consider following Keep a Changelog, HISTORY.md
* You can use tools like `scriv` to manage release notes as well.
* Explain clearly about using Poetry and how to use tags.
* Explain where docs go and provide format guidance.
* Clarify what is meant by "local setup", "deploy" and so on. Mention what environments have been used, not used yet.

---

ROUGH DRAFT...

## Code of Conduct

* (Put appropriate notes here)

---

## Types of Contributions

You can contribute in many ways:

### Report Bugs

Report bugs at <https://github.com/genuinemerit/mint/issues>

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

The mint-wiki can always use more documentation, either for developers or users.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/genuinemerit/saskan-calendar/issues>

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome

## Get Started

Ready to contribute? Here's how to set up `saskan-calendar` for local development.

First, read the design/00_develop and design/20_testing docs!

🍴 1. Fork the `saskan-calendar` repo on GitHub.

🍽️ 2. Clone your fork locally::

    `git clone git@github.com:your_name/mint.git`

⋔ 3. Set up your fork for local development

    ```bash
    cd saskan-calendar/
    # ...
    # this needs better explanation
    ```

🕊️ 4. Create a branch for local development

    `git checkout -b name-of-your-bugfix-or-feature`

   Now you can make your changes locally.

❄︎ 5. When you're done making changes, run code through linters/formatters like `black` or `flake8` and `isort`.

📌 6. Commit your changes and push your branch to GitHub::

(Explain here about creating feature branches...)

    ```bash
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

🚨 7. Submit a pull request through the GitHub website.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.12. Check..  
   talk about GitHub actions here..  
   <https://github.com/genuinemerit/saskan-calendar/pull_requests>
   and make sure that the tests pass for all supported Python versions.

### Tips

To run a subset of tests: `python -m pytest tests/unit/my_tests.py`

### Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.md).

Then run:

    ```bash
    # It won't be this, 'cause we'll be using Poetry...
    bumpversion patch # possible: major / minor / patch / dev
    git push
    git push --tags
    ```
