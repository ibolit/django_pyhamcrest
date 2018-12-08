# apyshka
Pronounced [ə'pɪʃkɑ:]

Share and enjoy

The idea behind this is to write a micro-framework for writing API wrappers.
You should be able to write declarative methods for your API calls, with the
minimum information required, and then you should be able to call the actual
API endpoints without too much hassle.

Here's what the result should look like:

You declare a method like this:
```python
class ExampleApi(MyApi):
    root = "/api/"  # or "api"

    @get("/examples/{example}/")
    def get_example(self, example) -> {}:
        pass
```

And then you or your clients should be able to call
```python
API = ExampleApi("https://example.com/")
fifth_example = API.get_example(5)
# Will be transformed to a call to https://example.com/api/examples/5/
sixth_example = API.get_example(example=6)
seventh_example = API.get_example(params={"example": 7}, q={"abridged": True}
# the latter should be transformed to a call to
# https://example.com/api/examples/7/?abridged=True
```
You can alxo leave out the name of the only parameter passed to the api call:
```python
fifth = API.get_example(5)
```
