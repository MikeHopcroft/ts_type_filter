# ts_type_filter

This is an experimental library to assist in preparing Typescript type definitions for use in Large Language Model (LLM) prompts.
We've seen from projects like [TypeChat](https://github.com/microsoft/TypeChat) that TypeScript type definitions are a good way to communicate the desired output schema in an LLM prompt.

In some scenarios, such as restaurant menus, the Typescript type definition may be long, and it may be desireable to work with a subset of the type definition that specifies only the types needed for the current term.

For instance, if the customer is ordering a drink it is not necessary to include the types related to sandwiches.

As an example, suppose we have a menu for a restaurant with a menu offering two sandwiches with some toppings, two sodas, and two juices:

~~~typescript
type Items = Sandwiches | Drinks;

type Sandwiches = {
  name: "Ham Sandwich" | "Turkey Sandwich";
  options: SandwichOptions[];
};

type SandwichOptions = {
  name: "lettuce" | "tomato" | "onion";
  amount: "no" | "regular" | "extra";
};

type Drinks = Soda | Juice;
type Soda = { name: "Coke" | "Pepsi" };
type Juice = { name: "Apple" | "Orange" };
~~~

[Tiktoken](https://tiktokenizer.vercel.app/) shows that this type definition uses 106 tokens.

If the user says something like, "I'll have a ham sandwich with no tomatoes", the menu could be filtered to something like

~~~typescript
type Items = Sandwiches;

type Sandwiches = {
  name: "Ham Sandwich" | "Turkey Sandwich";
  options: SandwichOptions[];
};

type SandwichOptions = { name: "tomato"; amount: "no" };
~~~

This filtered menu uses only 47 tokens. The potential savings due to filtering is much more signifant for a large menu.


`ts_type_filter` provides an algorithm to prune TypeScript type definitions based an a set of keywords. The algorithm first parses the TypeScript into an abstract syntax tree. It then builds an inverted index of the terms in the string type literals, and this index is used to prune the type definitions, based on the current contents of the shopping cart and the customer's request. You can learn more about the inverted index [here](./documentation/inverted-index.md).

## Installation

### From PyPI (when available)
```bash
pip install ts_type_filter
```

### From GitHub (recommended for now)
```bash
pip install git+https://github.com/MikeHopcroft/ts_type_filter.git
```

### Using Poetry
```bash
poetry add git+https://github.com/MikeHopcroft/ts_type_filter.git
```

### Development Installation
```bash
git clone https://github.com/MikeHopcroft/ts_type_filter.git
cd ts_type_filter
poetry install
```

## Sample Applications

`ts_type_filter` includes four samples:
* [filtering_api.ipynb](./samples/menu/simple.ipynb) - notebook demonstrates `ts_type_filter` api usage.
* [pipeline.ipynb](./samples/menu/pipeline.ipynb) - notebook demonstrates a
[Gotaglio](https://github.com/MikeHopcroft/gotaglio) pipeline that uses
`ts-type-filter` to optimize LLM prompts for a ficticious restaurant ordering bot.
* [gotag cli](./samples/menu/gotag.md) - shell script that runs the pipeline.
* [query cli](./samples/inverted_index/query.md) - shell script demonstrates inverted index of Shakespear sonnets.

You need a properly configured development to run the samples.

## Development Environments

The easiest way to try out the samples is in a [GitHub Codespace](./documentation/codespaces.md). This approach spins up a fully configured dev container connected to an instance of [Visual Studio Code](https://code.visualstudio.com/), running in your browser.

You can also clone the repo on your local workstation, install some tools and PyPi packages and then run the samples locally.

Here are instructions for both approaches:
* [GitHub Codespace](./documentation/codespaces.md)
* [Cloning to Local Repo](./documentation/clone.md)

## Documentation

* [Inverted Index](./documentation/inverted-index.md)
* [Type Pruning Algorithm](./documentation/algorithm.md)

## Using ts_type_filter

~~~
poetry add git+https://github.com/MikeHopcroft/ts_type_filter
~~~

TODO:
  * poetry or pip install
  * import
  * use api to build type
  * filter to generate source text

## Building ts_type_filter

1. Verify you have python version >=3.12. Note that 3.13 may not be supported yet.
1. `pip install poetry` outside of any virtual environment.
2. `git clone https://github.com/MikeHopcroft/ts_type_filter.git`
3. `cd ts_type_filter`
4. `python -m venv .venv`
5. `.venv\Scripts\activate`
6. `poetry install --no-root`

~~~bash
% gotag run menu samples\menu\cases2.json infer.model.name=perfect prepare.compress=True

% gotag format latest > junk\out3.md
~~~

~~~
    7  . .venv/bin/activate
   11  ./gotag run menu samples/menu/cases2.json infer.model.name=perfect

    1  gotag
    2  ./gotag
    3  poetry install
    4  tail .bashrc
    5  tail ~/.bashrc
    6  ls .venv
    7  . .venv/bin/activate
    8  ./gotag
    9  ./gotag run menu 
   10  ./gotag run menu samples/menu/cases2.json
   11  ./gotag run menu samples/menu/cases2.json infer.model.name=perfect
   12  history
~~~

