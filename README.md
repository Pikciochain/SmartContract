# Pikcio - Smart Contracts

This project includes **Pikcio** tools to submit, parse, quote and execute 
Smart Contracts in **Pikcio** blockchain.

## Content

This project contains a package to handle Smart Contracts, along with CLI
endpoints and unit tests.

### Understanding the project modules

Each module and subpackage of this project revolves around one of the main 
steps of the Smart Contract journey.

* `parse` package contains tools to extract Smart Contract ABI and to
ensure that contract matches Pikcio requirements.
* `compile` encapsulates compilation tools and configuration used by Pickio to
generate contract bytecode.
* `quotations` contains the tools used to generate quotations from a
Smart Contract.
* `invoke` contains the tools used to execute a Smart Contract in a sandbox.
This module currently supports docker only.
* `abi` is not executable directly but let translate invocation details from 
and to bytecode.

## Getting Started

These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project is built upon **Python 3**.
There is no other prerequisite or third-party required.


### Installing

After cloning the repository on your machine, it is encouraged to create a
virtual environment using your preferred tool. If you have no preference, you
can have a look at `virtualenvwrapper`, easily installed with:

```bash
pip install virtualenvwrapper
```

Once your environment ready and activated, install the pyton depencies using:

```bash
pip install -r requirements.txt
```

Optionally, if you also want to debug, develop or test the project, use:

```bash
pip install -r dev-requirements.txt
```

### Running CLI
The package has several entrypoints, one per executable submodule. Example with 
the `compile` one:

```bash
python -m pikciosc.compile --help
```

You should get something like:
```bash
usage: compile.py [-h] [-o OUTPUT] file

Pikcio Smart Contract Compiling module.

positional arguments:
  file                  source code file to compile

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to the compiled script.
```

In any case, if you are unsure about how to run a submodule try:
```bash
python -m pikciosc.<module> --help
```

#### Parse
`parse` validates a smart contract and generates its interface. You need to 
provide the path to the file to parse along with optional output options.

To parse a contract:
```bash
python -m pikciosc.parse smart_contract.py --indent 4 -o interface.json
```

#### Compile
`compile` compiles python script into bytecode, using Pikcio configuration. 
You need to provide the path to the file to compile along with optional output 
options.

To compile a contract:
```bash
python -m pikciosc.compile smart_contract.py -o smart_contract.pyc
```

#### Quote
`quote` creates quotations on Smart Contract prior to their 
submission/execution.

Quote currently offers two services: `submit` an `invoke`, each related to a 
different quotation.

*NOTE: To successfully perform a quotation, you need to provide the environment
variables that drive the computation.*
- *PKC_SC_SUBMIT_CHAR_COST*: Required in `submit` service. Tells the price of a single character of code, once encode to base 64.
- *PKC_SC_EXEC_LINE_COST*: Required in `invoke` service. Tells the price of a single line of executed endpoint.

To get a quotation for a contract submission:
```bash
PKC_SC_SUBMIT_CHAR_COST=0.2 \
python -m pikciosc.quotations submit smart_contract.py
```

To get a quotation for a contract invocation:
```bash
PKC_SC_EXEC_LINE_COST=0.4 \
python -m pikciosc.quotations invoke smart_contract.pyc <endpoint>
```

#### Invoke
`invoke` module lets you execute a contract. This is the most complicated 
module. It uses docker to execute provided code in a sandbox.

To execute a contract, let's assume you have a directory `dist` which contains:
- `binaries`: a folder where you store compiled contracts
- `interfaces`: a folder where you keep ABIs (contracts JSON interfaces)
- `executions`: a folder where you keep previous executions of each contract.

```bash
python -m pikciosc.invoke.invoke dist/binaries dist/interfaces \
	smart_contract compute_rate -kw amount 0.3 \
	--last_exec_path dist/executions/smart_contract/last_exec.json \
	-i 4 -o dist/executions/smart_contract/new_exec.json
```

Alternatively, if you don't want to use *docker* for a test, you can use:
```bash
SANDBOX=None \
python -m pikciosc.invoke.invoke dist/binaries dist/interfaces \
	smart_contract compute_rate -kw amount 0.3 \
	-le dist/executions/smart_contract/last_exec.json \
	-i 4 -o dist/executions/smart_contract/new_exec.json
```
This will execute the script but without any sandbox.

## Running the tests

Tests are run using following command at the root of the project:

```bash
pytest
```

All tests are kept under the `tests` folder at the root of the project.

## Authors

- **Jorick Lartigau** - *Development Lead* - [Pikcio](https://pikciochain.com)
- **Thibault Drevon** - *Architecture and implementation* - [Yellowstones](http://www.yellowstones.io)
