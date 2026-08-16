# Flask Inventory Management System

A REST API built with Flask for managing retail inventory, with integration to the OpenFoodFacts API to fetch real product data, plus a command-line interface (CLI) for interacting with it.

## Features

- Full CRUD operations for inventory items (Create, Read, Update, Delete)
- External API integration with OpenFoodFacts to fetch product details by name or barcode
- CLI tool to add, view, update, delete, and search items
- Error handling for invalid input and API/connection failures
- Unit tests covering API endpoints and external API interactions (pytest + unittest.mock)

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/trizahn2002-source/flask-inventory-management-system.git
   cd flask-inventory-management-system