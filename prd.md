# Project Requirements: Pynvoice

## 1. Introduction

This document outlines the functional and non-functional requirements for Pynvoice, a command-line application designed to simplify the generation of invoices. The application will allow users to manage senders, clients, and invoice items, culminating in the creation of a professional PDF invoice.

## 2. Goals

The primary goal of Pynvoice is to provide a straightforward and efficient way for users to create customized invoices in PDF format, reducing manual effort and potential errors.

## 3. User Roles

- **Invoice Creator:** A user who needs to generate invoices for various clients and services.

## 4. Functional Requirements

### FR1: Sender Management

- **FR1.1: Create New Sender:** The system shall prompt the user to input details for a new sender, including (but not limited to) name, address, email, and phone number.
- **FR1.2: Choose Existing Sender:** The system shall display a list of previously created senders and allow the user to select one for the current invoice.
- **FR1.3: Sender Data Storage:** Sender information shall be persistently stored (e.g., in a database table).

### FR2: Client Management

- **FR2.1: Create New Client:** The system shall prompt the user to input details for a new client. The client **name** shall be a mandatory field. The **address** and **email address** shall be optional fields.
- **FR2.2: Choose Existing Client:** The system shall display a list of previously created clients and allow the user to select one for the current invoice.
- **FR2.3: Client Data Storage:** Client information shall be persistently stored (e.g., in a database table).

### FR3: Invoice Generation

- **FR3.1: PDF Output:** The system shall generate an invoice in PDF format.
- **FR3.2: Sender and Client Inclusion:** The generated PDF shall include the selected sender's details and the selected client's details.
- **FR3.3: Invoice Data Persistence:** Invoice details, including references to the selected sender and client, shall be persistently stored in the database. This will allow for future lookup or regeneration of invoices.

### FR4: Item Management

- **FR4.1: Add New Item:** The system shall prompt the user to input details for an invoice item, including:
  - Item Name (e.g., "Consulting Hours", "Product X")
  - Amount (quantity, e.g., 10, 5.5)
  - Cost per unit (price, e.g., $50.00, $12.99)
- **FR4.2: Multiple Item Entry:** The system shall allow the user to add multiple items to a single invoice until explicitly stopped.
- **FR4.3: Item Listing on PDF:** All added items shall be listed clearly on the generated PDF, including their name, amount, cost per unit, and the calculated line total for each item.
- **FR4.4: Item Data Persistence:** Invoice items shall be persistently stored in the database, linked to their respective invoice.

### FR5: Invoice Totals

- **FR5.1: Calculate Subtotal:** The system shall calculate the subtotal of all items (sum of line totals) before any taxes or discounts.
- **FR5.2: Calculate Grand Total:** The system shall calculate the grand total of the invoice, which is the sum of all item line totals. This grand total shall be prominently displayed on the PDF.

### FR6: Footer Message Management

- **FR6.1: Create New Footer Message:** The system shall prompt the user to input a custom message to be displayed in the invoice footer (e.g., payment terms, thank you note).
- **FR6.2: Choose Existing Footer Message:** The system shall display a list of previously saved footer messages and allow the user to select one.
- **FR6.3: Footer Message Data Storage:** Footer messages shall be persistently stored (e.g., in a database table).
- **FR6.4: Footer Message Inclusion:** The selected footer message shall be included in the footer section of the generated PDF.

## 5. Non-Functional Requirements

### NFR1: Performance

- **NFR1.1: Invoice Generation Speed:** PDF invoice generation should be completed within a reasonable timeframe (e.g., a few seconds for a standard invoice).

### NFR2: Usability

- **NFR2.1: Intuitive CLI:** The command-line interface should be easy to navigate and understand for users with basic command-line proficiency.
- **NFR2.2: Clear Prompts:** All user prompts should be clear, concise, and guide the user through the invoice creation process.
- **NFR2.3: Error Handling:** The system should provide clear and helpful error messages when invalid input is provided or an operation fails.

### NFR3: Maintainability

- **NFR3.1: Code Structure:** The codebase should be modular, well-commented, and follow good programming practices to facilitate future enhancements and bug fixes.

### NFR4: Security (Basic)

- **NFR4.1: Data Integrity:** The system should ensure the integrity of stored sender, client, and footer message data.

## 6. Technical Considerations (High-Level)

- **Programming Language:** Python
- **PDF Generation Library:** A suitable Python library for PDF creation (e.g., ReportLab, FPDF2).
- **Data Persistence:** A lightweight database (e.g., SQLite) for senders, clients, footer messages, invoices, and invoice items.
- **User Interface:** Command-Line Interface (CLI).

## 7. Future Enhancements (Out of Scope for Initial Release)

- Invoice numbering/tracking (could be part of the initial `Invoice` table, but auto-generation/management might be a future enhancement)
- Tax calculation and application
- Discount application
- Ability to edit existing senders, clients, or items
- Exporting invoice data to other formats (e.g., CSV)
- Web-based user interface
- Recurring invoices
