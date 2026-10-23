Module 2, Checkpoint 1 — AI Content Studio Results

Course: Python for AI
Business: Sweet Crumbs
Location: Lahore, Pakistan

1. AI Quality Tests

Test 1: Opening Hours

Input:
"what are your opening hours?"

Actual AI response:
“Our opening hours are from 9 am to 10 pm.”

Judgement: PASS

Reason: The AI provided the correct opening hours from the business facts.

Test 2: Product Price

Input:
"/price CUPCAKE"

Actual response:
“Cupcake costs 250 PKR.”

Judgement: PASS

Reason: The program correctly found the cupcake price from the price dictionary. No AI call was needed.

Test 3: Unknown Product

Input:
"/price pizza"

Actual response:
“Pizza is not on our menu.”

Judgement: PASS

Reason: The program correctly identified that pizza was not listed in the business price dictionary.

---

2. Chat Memory Test

Input 1:
"my name is ali"

Actual AI response:
“Hello Ali! How can I help you today?”

Judgement: PASS

Reason: The AI responded to the user's name and maintained the conversation context.

Input 2:
"/reset"

Actual response:
“Chat memory has been reset.”

Judgement: PASS

Reason: The reset command cleared the previous conversation while preserving the system message.

Input 3:
"what is my name?"

Actual AI response:
“I do not know your name.”

Judgement: PASS

Reason: After resetting the conversation, the AI no longer remembered the previously provided name.

---

3. Social Media Post Quality Tests

Test 1: Fun Tone

Command: "/post fun"

Quality judgement: The post used friendly language, emojis, and an engaging style suitable for a bakery's social media.

Issue found: The AI incorrectly mentioned mango tarts as available, although the business data lists their price as 0 and says they are coming soon.

Judgement: PARTIAL PASS

Test 2: Premium Tone

Command: "/post premium"

Quality judgement: The post used elegant language and presented the bakery's products in a polished style.

Issue found: The AI included mango tart without clearly stating that it is coming soon.

Judgement: PARTIAL PASS

Test 3: Urgent Tone

Command: "/post urgent"

Quality judgement: The post used action-focused language and encouraged customers to order.

Issue found: The AI incorrectly described mango tart as available.

Judgement: PARTIAL PASS

Default Tone Test

Command: "/post pirate"

Actual behaviour: The program used its default friendly tone instead of crashing.

Judgement: PASS for default-tone handling.

Issue found: The generated post again incorrectly mentioned mango tart as available.

---

4. Best Post and Final Judgement

Selected tone: Premium

Reason: The premium tone presents Sweet Crumbs in an elegant and professional way. It is suitable for a bakery that wants to promote its products attractively.

Required improvement: The system prompt should explicitly tell the AI that products with a price of 0 are coming soon and must never be advertised as currently available. Product availability should also be checked against the business facts before publishing a post.

---

5. Batch Menu Writer Test

Command:
"uv run python code/lesson_2_4_batch_writer.py"

Actual results:

- Chocolate Cake: 1,500 PKR
- Cupcake: 250 PKR
- Brownie: 300 PKR
- Donut: 200 PKR
- Cookie: 100 PKR
- Old stock was skipped because it had no price.

Final report: 5 descriptions generated, 235 tokens, 5.7 seconds.

Judgement: PASS

Reason: The program generated descriptions for five priced products and skipped the zero-priced item.

---

6. Overall Project Results

Feature| Result
Batch product descriptions| PASS
Zero-price item skipped with "continue"| PASS
Opening-hours question| PASS
Exact product price lookup| PASS
Unknown product handling| PASS
Conversation memory| PASS
"/reset" command| PASS
Fun social media post| PARTIAL PASS
Premium social media post| PARTIAL PASS
Urgent social media post| PARTIAL PASS
Default tone for unknown tone| PASS
Mango tart availability accuracy| NEEDS IMPROVEMENT

7. Final Reflection

The AI Content Studio successfully generated product descriptions, answered business questions, returned exact prices, maintained conversation memory, and reset the conversation when requested.

The tests also revealed an important limitation: the AI sometimes advertised mango tart as available even though the business data marked it as coming soon. This shows why AI-generated content must be checked against reliable business facts before it is shared with customers.

The next improvement will be to strengthen the system prompt and add a reliable availability check so that the AI does not advertise coming-soon products as available.

Conclusion: The main features work, and the project meets many of its requirements. Improving product-availability accuracy is the most important remaining quality improvement.