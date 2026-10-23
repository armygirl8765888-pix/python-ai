Module 2 Checkpoint 1 — AI Content Studio Design

1. Business Facts

Key| Value
name| Sweet Crumbs
business_type| Bakery
city| Lahore
hours| 9 am to 10 pm
delivery| 200 PKR; free on orders of 3,000 PKR or more
customers| Families, students and cake lovers
prices| Chocolate Cake: 1500 PKR, Cupcake: 250 PKR, Brownie: 300 PKR, Mango Tart: 0 PKR (coming soon)

2. Social Media Tones

Tone| Description sent to the AI
fun| Playful, energetic, friendly and uses short sentences
premium| Elegant and calm, focused on quality and freshness
urgent| Exciting and action-focused, encourages customers to order

3. Which Model for Which Job?

Job| Model and temperature| Why
Menu descriptions| Creative model, 0.8| Marketing descriptions should sound interesting and varied
Social media posts| Creative model, 0.8| Different tones need creative writing
Customer questions| Precise model, 0.2| Answers should follow the real business facts
Price lookup| No AI model| The dictionary gives the exact price without using tokens

4. Feature Tests

You type| Expected result| Pass?
/menu| Mango Tart skipped; numbered menu and comma-formatted prices| Pending
/post fun| Fun post streams in chunks| Pending
/post premium| Premium post streams in chunks| Pending
/post urgent| Urgent post streams in chunks| Pending
/post pirate| Default tone used without a KeyError| Pending
/price CUPCAKE| Correct price: 250 PKR| Pending
/price mango tart| Coming soon| Pending
/price pizza| Not on our menu| Pending
My name is Ali, then What is my name?| Remembers Ali| Pending
/reset, then What is my name?| Does not know the name from the cleared conversation| Pending
Press Enter without text| Asks for input again| Pending
BYE| Goodbye and session report| Pending

Update each Pending value to Pass or Fail after running the actual test. Do not mark an untested feature as Pass.