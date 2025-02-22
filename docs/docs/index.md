# Welcome to ResultAPI

**ResultAPI** is a project that aims to enable programmers to start implementing an API using **FastAPI** **quickly** and **easily**.

## Why

On every new **FastAPI** project, you need to define a *logger*, consume environment variables from an *.env* file, maybe you'll consume 3rd services so you'll need an *http api client* and the list goes on.

**ResultAPI** tries to help you with these repetitive tasks so you can start writing your API endpoints and focus on your business logic from moment zero.

## How

**ResultAPI** already provides you with a directory structure that it's suggested to be followed, but it's up to you how do you want to structure your code.

**ResultAPI** comes with *batteries included*. It provides ***services***, which are simple Python modules that provide reusable generic functionalities that are generally necessary when developing an API. See *Services* tab for more information. Also, If you want to contribute to the project, new services are very welcome!

**ResultAPI** takes care of everything related to the Python interpreter you want to use in your project. You only have to specify which version of Python you want to use (and this is optional! If you don't choose a Python version to run the project with, one will be automatically selected). You no longer have to struggle with *virtualenvs*, installing the Python interpreter, etc. **ResultAPI** does it for you :)

**ResultAPI** automatically generates files for Docker and Docker Compose, so you can run the API within a Docker container. Additionally, it comes configured with *hot-reloading*, so any changes you make to your source code are automatically reloaded within the container.

**ResultAPI** makes it very easy to manage dependencies or third-party libraries in your project. Providing this functionality is thanks to the [Rye](http://rye-up.com) project, which **ResultAPI** uses.