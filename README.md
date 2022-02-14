# Spike

*Python web framework, based on Reactor framework*

--------------------------

## Overview

Spike is a Python web framework. It provides tools for building various web applications. A quick underline of features this framework is capable of:
- Versatile declarative API for handling web requests.
- Template rendering.
- Serving static resources.
- Database interaction API that does not depend on a specific database.
- Authentication of users.

And many more...

Concept of **applications** makes Spike framework modular and declarative. A **Spike application** is a class that defines some resources and information that the framework uses to configure itself. Inherit from `spike.application.Application` to define a new application. The subclass of `Application` itself represents a new application that can be plugged into Spike. Define special fields and methods directly on the class (not on its instance). Theses fields and methods will configure aspects of Spike corresponding to their name.

To start the framework and make use of the applications use `spike.reactor.Spike`. This is the main singleton of all the Spike. You will need to create it yourself and store it somewhere where anything can access it. Pass all the applications you want to use to the constructor. The `Spike` class inherits from reactor and implements it.

## Development Progress

The Spike framework is not yet finished. All the information in this file is not applicable to the framework in its current state. The information describes what the framework will be like in the future when it will be done.


