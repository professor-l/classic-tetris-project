# Testing

## Why test?
Testing becomes an important part of any project as it grows larger. Arguably the most important reason for writing tests is to avoid *regression*. Regression testing involves running the existing test suite after making changes in order to make sure that your changes don't break any existing areas of the code base. If any tests fail, then either there's a bug in your changes that you should fix, or the functionality of the code being tested has intentionally changed and those tests should be updated to reflect that change. Of course, regression testing will only prevent you from breaking areas of the code base that are well-tested.

Another reason for testing is to make sure the code that you're writing works as expected. The test-driven development (TDD) methodology recommends that you treat tests as a spec that describes the code you're writing; that is, you should write a test, run it and watch it fail, write the minimum amount of code needed to make the test pass, and repeat. We provide no recommendation on whether you should write your tests before, during, or after writing your code, but I would recommend trying out TDD at some point as an exercise to gain an understanding of how writing tests can inform the code that you're writing. It's easy to get caught in a trap where you write tests afterward and your tests only describe the code that you wrote instead of describing the intended functionality.

In any case, writing tests along with your code can surface corner cases or other scenarios that you may not have considered when writing the code. It can also be a good tool to quickly iterate on your code to make it work as intended instead of having to continually go through the sluggish process of testing it manually.


## When to test
Ideally, always. The better test coverage an area of code has, the less likely it is to break. As of writing, most of the code base is untested, but over time we should aim to backfill these tests as we touch different components and as it makes sense to. However, testing can sometimes be a cumbersome process that slows down development. Tests are most important around brittle areas of the code base that rely on a lot of other code and that can easily break. As an example, we should write integration tests for bot commands since much of the code base's functionality is exposed to users through commands. We should also plan to write unit tests around the most critical areas of code.

Going forward, most new code should be tested -- especially code that is easily broken or important to other parts of the code base. When testing a method or feature, it's good practice to make sure you're thinking about and writing tests for the typical use cases as well as any corner cases that may arise. You should aim for your tests to exercise all possible code paths through the method or feature that you're testing; this can be measured using tools such as [coverage.py](https://coverage.readthedocs.io/en/coverage-5.1/).


## How to test
We mostly use Django's testing framework, with a few modifications (heavily inspired by [RSpec](https://rspec.info/), if you're familiar). To start with, I recommend reading through some of Django's [documentation on testing](https://docs.djangoproject.com/en/2.2/topics/testing/).

Test are organized inside of test classes that inherit from `TestCase`. Each test class can have multiple test methods, which are each run individually. Tests use their own test database, which is reset between each test.

All tests should be contained in the `tests/` directory, whose structure mirrors that of `classic_tetris_project/`. Each file being tested should have an associated test file whose name is prefixed with `test_`. Each class being tested should be tested in a test class that inherits from `TestCase`. All test method names should begin with `test_`. For example, if `classic_tetris_project/models/users.py` contained a class named `User`, then we would write tests for this class in `tests/models/test_users.py`, which would contain:
```python
class UserTestCase(TestCase):
    def test_that_it_does_something(self):
        ...
```

### Writing tests
Your most important resource when writing tests is our [`tests.helper`](https://github.com/professor-l/classic-tetris-project/blob/master/tests/helper/__init__.py) module. This imports a bunch of useful testing tools for you so that you don't have to import a million things at the top of each of your test files. Every test file should begin with:
```python
from tests.helper import *
```

Some of the tools included are:
- [expects](https://expects.readthedocs.io/en/stable/) is an assertion library that we use in place of Django's assertions. In my opinion it results in cleaner and more expressive assertions, and it's more extensible and can build more complex conditions than Django's assertions. All expects matchers are included in `tests.helper`.
- [factory_boy](https://factoryboy.readthedocs.io/en/latest/) is a substitute for Django's fixtures that makes building model instances during testing easier. Factories are defined in the `tests.helpers.factories` module. Each factory class can be called to create an instance of its associated model:
  ```python
  # creates a ScorePB with some default values and an associated User
  score_pb = ScorePBFactory(starting_level=18)
  ```
  All factories are included in `tests.helper`.
- [mock](https://docs.python.org/3/library/unittest.mock.html) allows you to mock out parts of the system during testing in order to isolate the functionality that you want to test. For example, you might mock out a discord.py API call to return a specific value, or assert that a method was called with specific arguments. I most frequently find myself using the `@patch` or `@patch.object` decorators around test methods.
- The `@lazy` decorator (defined in [`memo.py`](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/util/memo.py)) composes the `@property` and `@memoize` decorators. I find this particularly useful to define *lazy resources* in test cases where multiple of the test methods share a variable (e.g. a `User` instance). For example, I might define a lazy `user` resource on a test case:
  ```python
  @lazy
  def user(self):
      return UserFactory()
  ```
  Then every test method in that test case has access to `self.user` without having to explicitly write code to create a `User` each time; a `User` is created the first time that `self.user` is invoked and remembered in subsequent invocations. This can be better than creating a `User` in the `setUp` method since `setUp` is common to all test methods in a test case. A particular resource might be necessary for only a subset of test methods, so we avoid the waste of creating a bunch of extra resources before each test method by creating them lazily as needed.

  Note that it will sometimes make sense to call `self.user` in a test method without using its return value in order to insert the record into the database.
- When writing unit tests, I recommend using the `describe` context manager to help organize tests for different methods, e.g.
  ```python
  class UserTestCase(TestCase):
      with describe("#add_pb"):
          def test_add_pb_creates_score_pb(self):
              ...

      with describe("#get_pb"):
          def test_get_pb_returns_greatest_score(self):
              ...
  ```
  `describe` has no actual effect, but it can group related test methods together inside an indented block, which helps make the test suite more readable. I recommend naming instance methods as `#instance_method_name` and static and class methods as `.static_method_name`, though you may use `describe` to create other groupings (i.e. you could separate out testing the Discord and Twitch versions of commands).
- When writing tests for bot commands, you should extend the `CommandTestCase` class. This stubs out logging and Twitch API calls, provides a bunch of lazy resources that are generally useful for testing commands, and defines the `expect_discord` and `expect_twitch` instance methods, which can be used to check that running a specific command string will result in the bot sending a message or sequence of messages.

I would recommend starting by looking at some of the tests in `tests/` to get a feel for how the existing test suite is written. Feel free to contact dexfore if you have any questions about writing tests.

### Running tests
We use [nose](https://nose.readthedocs.io/en/latest/) as the test runner, which gives more flexibility when discovering and running tests.

The full test suite can be run with:
```
python manage.py test
```
You can specify a module if you only want to run all tests in that module. For example, if I wanted to run all tests inside of `tests/models/test_users.py`, then I could run either of:
```
python manage.py test tests.models.test_users
python manage.py test tests/models/test_users.py
```
If I wanted to run tests inside of a specific test class or a specific test method, I could run something like one of:
```
python manage.py test tests.models.test_users:UserTestCase.test_add_pb_creates_score_pb
python manage.py test tests/models/test_users.py:UserTestCase.test_add_pb_creates_score_pb
```

You can additionally run the test suite with [coverage.py](https://coverage.readthedocs.io/), a tool that measures the areas of your code base that are exercised when the test suite is run. See more information about how to run that with django [here](https://docs.djangoproject.com/en/2.2/topics/testing/advanced/#integration-with-coverage-py).

For more specific information on running tests, check out the testing docs for [nose](https://nose.readthedocs.io/en/latest/usage.html), [django-nose](https://django-nose.readthedocs.io/en/latest/usage.html), or [Django](https://docs.djangoproject.com/en/2.2/topics/testing/overview/).
