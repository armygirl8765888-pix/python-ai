Module 2 Final Project — Design

1. Business Data

Key| Example Value
name| Sweet Crumbs
type| Bakery
city| Lahore
hours| 9 AM to 10 PM
delivery| Available in selected areas
delivery_fee| 150 PKR
prices| chocolate cake: 1500, cupcake: 250, brownie: 300, donut: 200

2. Tools

Tool| What it does| Inputs| Approval?
get_price| Checks menu price| item| No
get_info| Checks business information| topic| No
order_status| Checks an order| order_id| No
place_order| Calculates and saves an order| item, quantity, customer| Yes

3. Guardrails

Risk| Guardrail
Agent runs forever| MAX_STEPS = 5
AI invents prices| Read prices from business.json
Wrong order total| Calculate total using Python
Order saved without permission| Ask owner for approval
Unknown tool requested| Handle unknown tool names
Damaged JSON file| Catch JSON errors and start safely
AI server is offline| Show a friendly message and log the error
Fake customer name| Check the original WhatsApp message