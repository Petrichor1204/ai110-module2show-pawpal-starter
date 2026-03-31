## 1. System Design
Actions user should be able to perform:
- Add, edit, update their pet details
- Add tasks and update them as completed or not
- Create daily schedule

**a. Initial design**

- Briefly describe your initial UML design.
  My initial UML had four classes: Pet, Task, Owner, and Scheduler. Pet stored info about the pet, Task had details like title and priority, Owner managed pets, and Scheduler made the schedule.
- What classes did you include, and what responsibilities did you assign to each?
  Pet: hold pet details and tasks. Task: represent a care activity. Owner: own pets and set time window. Scheduler: sort tasks and create plan.

**b. Design changes**

- Did your design change during implementation?
  Yes, it changed a bit.
- If yes, describe at least one change and why you made it.
  I changed the Scheduler to not hold its own list of tasks. Instead, it gets tasks from the Owner. This made sense because the Owner already manages pets and their tasks, so it kept things organized.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  It considers the owner's available time window, task priority, and task duration. It also looks at preferred time but doesn't force it.
- How did you decide which constraints mattered most?
  I thought priority was most important because high-priority tasks like feeding should come first. Time window is key to fit everything in.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduler makes is only checking for exact time matches in conflict detection instead of detecting overlapping durations. For example, if one task starts at 08:00 and lasts 30 minutes, and another starts at 08:15, the current system would not flag this as a conflict even though they overlap. This tradeoff is reasonable because the scheduling algorithm places tasks sequentially without allowing overlaps, so the primary conflicts occur when tasks are explicitly set to the same start time, keeping the logic simple and focused on user-specified times rather than complex duration calculations.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used VS Code Copilot for writing code, like suggesting method names and loops. I also asked questions in chat for ideas on how to structure classes.
- What kinds of prompts or questions were most helpful?
  Prompts like "how to implement this method" or "fix this error" were helpful. Also, asking for UML updates.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  Copilot suggested a way to sort tasks that was too complicated, so I simplified it to just priority and duration.
- How did you evaluate or verify what the AI suggested?
  I thought about if it fit my design and tested it with the demo script to see if it worked.

**c. AI Strategy with VS Code Copilot**

- Which Copilot features were most effective for building your scheduler?
  The inline suggestions were really helpful for writing code quickly, like when I was adding methods to the classes. It saved me time on typing out the basic structure.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
  Copilot suggested making the Scheduler class hold a list of tasks directly, but I changed it to get tasks from the Owner instead. This kept things cleaner because the Owner manages all pets and their tasks, so the Scheduler doesn't need its own copy.

- How did using separate chat sessions for different phases help you stay organized?
  It helped a lot because each phase had its own chat, so I could focus on one thing at a time, like first designing the classes, then implementing logic, then connecting to the UI. It stopped things from getting mixed up.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
  I learned that I'm the one who decides the big picture, like how the classes should work together. The AI is great for details, but I have to guide it and make sure the design makes sense for the project.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  I tested task completion and adding tasks to pets.
- Why were these tests important?
  They make sure basic things work, like marking tasks done and linking tasks to pets.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  Pretty confident, it works for the main cases.
- What edge cases would you test next if you had more time?
  Things like no tasks, or tasks longer than the day, or multiple pets with overlapping tasks.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  I'm happy with how the scheduler sorts tasks and shows conflicts.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  I'd add better handling for preferred times and maybe recurring tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  I learned that starting with a clear design helps, and AI can help but I need to check its ideas.
