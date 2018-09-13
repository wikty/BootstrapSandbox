# Motivation

This project was born, when i working with [bootstrap](http://getbootstrap.com) framework.  Assume that you need add a new bootstrap component into your project, before that usual you should modify the component suitable for your project sytle, if you directly do this in your project, may mess up other parts. You shoud have a clean workspace to debug the new component, and then merge it into your project. Yeah, this project's goal is providing a clean workspace for that situation.

# Usage

1. First, you should configure your workspace path, modify the `WORKING_DIR` variable in the file `config.py` to your workspace directory.

2. Generate bootstrap testing file

        python testbox.py [file...]

Note: The `file` is your html sinppet file.

# Syntax

How to write your html snippet file? The content in the file is like this:

        {% extend "some_parent.html" %}
        {% block blockname %}{% endblock %}
        <div>arbitrarily html code</div>

* **block**, to identify content block

* **extend**, current file inherit from parent file, means that current file can add new block or override parent file's block

*NOTE*: If you want more usage details, please have a look into [examples](examples).