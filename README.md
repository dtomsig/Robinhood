# Project Title

Robinhood Transaction Generator

## Description

This program generates an OFX and QIF file from a given Robinhood brokerage 
account. The OFX file is an OFX investment response  with a list of stock
information that were found in the brokerage account. The QIF file contains
all dividends, stock purchases, and associated capital gains occurring after
a specific entered date. The OFX file will still respond with securities that
were purchased and sold that the user no longer has a position in. The entered
date does not affect the OFX file. The OFX file will contain security 
information of all stocks that were purchased or sold.

The main purpose of this program is to be able to import transactions from a 
Robinhood brokerage account into GNUcash.

### Prerequisites

Python 3 is required to run the program. 


### Installing

To install simply download the files in the repo. 


## Authors

* **Diego Tomsig** - *Author* - [dtomsig](https://github.com/dtomsig)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

