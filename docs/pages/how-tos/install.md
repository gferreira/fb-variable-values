---
title     : Installing VariableValues
layout    : default
permalink : /how-tos/install/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="../../how-tos">How-Tos</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

VariableValues is packaged and distributed as a [RoboFont extension].
{: .lead}

* Table of Contents
{:toc}


Installing with Mechanic
------------------------

It is recommended to install VariableValues using [Mechanic], so it can automatically check for updates and install them.

1. Download the file `VariableValues.mechanic` from the [GitHub repository].
2. Go to the Mechanic extension’s settings.
3. Use the plus button to add the `.mechanic` file to the list of [Single Extension Items].

[GitHub repository]: http://github.com/gferreira/fb-variable-values
[RoboFont extension]: http://robofont.com/documentation/extensions/
[Mechanic]: http://github.com/robofont-mechanic/mechanic-2
[Single Extension Items]: http://robofont.com/documentation/how-tos/extensions/managing-extension-streams/#adding-single-extension-items


Installing manually
-------------------

The VariableValues extension can also be installed manually if you download the extension package.

Simply double-click the file `VariableValues.roboFontExt` to have it installed in RoboFont.

<div class="alert alert-warning" role="alert" markdown='1'>
<i class="bi bi-exclamation-circle me-1"></i> If you install the extension manually, you will not be notified about updates.
{: .card-text }
</div>


Installing from source
----------------------

VariableValues can be used directly from the source code if you download the repository.

This mode allows developers to make changes to the code while using and testing the tools in RoboFont.

1. Clone the repository using `git clone` (recommended\*) or download the source code.
2. In the RoboFont Preferences window, go to [Extensions > Start Up Scripts].
3. Add the file `VariableValues/code/Lib/start.py` to the list of start-up scripts.
4. Save the settings and restart RoboFont; VariableValues will now appear under the *Extensions* menu.

[Extensions > Start Up Scripts]: http://robofont.com/documentation/reference/workspace/preferences-window/extensions/#start-up-scripts

<div class="alert alert-primary" role="alert" markdown='1'>
\* If you clone the repository using Git, you can get updates more easily later with `git pull`.
{: .card-text }
</div>