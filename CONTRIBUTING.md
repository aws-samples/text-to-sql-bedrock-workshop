= Contributing to Kubernetes the AWSome Way
Thank you for your interest in contributing to Kubernetes the AWSome Way! We work hard to provide a high quality and useful workshop for our customers, and we appreciate your interest in helping us and the rest of our community of users. We welcome bug reports, enhancements, and contributions.

__Jump To:__

* link:#bug-reports[Bug Reports]
* link:#enhancements[Enhancements]
* link:#contributions[Contributions]
* link:#getting-in-contact[Getting in Contact]

== Bug Reports
Bug reports are accepted through the link:https://github.com/aws-samples/aws-workshop-for-kubernetes/issues[Issues] page.

The following labels are used to track bug related issues: link:https://github.com/aws-samples/aws-workshop-for-kubernetes/labels/Bug[Bug].

=== Before Submitting a Bug Report
Before submitting a bug report, please do the following:

1. Do a search through the existing issues to make sure it has not already been reported. If there's an existing one, be sure to give a +1 reaction which will help us prioritize which issues to address first.

2. Provide as much information about your environment, software version, and relevant dependencies as possible. For example, let us know what version of kubernetes you are using, which launch type for the kubernetes cluster (e.g. EKS or kops), and the environment your code is running in. (e.g Cloud9).

If, after doing the above steps, you determine that you need to submit a bug report, refer to the next section.

=== Submitting a Bug Report
So that we are able to assist you as effectively as possible with the issue, please ensure that your bug report has the following:

* A short, descriptive title. Ideally, other community members should be able to get a good idea of the issue just from reading the title.
* A detailed description of the problem you're experiencing. This should include:
  * Expected behavior of the workshop and the actual behavior exhibited.
  * Any details of your application environment that may be relevant.
  * Commands and output used to reproduce the issue.
* link:https://guides.github.com/features/mastering-markdown/[Markdown] formatting as appropriate to make the report easier to read; for example use code blocks when pasting a code snippet and exception stacktraces.

=== Tracking your Bug Report
You will automatically be notified of any changes to a bug report. Either a maintainer or a community member may comment on the bug report requiring further input. We encourage all contributors to stay active on their bug reports reports. This helps the community to focus on issues with more influence and activity.

Any input to the workshop is always appreciated. Our maintainers cannot devote 100% of their time to this project, but will try to respond in a timely manner. We want to squash bugs as often as we can, but sometimes require comments from the submitter or community in order to proceed.

If a bug report has been inactive (waiting on comment from submitter or community) for 14 days, a maintainer may label the issue as stale.  Once a bug report has been inactive for more than 28 days, the issue will be administratively closed. Issues can be re-opened after being administratively closed by commenting on the issue requesting to re-open and providing the necessary comment.

== Enhancements
Like bug reports, enhancements are submitted through the link:https://github.com/aws-samples/aws-workshop-for-kubernetes/issues[Issues] page.

As with Bug Reports, please do a search of the open requests first before submitting a new one to avoid duplicates. If you find an existing one, give it a +1.

[NOTE]
If this is an enhancement you intend to implement, please be sure to submit the enhancement *before* working on any code changes. This will allow members on the workshop team to have a discussion with you to ensure that it's the right design and that it makes sense to include in the workshop.

Enhancements are labeled with link:https://github.com/aws-samples/aws-workshop-for-kubernetes/labels/Enhancement[Enhancement].

=== Submitting an Enhancement
Open an link:https://github.com/aws-samples/aws-workshop-for-kubernetes/issues[issue] with the following:

* A short, descriptive title. Ideally, other community members should be able to get a good idea of the enhancement just from reading the title.
* A detailed description of the the proposed enhancement. Include justification for why it should be added to the workshop, and possibly example code to illustrate how it should work.
* link:https://guides.github.com/features/mastering-markdown/[Markdown] formatting as appropriate to make the request easier to read.
* If you intend to implement this enhancement, indicate that you'd like to the issue to be assigned to you.

== Contributions
Contributions to the workshop are done through link:https://github.com/aws-samples/aws-workshop-for-kubernetes/pulls[Pull Requests]. Please keep the following in mind when considering a contribution:

* The workshop is released under the link:https://github.com/aws-samples/aws-workshop-for-kubernetes/blob/master/LICENSE[Apache 2.0 License]. Any code you submit will be released under this license. If you are contributing a large/substantial enhancement, you may be asked to sign a link:https://github.com/aws/aws-cla[Contributor License Agreement (CLA)].

* You should always start by checking the link:https://github.com/aws-samples/aws-workshop-for-kubernetes/issues[Issues] page to see if the work is already being done by another person. We require that pull requests reference an issue.

[NOTE]
If you're working on a bug fix, check to see if the bug has already been reported. If it has but no one is assigned to it, comment that you are assigning it to yourself before beginning work.  If you're confident the bug hasn't been reported yet, create a new link:#bug-reports[Bug Report] then comment that you are assigning it to yourself.

[NOTE]
If you are thinking about adding entirely new functionality, open an link:#enhancements[Enhancements] or link:https://gitter.im/aws-samples/aws-workshop-for-kubernetes[ping] the maintainers to ask for feedback first before beginning work; again this is to make sure that no one else is already working on it, and also that it makes sense to be included in the workshop.

=== Pull Request Readiness
Before submitting your pull request, refer to the pull request readiness checklist below:

* [ ] Includes tests to exercise the new behavior
* [ ] Code is documented, especially public and user-facing constructs
* [ ] Git commit message is detailed and includes context behind the change
* [ ] The issue number for the bug report or enhancement is referenced

[NOTE]
Some changes have additional requirements. Refer to the section below to see if your change will require additional work to be accepted.

=== Getting Your Pull Request Merged
All Pull Requests must be reviewed and approved by at least two other contributors or one maintainer before it can be merged in. Additionally, maintainers will strive to not merge their own pull requests unless 72 hours has passed, though extenuating circumstances may apply. The members only have limited bandwidth to review Pull Requests so it's not unusual for a Pull Request to go unreviewed for a few days, especially if it's a large or complex one. If, after a week, your Pull Request has not had any engagement from the workshop team, feel free to link:https://gitter.im/aws-samples/aws-workshop-for-kubernetes[ping] a member to ask for a review.

If your branch has more than one commit when it's approved, you may also be asked to link:https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History[squash] them into a single commit before it is merged in.

== Getting in Contact
Come chat with us on:
* link:https://gitter.im/aws-samples/aws-workshop-for-kubernetes[Gitter]!
* **#eks** channel in **Kubernetes** Slack workspace
* **#containers** and **#kubernetes** channels in **aws-developers** Slack workspace