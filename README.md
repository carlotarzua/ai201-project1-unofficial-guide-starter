# The Unofficial Guide — Project 1

## Domain

My project is **The Unofficial Guide to DePaul Professors**. It covers unofficial student reviews of DePaul University professors collected from Rate My Professors.

This knowledge is valuable because official DePaul course catalogs and department pages usually list course descriptions, instructor names, and requirements, but they do not explain what students actually experience in class. Students often want to know things like whether a professor gives useful feedback, whether exams are hard, whether attendance matters, how heavy the workload is, and whether the professor is caring or difficult. This kind of student-experience information is easier to find in unofficial reviews than in official university sources.

---

## Document Sources

I collected 10 Rate My Professors professor review pages for DePaul University. Each professor page was saved as one cleaned `.txt` file in `data/raw/`. The actual Rate My Professors URL is included in the `Source URL` line inside each raw text file.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Eric Landahl | Professor review page | `data/raw/eric_landahl.txt` |
| 2 | Rate My Professors — Kristina Thomas | Professor review page | `data/raw/kristina_thomas.txt` |
| 3 | Rate My Professors — Yang Choi | Professor review page | `data/raw/yang_choi.txt` |
| 4 | Rate My Professors — Kenny Castellanos | Professor review page | `data/raw/kenny_castellanos.txt` |
| 5 | Rate My Professors — Nancy Brown | Professor review page | `data/raw/nancy_brown.txt` |
| 6 | Rate My Professors — Xorla Ocloo | Professor review page | `data/raw/xorla_ocloo.txt` |
| 7 | Rate My Professors — Juan Hu | Professor review page | `data/raw/juan_hu.txt` |
| 8 | Rate My Professors — Emily Barnard | Professor review page | `data/raw/emily_barnard.txt` |
| 9 | Rate My Professors — Naomi Wangler | Professor review page | `data/raw/naomi_wangler.txt` |
| 10 | Rate My Professors — Kaitlyn Bolyard | Professor review page | `data/raw/kaitlyn_bolyard.txt` |

---

## Document Pipeline

The document pipeline loads all `.txt` files from `data/raw/`, cleans the text, splits it into chunks, and saves the result to `data/chunks.json`.

The raw files were copied from Rate My Professors pages and cleaned before being used by the RAG system. I removed website clutter such as navigation text, buttons, “Helpful,” thumbs up/down counts, ads, “Rate,” “Compare,” and unrelated promotional text. I kept the professor name, department, rating summary, course codes, dates, attendance information, difficulty ratings, tags, and actual student review text.

The ingestion script is `ingest.py`. It creates chunk objects with:

- `id`
- `text`
- `metadata.source`
- `metadata.professor`
- `metadata.chunk_index`

This metadata is important because the final answer must cite which professor/source file the information came from.

---

## Chunking Strategy

**Chunk size:** 700 characters

**Overlap:** 100 characters

**Why these choices fit my documents:**

My documents are Rate My Professors reviews, which are short and opinion-based. A 700-character chunk usually keeps a complete student review or a small group of related review details together, such as the course code, difficulty rating, attendance information, and the review itself.

I used 100 characters of overlap because some important details may fall near a chunk boundary. For example, a course code or professor name might appear just before the review text. The overlap helps preserve context so retrieval can still return useful chunks.

**Preprocessing:**

Before chunking, I removed repeated page clutter and kept only the meaningful review content. I also normalized whitespace so the chunks would be readable.

**Final chunk count:** 81 chunks

---

## Sample Chunks

### Sample Chunk 1 — `emily_barnard.txt`

```text
Professor: Emily Barnard
School: DePaul University
Department: Mathematics
Overall Quality: 4.6 / 5
Number of Ratings: 5
Would Take Again: 100%
Level of Difficulty: 3.2 / 5

Review 1
Course: MAT150
Date: Apr 6th, 2026
Quality: 5.0
Difficulty: 3.0
Review: Easily the best professor I have taken at DePaul. Actually cares about her students and formats the lectures in a digestible way. Also always available outside of class and during office hours.
```

### Sample Chunk 2 — `kaitlyn_bolyard.txt`

```text
Professor: Kaitlyn Bolyard
Source: kaitlyn_bolyard.txt

Review: Professor Bolyard is very nice, tries to get the class talking about different opinions they had on the assigned textbooks, isn't a harsh grader, and will happily help or give second chances on assignments if you take the class seriously. Her class isn't hard. She gives extra credit for participation and has a lot of easy group work.
```

### Sample Chunk 3 — `kenny_castellanos.txt`

```text
Professor: Kenny Castellanos
Source: kenny_castellanos.txt

Review: TERRIBLE. He would take FOREVER to grade the assignments, the assignments were very difficult, and the final was very long and difficult. The class is interesting and useful but he's a very boring professor who just reads off slides and it'll bore you easily.
Tags: Tough Grader, Lecture Heavy, Graded by Few Things
```

### Sample Chunk 4 — `eric_landahl.txt`

```text
Professor: Eric Landahl
School: DePaul University
Department: Physics
Overall Quality: 3.9 / 5

Review: Landahl is a relaxed but incredibly knowledgeable teacher. The grade consists of in-class work, quizzes every other week, a midterm project, and a final paper.
Tags: Caring, Respected
```

### Sample Chunk 5 — `nancy_brown.txt`

```text
Professor: Nancy Brown
Source: nancy_brown.txt

Review: Nancy Brown is one of the most amazing professors at DePaul. Attendance does matter but she really cares about her students and it shows. She is very accessible outside of class and always willing to help. There is a fair amount of reading, easy quizzes, and discussion with classmates.
Tags: Group Projects, Caring
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` from `sentence-transformers`

I used `all-MiniLM-L6-v2` because it runs locally, is free, does not require an embedding API key, and works well for small semantic-search projects. It can match related ideas even when the query does not use the exact same words as the review. For example, a question about whether a professor is “helpful” can retrieve reviews that use words like “accessible,” “caring,” or “willing to help.”

**Vector store:** ChromaDB

**Top-k:** 4 retrieved chunks per query

**Production tradeoff reflection:**

If I were deploying this for real users and cost was not a constraint, I would compare embedding models based on accuracy, latency, cost, privacy, context length, and multilingual support. A larger API-hosted embedding model might perform better on messy student language or subtle opinion questions, but it would cost more and may be slower. A local model is cheaper and keeps the data private, but it may be less accurate for nuanced queries or uncommon phrasing.

---

## Retrieval Test Results

### Retrieval Test 1

**Query:** What do students say about Eric Landahl's lecture style?

| Rank | Professor | Source | Distance | Top returned chunk summary |
|---|---|---|---|---|
| 1 | Eric Landahl | `eric_landahl.txt` | 0.6771 | A review says he never lectured much and was unclear or unprepared. |
| 2 | Eric Landahl | `eric_landahl.txt` | 0.7630 | A review describes him as relaxed and knowledgeable. |
| 3 | Eric Landahl | `eric_landahl.txt` | 0.8748 | A review says he does not teach much and students have to teach themselves. |
| 4 | Eric Landahl | `eric_landahl.txt` | 0.9519 | A review says he was prepared and helped students prepare for tests. |

**Why the returned chunks are relevant:**  
The chunks are relevant because they directly discuss Landahl’s teaching and lecture style. The results show mixed student opinions: some students say he does not lecture clearly, while others say he is knowledgeable or prepared.

### Retrieval Test 2

**Query:** Is Kenny Castellanos described as difficult?

| Rank | Professor | Source | Distance | Top returned chunk summary |
|---|---|---|---|---|
| 1 | Kenny Castellanos | `kenny_castellanos.txt` | 1.0323 | A review says assignments and the final were very difficult. |
| 2 | Kenny Castellanos | `kenny_castellanos.txt` | 1.1007 | A review describes a very negative experience in Data Structures. |
| 3 | Kenny Castellanos | `kenny_castellanos.txt` | 1.1189 | A review says he does not teach well and has unrealistic due dates. |
| 4 | Kenny Castellanos | `kenny_castellanos.txt` | 1.1205 | A review mentions a low midterm average and test-heavy work. |

**Why the returned chunks are relevant:**  
The chunks are relevant because they come from Kenny Castellanos’s review file and include comments about difficulty, strict due dates, difficult assignments, test-heavy work, and negative student experiences.

### Retrieval Test 3

**Query:** What do students say about Kaitlyn Bolyard's feedback and grading?

| Rank | Professor | Source | Distance | Top returned chunk summary |
|---|---|---|---|---|
| 1 | Kaitlyn Bolyard | `kaitlyn_bolyard.txt` | 0.5679 | A review says she is not a harsh grader and gives second chances. |
| 2 | Kaitlyn Bolyard | `kaitlyn_bolyard.txt` | 0.6007 | A review describes easy assignments and peer groups. |
| 3 | Kaitlyn Bolyard | `kaitlyn_bolyard.txt` | 0.6463 | A review says she is a clear grader who gives great feedback. |
| 4 | Kaitlyn Bolyard | `kaitlyn_bolyard.txt` | 0.6512 | A review says she has clear criteria and offers extra credit. |

**Why the returned chunks are relevant:**  
The chunks directly answer the question because they mention feedback, grading, extra credit, clear criteria, second chances, and whether the class is hard.

---

## Grounded Generation

**LLM used:** Groq `llama-3.3-70b-versatile`

**System prompt grounding instruction:**

```text
You are an assistant for The Unofficial Guide to DePaul Professors.

Answer the user's question using ONLY the provided retrieved source chunks.
Do not use outside knowledge.
If the retrieved chunks do not contain enough information to answer, say:
"I don't have enough information in the provided sources to answer that."

When you answer, cite the professor names and source filenames that support your answer.
Be honest about mixed or contradictory student reviews.
```

**How source attribution is surfaced in the response:**

Each retrieved chunk includes metadata for the professor name and source file. The `query.py` script formats the context with source labels before sending it to Groq. After generation, the app also displays a separate **Sources** box listing the professor and file name, such as:

```text
Eric Landahl — eric_landahl.txt
```

This means source attribution is not only left to the LLM. It is also surfaced programmatically from the retrieved metadata.

---

## Example Responses

### Example Response 1

**Question:** What do students say about Eric Landahl's lecture style?

**System response:**

```text
According to the reviews, Eric Landahl's lecture style is inconsistent and has received mixed feedback from students. Some students praised him as knowledgeable and relaxed, while others criticized him for not lecturing much and being unclear or unprepared. Overall, the reviews suggest that Landahl's lecture style may work for some students but not for others.

Sources: Eric Landahl — eric_landahl.txt
```

### Example Response 2

**Question:** Is Kenny Castellanos described as difficult?

**System response:**

```text
Yes. According to the retrieved reviews, Kenny Castellanos is often described as difficult. Students mention difficult assignments, strict due dates, test-heavy work, lecture-heavy classes, and confusing explanations. However, one retrieved review disagrees and says students need to be willing to learn independently. Overall, most of the retrieved reviews describe the class as challenging.

Sources: Kenny Castellanos — kenny_castellanos.txt
```

### Out-of-Scope Example

**Question:** What dining hall has the best food at DePaul?

**System response:**

```text
I don't have enough information in the provided sources to answer that.

The provided sources do not mention anything about dining halls at DePaul University. They only contain information about professors, their courses, and student reviews.
```

---

## Query Interface

The project uses a Gradio web interface in `app.py`.

**Input field:**

- `Your question`: a natural-language question about DePaul professors.

**Output fields:**

- `Answer`: the generated grounded answer.
- `Sources`: professor names and source filenames used.
- `Retrieved chunks`: the top retrieved chunks with professor, source, distance score, and text preview.

**Sample interaction transcript:**

```text
User question:
What do students say about Kaitlyn Bolyard's feedback and grading?

Answer:
According to the reviews from kaitlyn_bolyard.txt, students say Professor Kaitlyn Bolyard gives great feedback and is a clear grader. She is also described as an easy grader who gives full points when students put effort into their work. Several reviews mention clear grading criteria, extra credit, second chances, and helpful feedback.

Sources:
- Kaitlyn Bolyard — kaitlyn_bolyard.txt

Retrieved chunks:
Chunk 1
Professor: Kaitlyn Bolyard
Source: kaitlyn_bolyard.txt
Distance: 0.5679
...
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Eric Landahl’s lecture style? | Reviews are mixed. Some students say he does not lecture much and students have to figure things out themselves, while others say he is knowledgeable or prepared. | The system said reviews are mixed: some students describe him as knowledgeable and relaxed, while others criticize him for not lecturing, being unclear, or making students teach themselves. | Relevant | Accurate |
| 2 | Is Kenny Castellanos described as difficult? | Yes. Many reviews describe difficult assignments, strict due dates, test-heavy work, confusing explanations, and warnings not to take him. | The system said he is often described as difficult, with difficult assignments, strict due dates, test-heavy work, and negative reviews, while noting one contradictory positive review. | Relevant | Accurate |
| 3 | What do students say about Kaitlyn Bolyard’s feedback and grading? | Students generally describe her as clear, kind, helpful, and not harsh. Reviews mention clear grading criteria, feedback, extra credit, and manageable writing assignments. | The system said Bolyard gives great feedback, is a clear grader, offers extra credit, gives second chances, and is often described as caring or sweet. | Relevant | Accurate |
| 4 | Which professors are described as caring or helpful? | Possible correct answers include Juan Hu, Kaitlyn Bolyard, Eric Landahl, Yang Choi, Nancy Brown, Xorla Ocloo, Emily Barnard, and Naomi Wangler, depending on the retrieved chunks. | The system retrieved and summarized professors such as Juan Hu, Kaitlyn Bolyard, Eric Landahl, and Yang Choi as caring or helpful. | Relevant | Partially accurate |
| 5 | What complaints do students make about Kristina Thomas? | Complaints include unclear expectations, limited feedback, arbitrary grading, lectures that are hard to follow, difficulty talking to her, D2L issues, slow grading, and negative SCWR302 experiences. | The system identified complaints about unclear expectations, difficult communication, hard-to-follow lectures, grading issues, D2L problems, and negative student experiences. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

```text
Is Kenny Castellanos described as difficult?
```

**What the system returned originally:**

Before I added metadata filtering, semantic retrieval returned chunks from Eric Landahl and Yang Choi instead of Kenny Castellanos. Those chunks had words related to difficulty, lecturing, or confusing classes, but they were from the wrong professor.

**Root cause tied to a specific pipeline stage:**

This was a retrieval-stage failure. Semantic search alone focused on general concepts like “difficult,” “lecture,” and “confusing,” but it did not reliably enforce that the answer had to come from Kenny Castellanos’s reviews. The system was matching the topic of difficulty but not the professor identity.

**What I changed to fix it:**

I added professor metadata filtering in `retrieve.py`. When a query includes a known professor name, the retrieval function applies a ChromaDB metadata filter so only chunks from that professor’s source file are returned. After this change, the Kenny Castellanos query retrieved chunks only from `kenny_castellanos.txt`.

**What I would change next:**

I would improve the chunking strategy so chunks begin cleanly at review boundaries instead of sometimes starting in the middle of a sentence. Some chunks currently begin with partial words because the splitter uses character boundaries. A sentence-aware or review-aware chunker would make chunks more readable and probably improve retrieval quality.

---

## Stretch Feature: Metadata Filtering

I implemented a metadata filtering feature. The retrieval system detects professor names in the query and filters ChromaDB results by the `professor` metadata field.

For example, when the user asks:

```text
Is Kenny Castellanos described as difficult?
```

The system applies:

```text
Metadata filter applied: professor = Kenny Castellanos
```

This visibly changes the results because the retrieved chunks come from `kenny_castellanos.txt` instead of unrelated professor files. This improves professor-specific questions and addresses the retrieval failure described above.

---

## Spec Reflection

**One way the spec helped me during implementation:**

The planning document helped me decide the structure of the system before coding. Because I had already written down my domain, chunk size, overlap, embedding model, top-k value, and evaluation questions, I had a clear guide for each implementation step. This made it easier to build the project in stages instead of trying to build the full app at once.

The spec also helped me test the system honestly. Since the evaluation questions were planned ahead of time, I could compare the system’s actual answers against expected answers instead of changing the questions to match whatever the system did well.

**One way my implementation diverged from the spec, and why:**

My original retrieval plan used semantic search only. During testing, I found that semantic search alone could retrieve chunks from the wrong professor when the query used common words like “difficult” or “helpful.” I changed the implementation by adding metadata filtering when the query includes a known professor name.

This divergence improved the project because professor identity is essential for this domain. A technically similar review from the wrong professor is not useful to the user, so filtering by professor metadata made the system more reliable.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave ChatGPT my project topic, the assignment requirements, and my plan to use DePaul Rate My Professors reviews.
- *What it produced:* It helped draft a complete `planning.md` with the domain, document list, chunking strategy, retrieval approach, evaluation questions, anticipated challenges, architecture diagram, and AI tool plan.
- *What I changed or overrode:* I added my actual professor files and source URLs. I also checked that the plan matched my real project instead of using generic professor-review examples.

**Instance 2**

- *What I gave the AI:* I gave ChatGPT my chunking strategy and explained that my documents were cleaned `.txt` professor review files.
- *What it produced:* It helped generate `ingest.py`, which loads files from `data/raw/`, cleans text, creates 700-character chunks with 100-character overlap, and saves `data/chunks.json`.
- *What I changed or overrode:* I ran the script myself, inspected the sample chunks, and confirmed that it produced 81 chunks. I checked that the chunks were readable and connected to the correct professor.

**Instance 3**

- *What I gave the AI:* I gave ChatGPT my retrieval results, including the problem where the Kenny Castellanos query returned unrelated professor chunks.
- *What it produced:* It suggested adding professor-name detection and ChromaDB metadata filtering to `retrieve.py`.
- *What I changed or overrode:* I tested the updated retrieval script and confirmed that the Kenny query returned only `kenny_castellanos.txt` chunks after the metadata filter was added.

**Instance 4**

- *What I gave the AI:* I gave ChatGPT the grounding requirement and the Gradio interface requirement.
- *What it produced:* It helped create `query.py` for grounded Groq responses and `app.py` for the Gradio interface.
- *What I changed or overrode:* I tested both in-scope professor questions and an out-of-scope dining hall question. I confirmed that the app showed answers, sources, and retrieved chunks, and that it refused to answer when the sources did not contain enough information.
