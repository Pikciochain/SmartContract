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

## Getting Started

These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project is built upon **Python 3**.
There is no other prerequisite of third-party required.


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
The package can be run as a CLI:

```bash
python -m pikciosc --help
```

You should get something like:
```bash
usage: __main__.py [-h] [-f FILE] [-i INDENT] {parse,quote,compile}

Pikcio Smart Contract package.

positional arguments:
  {parse,quote,compile}
                        Name of service to use

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  source code file to submit
  -i INDENT, --indent INDENT
                        If positive, prettify the output json with tabs
```

Available services are:
1. `parse`: Validates a smart contract and generates its interface,
2. `quote`: Creates quotations on Smart Contract prior to their submission.
3. `compile`: Compiles python script into bytecode, using Pikcio configuration.

In addition, it is possible to execute a contract using the dedicated service 
`invoke`:

```bash
python pikciosc/invoke/invoke.py --help
```

You should get something like:
```bash
usage: invoke.py [-h] [--kwargs [KWARGS [KWARGS ...]]] [-i INDENT]
                 bin_folder interface_folder execution_folder endpoint
                 contract_name

Pikcio Smart Contract Invoker

positional arguments:
  bin_folder            folder where python binaries are stored.
  interface_folder      folder where contract interfaces are stored.
  execution_folder      folder where contract executions are stored.
  endpoint              endpoint to call
  contract_name         Name of contract to execute.

optional arguments:
  -h, --help            show this help message and exit
  --kwargs [KWARGS [KWARGS ...]], -kw [KWARGS [KWARGS ...]]
                        List of args names and values
  -i INDENT, --indent INDENT
                        If positive, prettify the output json with tabs

```


##### Examples
Let's assume there is a contract called *smart_contract.py* at the root.

To parse a contract:
```bash
python -m pikciosc parse --file smart_contract.py --indent 4
```

To get a quotation for a contract:
```bash
export PKC_QUOTE_CHAR_COST=0.2 && python -m pikciosc quote --file smart_contract.py --indent 4
```

To compile a contract:
```bash
python -m pikciosc compile --file smart_contract.py --indent 4
```

To execute a contract, assuming you have a directory `dist` which contains:
- `binaries`: a folder where you store compiled contracts
- `interfaces`: a folder where you keep ABIs (contracts JSON interfaces)
- `executions`: a folder where tracking of contracts executions is performed

```bash
export PYTHONPATH='.' && \
python pikciosc/invoke/invoke.py \
	dist/binaries dist/interfaces dist/executions \
	smart_contract compute_rate -kw amount 0.3
```

Alternatively, if *docker* is not installed on your machine, you can use:
```bash
export PYTHONPATH='.' && export SANDBOX=None && \
python pikciosc/invoke/invoke.py \
	dist/binaries dist/interfaces dist/executions \
	smart_contract compute_rate -kw amount 0.3
```
This will execute the script but without any sandbox.

#### CLI output

CLI output is a JSON object representing the result of executing a service.
For example:
```bash
export PKC_QUOTE_CHAR_COST=0.2 && python -m pikciosc quote --file <example_file> --indent 4
```
Will generate:
```
{
    "code_len": 280,
    "char_cost": 0.2,
    "total_price": 56.0
}
```

## Running the tests

Tests are run using following command at the root of the project:

```bash
pytest
```

All tests are kept under the `tests` folder at the root of the project.

## Authors

- **Jorick Lartigau** - *Development Lead* - [Pikcio](https://pikciochain.com)
- **Thibault Drevon** - *Architecture and implementation* - [Yellowstones](http://www.yellowstones.io)
