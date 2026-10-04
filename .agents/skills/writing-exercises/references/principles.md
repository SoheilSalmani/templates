# The research behind the rules

Load this when a call is genuinely unclear. `SKILL.md` holds the rules in operational form; this file says why they hold and where they stop holding.

Condensed from three literature reviews made for this skill in October 2026, on the cognitive science of practice, on computing education, and on established exercise collections. Almost none of the studies used the learner this skill writes for, an experienced developer learning a tool alone: most used school or university students. Where a rule extends a finding to that learner, it says so. Sources marked *abstract* were read only as an abstract.

## Contents

- The loop: attempt, check, then the solution
- Exercise or flashcard
- Real tasks
- Hints
- How much to guide
- How much goes in one exercise
- Order and revisits
- Which types pay off
- The shape of a set
- Wording
- Sizing
- Where the evidence is weak

## The loop: attempt, check, then the solution

- **Retrieval beats rereading**, even though rereading feels better at the time. Retrieval wins at two days and a week; rereading wins only at five minutes, and raises confidence while lowering recall (Roediger & Karpicke 2006, *abstract*). Dunlosky et al. (2013) rate practice testing and spacing the only two high-utility techniques of ten, and rereading low. **So**: every item is an outcome the learner produces, never a recipe to follow or a page to reread.
- **Generating beats reading**, by about 0.40 SD across 86 studies, more when the learner generates the whole answer (0.55) than part of it (0.32), and about zero for nonwords (Bertsch et al. 2007). **So**: the learner writes the whole unit of code. A name nobody could derive, such as a magic file name, is a nonword: name it, link it, and don't make the learner guess it.
- **Feedback helps on average (d = 0.48), most when it carries information (0.99) and least as reward or punishment (0.24)** (Wisniewski, Zierer & Hattie 2020). Over a third of feedback interventions made performance worse, and feedback aimed at the person rather than the task does least, praise included (Kluger & DeNisi 1996, *abstract*; Hattie & Timperley 2007). **So**: the check tells the learner whether it works; the solution says why, and names the likely wrong turn. No praise.
- **Feedback helps after an attempt, not before.** Studies that kept answers out of reach until the learner tried show a benefit; studies that did not are inconsistent (Shute 2008, citing Bangert-Drowns et al. 1991). **So**: the solution is hidden, and the check sits outside it so that verifying never needs it.
- **A failed attempt followed by the answer beats reading the answer**, for guesses that were sure to fail (Kornell, Hays & Bjork 2009, *abstract*; Richland, Kornell & Kao 2009, *abstract*), provided correction follows and analyses the error (Metcalfe 2017, *abstract*). **So**: predict items are worth writing even when most predictions will be wrong, as long as the solution explains the actual behaviour.
- **Judging your learning with the answer in view misleads you** (Koriat & Bjork 2005, *abstract*). **So**: checks are external, such as output, tests or behaviour, never "do you understand this?". A recall item later tests what reading the solution only seemed to teach.

## Exercise or flashcard

- **Facts are best kept by spaced retrieval.** Practice testing and distributed practice are the only two techniques of ten rated high utility (Dunlosky et al. 2013), and a spaced flashcard is both at once. Hermans recommends flashcards for learning a new language's syntax (Hermans 2021, *The Programmer's Brain*, chapter 3; table of contents and opening only).
- **Skills are kept by doing them.** The four-component model separates supportive information, the theory a task draws on, from the learning tasks themselves, and keeps drill for routines that must become automatic (van Merriënboer 2019). Memory depends on how closely the processing at study matches the processing it is later used for (Morris, Bransford & Franks 1977, *abstract*).
- **So**: what can be stated in a sentence goes on a card, and an exercise is kept for what has to be done. A concept with both sides gets both, once each.

## Real tasks

- **Transfer falls with the distance between practice and use**, and with the step from being told which method to use to recognising which one applies (Barnett & Ceci 2002). Whole tasks taken from real work drive the four-component model (van Merriënboer 2019). Problems learners recognise from their work leave all their effort for the tool; puzzles of unclear purpose put learners off (Hogan 2015, *Exercises for Programmers*, preface).
- **So**: every exercise is a task from real work, even when it needs several concepts at once. The limit is on concepts new to the learner, not on concepts.

## Hints

- **Learners click straight through hints to the answer.** In intelligent tutors, 68% of the hint levels before the last were viewed for under a second, and this help abuse went with poorer learning. Hints that state the principle helped understanding; answer-giving hints helped only when the learner explained them (Aleven, Roll, McLaren & Koedinger 2016).
- **So**: no hints. A learner who is stuck opens the solution, which carries what helped in a hint, the principle and the likely wrong turn, along with the answer.

## How much to guide

- **Worked examples beat problem solving early, and problem solving wins later** (Renkl & Atkinson 2003, *abstract*; Kirschner, Sweller & Clark 2006). **The advantage reverses with expertise**: guidance that helps novices gets in experts' way (Kalyuga, Ayres, Chandler & Sweller 2003, *abstract*; Brown, Hermans & Margulieux 2024). An experienced developer is an expert in programming and a novice in the new tool. **So**: guide only what is new in the tool, and fade the guidance quickly.
- **Attempting first can beat instruction first**, for conceptual understanding and transfer (g = 0.36 over 53 studies), but the effect reverses for young learners and for domain-general skills (Sinha & Kapur 2021, *abstract*). It needs a problem that engages without defeating, admits several approaches, draws on what the learner knows, and is followed by comparison with the correct solution (Kapur 2016). How many interacting elements the material has decides which order wins (Chen, Kalyuga & Sweller 2015, *abstract*). **So**: let the learner attempt first where reasoning from what they know can reach the answer. Name the feature first where it is an arbitrary convention of the tool.
- **Being told which approach to use is not the same skill as recognising which one applies**, and real work needs the second (Barnett & Ceci 2002). **So**: name a feature the first time, then give only the goal, then make the learner choose between look-alikes.

## How much goes in one exercise

- Working memory is limited for new material. How much an exercise can carry depends on how much its new elements interact, and on what the learner already knows (Sweller, van Merriënboer & Paas 2019). No source gives a number.
- **So**: one new tool idea per exercise is this skill's own working rule, not a research finding. Ideas the learner already has from programming cost almost nothing.
- Text the task does not need is extraneous load: it takes working memory from what is new (Sweller, van Merriënboer & Paas 2019). **So**: an item is as short as its task allows, and material from outside the target shrinks to a stand-in.

## Order and revisits

- **Spacing beats massing, and the best gap grows with how long the knowledge must last** (Cepeda et al. 2006, *abstract*; Cepeda et al. 2008, *abstract*). Recalling a concept to three correct answers, then relearning it three times at spaced intervals, gave large gains in retention for little extra time (Rawson & Dunlosky 2011, *abstract*). **So**: each core idea comes back at least twice, unannounced, and a recall item closes the set for a later day.
- **Interleaving helps when the categories are similar and must be told apart** (g = 0.42 over 59 studies), more so the more similar the categories, and blocking wins for word lists (g = −0.39) (Brunmair & Richter 2019). **So**: mix only look-alike features, and only after each has been introduced on its own.
- **Variation helps when the load is low and hurts when it is high** (Paas & van Merriënboer 1994, *abstract*; Wulf & Shea 2002), and gains from a worked example carry over only to problems of the same structure (Sweller & Cooper 1985, *abstract*). **So**: keep a feature's first use plain, and vary the input and the entity on later uses.

## Which types pay off

- **Reading and predicting go with writing.** Skill at tracing code correlated with skill at writing it (r = .63), and explaining code in plain English correlated at r = .56 (Lopez, Whalley, Robbins & Lister 2008). PRIMM's order, predict, run, investigate, modify, then make, beat the comparison classes in a quasi-experiment with 11- to 14-year-olds (Sentance, Waite & Kallia 2019). **So**: predict items before build items when a feature behaves in a way the learner might not expect.
- **False friends hinder transfer**: features similar in syntax and different in semantics across languages (Brown, Hermans & Margulieux 2024). **So**: aim predict and break items at the places where this tool looks like one the learner knows.
- **Finding a bug is the hard part.** Once students found a bug, they fixed it 97% of the time (Fitzgerald et al. 2008, *abstract*). **So**: a fix-the-bug item trains finding; describe the symptom, not the location.
- **Comparing two cases beats studying them separately** (d = 0.50 over 57 experiments), especially when the learner looks for what they share and the principle comes after the comparison (Alfieri, Nokes-Malach & Schunn 2013, *abstract*). **So**: compare items name the principle in the solution, not in the prompt.

## The shape of a set

- **Whole tasks, from simple to complex, with support that fades.** Drill only the routines that must become automatic, and only after the whole task has shown why they matter (the four-component instructional design model, in van Merriënboer 2019 and in Sweller, van Merriënboer & Paas 2019). **So**: one project grows across the set, and the capstone is a whole task.
- **Design backwards from the final performance** (McTighe & Wiggins 2012). Wilson's version: write the program the learner should finish with, remove its hardest part to make the last exercise, and repeat (Wilson 2019, *Teaching Tech Together*). **So**: write the capstone first.
- **Break the skill into subskills, practise the most important first, learn enough to self-correct, and remove the barriers to practising** (Kaufman 2013, *The First 20 Hours*, excerpt). **So**: the day-one loop comes first, and exercise 1 is a quick, visible win.
- **Teach what the tool is, not a tour of its features**: the skills learners need to do things, and the model of how the tool runs (The Carpentries, lesson design training; Wilson 2019). Teach the concepts the tool actually has, not those other tools have (Exercism, syllabus docs).
- **Doing beats reading by a wide margin**: in one online course, extra practice was associated with more than six times the learning of extra reading or watching (Koedinger et al. 2015, correlational). **So**: the README carries almost no prose, and each item as few words as its task allows.
- **Learning styles are a myth**: there is virtually no evidence that matching instruction to a preferred style helps (Pashler, McDaniel, Rohrer & Bjork 2008, *abstract*). **So**: no "visual" or "hands-on" variants. Match the format to the content.

## Wording

- **Say what to do, not how**, name the artefact the learner must build, and give an example that differs from the tests (Exercism, concept exercise instructions).
- **One verifiable verb, one skill**, never "understand", "learn" or "explore" (The Carpentries, defining lesson objectives; Wilson 2019).
- **Every sentence will be skipped by someone**, so a key fact stated once is a fact some learners never see (Eric Wastl, on writing Advent of Code puzzles, in a talk). **So**: every fact the task depends on goes in the item itself.

## Sizing

- Exercism aims its concept exercises at 5 to 10 minutes for a developer experienced in another language; a CodeKata takes 30 to 60 minutes; Wilson recommends a check every 10 to 15 minutes of teaching. These are targets set by their authors, not measured optimums.
- **So**: 5 to 10 minutes per item, never more than 15, and the capstone only as long as combining the core takes.

## Where the evidence is weak

- No study compares a project with drills for developers learning a tool. The project spine with drills only for routines is an inference from the four-component model and from transfer research.
- Spacing ratios come from fact learning; applying them to code is inference.
- Productive failure was studied mostly in school maths, in groups, with a teacher guiding the comparison afterwards. A learner alone has neither, which is why the solution must carry the comparison.
- Dropping hints extends the finding that hints get skipped to experienced developers, and follows the learner's own preference for less to read.

## Sources

- Alfieri, L., Nokes-Malach, T. J., & Schunn, C. D. (2013). Learning through case comparisons: a meta-analytic review. https://doi.org/10.1080/00461520.2013.775712
- Aleven, V., Roll, I., McLaren, B. M., & Koedinger, K. R. (2016). Help helps, but only so much. https://link.springer.com/content/pdf/10.1007/s40593-015-0089-1.pdf
- Barnett, S. M., & Ceci, S. J. (2002). When and where do we apply what we learn? A taxonomy for far transfer. http://rapunselshair.pbworks.com/f/barnett_2002.pdf
- Bertsch, S., Pesta, B. J., Wiscott, R., & McDaniel, M. A. (2007). The generation effect: a meta-analytic review. https://link.springer.com/article/10.3758/BF03193441
- Brown, N. C. C., Hermans, F. F. J., & Margulieux, L. E. (2024). 10 things software developers should learn about learning. https://cacm.acm.org/research/10-things-software-developers-should-learn-about-learning
- Brunmair, M., & Richter, T. (2019). Similarity matters: a meta-analysis of interleaved learning. https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf
- Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks. https://doi.org/10.1037/0033-2909.132.3.354
- Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: a temporal ridgeline of optimal retention. https://pubmed.ncbi.nlm.nih.gov/19076480/
- Chen, O., Kalyuga, S., & Sweller, J. (2015). The worked example effect, the generation effect, and element interactivity. https://doi.org/10.1037/edu0000018
- The Carpentries. Collaborative Lesson Development Training: designing exercises, and defining lesson objectives. https://carpentries.github.io/lesson-development-training/formative-assessment.html and https://carpentries.github.io/lesson-development-training/objectives.html
- Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques. https://www.whz.de/fileadmin/lehre/hochschuldidaktik/docs/dunloskiimprovingstudentlearning.pdf
- Exercism. Concept exercises, and syllabus. https://exercism.org/docs/building/tracks/concept-exercises and https://exercism.org/docs/building/tracks/syllabus
- Fitzgerald, S., et al. (2008). Debugging: finding, fixing and flailing. https://eric.ed.gov/?id=EJ810215
- Hattie, J., & Timperley, H. (2007). The power of feedback. https://ctl.univie.ac.at/fileadmin/user_upload/z_ctl/Feedback/Hattie_Timperley_2007_Power_of_Feedback_1_.pdf
- Hermans, F. (2021). The Programmer's Brain, chapter 3. https://livebook.manning.com/book/the-programmers-brain/chapter-3
- Hogan, B. P. (2015). Exercises for Programmers, preface. https://media.pragprog.com/titles/bhwb/preface.pdf
- Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. https://doi.org/10.1207/S15326985EP3801_4
- Kapur, M. (2016). Examining productive failure, productive success, unproductive failure, and unproductive success in learning. https://www.nomanis.com.au/hubfs/Nomanis_June2023/Pdf/Examining%20Productive%20Failure%20Productive%20Success%20Unproductive%20Failure%20and%20Unproductive%20Success%20in%20Learning.pdf
- Kaufman, J. (2013). The First 20 Hours, chapters 1 to 3. https://faculty.bard.edu/hhaggard/teaching/sci127Sp20/notes/KaufmanFirstTwentyHoursExcerpt.pdf
- Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). Why minimal guidance during instruction does not work. https://itgs.ict.usc.edu/papers/Constructivism_KirschnerEtAl_EP_06.pdf
- Kluger, A. N., & DeNisi, A. (1996). The effects of feedback interventions on performance. https://doi.org/10.1037/0033-2909.119.2.254
- Koedinger, K. R., Kim, J., Jia, J. Z., McLaughlin, E. A., & Bier, N. L. (2015). Learning is not a spectator sport. http://pact.cs.cmu.edu/pubs/koedinger,%20Kim,%20Jia,%20McLaughlin,%20Bier%202015.pdf
- Koriat, A., & Bjork, R. A. (2005). Illusions of competence in monitoring one's knowledge during study. https://doi.org/10.1037/0278-7393.31.2.187
- Kornell, N., Hays, M. J., & Bjork, R. A. (2009). Unsuccessful retrieval attempts enhance subsequent learning. https://pubmed.ncbi.nlm.nih.gov/19586265/
- Lopez, M., Whalley, J., Robbins, P., & Lister, R. (2008). Relationships between reading, tracing and writing skills in introductory programming. https://opus.lib.uts.edu.au/bitstream/10453/10806/1/2008001530.pdf
- McTighe, J., & Wiggins, G. (2012). Understanding by Design framework. https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf
- Metcalfe, J. (2017). Learning from errors. https://doi.org/10.1146/annurev-psych-010416-044022
- Morris, C. D., Bransford, J. D., & Franks, J. J. (1977). Levels of processing versus transfer appropriate processing. https://eric.ed.gov/?id=EJ171929
- Paas, F., & van Merriënboer, J. J. G. (1994). Variability of worked examples and transfer of geometrical problem-solving skills. https://doi.org/10.1037/0022-0663.86.1.122
- Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008). Learning styles: concepts and evidence. https://pubmed.ncbi.nlm.nih.gov/26162104
- Rawson, K. A., & Dunlosky, J. (2011). Optimizing schedules of retrieval practice for durable and efficient learning. https://doi.org/10.1037/a0023956
- Renkl, A., & Atkinson, R. K. (2003). Structuring the transition from example study to problem solving. https://doi.org/10.1207/S15326985EP3801_3
- Richland, L. E., Kornell, N., & Kao, L. S. (2009). The pretesting effect. https://doi.org/10.1037/a0016496
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning. https://pubmed.ncbi.nlm.nih.gov/16507066/
- Sentance, S., Waite, J., & Kallia, M. (2019). Teaching computer programming with PRIMM. https://primmportal.com/wp-content/uploads/2020/10/teaching-computer-programming-with-primm-a-sociocultural-perspective.pdf
- Shute, V. J. (2008). Focus on formative feedback. https://myweb.fsu.edu/vshute/pdf/shute%202008_b.pdf
- Sinha, T., & Kapur, M. (2021). When problem solving followed by instruction works. https://doi.org/10.3102/00346543211019105
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. https://doi.org/10.1207/s1532690xci0201_3
- Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. https://link.springer.com/content/pdf/10.1007/s10648-019-09465-5.pdf
- van Merriënboer, J. J. G. (2019). The four-component instructional design model: an overview of its main design principles. https://www.4cid.org/wp-content/uploads/2021/04/vanmerrienboer-4cid-overview-of-main-design-principles-2021.pdf
- Wastl, E. Advent of Code: behind the scenes (talk). https://www.youtube.com/watch?v=_oNOTknRTSU
- Wilson, G. (2019). Teaching Tech Together. https://teachtogether.tech/en/index.html
- Wisniewski, B., Zierer, K., & Hattie, J. (2020). The power of feedback revisited. https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full
- Wulf, G., & Shea, C. H. (2002). Principles derived from the study of simple skills do not generalize to complex skill learning. https://link.springer.com/content/pdf/10.3758/BF03196276.pdf
