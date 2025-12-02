from openai import OpenAI
import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime

def export_feedback_to_pdf(report_text, filename="grading_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Grader Report</b>", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    for line in report_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    print(f"✅ PDF saved as {filename}")
    return filename


client = OpenAI(api_key="API KEY HERE")

def process_pdf(pdf_file):
    # Upload the file
    file = client.files.create(
        file=open(pdf_file.name, "rb"),
        purpose="assistants"
    )

    #  Transcription
   # transcription = client.responses.create(
      #  model="gpt-4.1",
       # input=[
        #    {"role": "user", "content": [
        #        {"type": "input_text", "text": "Please transcribe this PDF into clean text."},
        #        {"type": "input_file", "file_id": file.id}
        #    ]}
        #]
    #)

    grading_prompt = """ You will be given the task of grading work as best you can. Do not be a harsh grader, as in only grade the requirements and their completion, not proper practices or efficiency. You may still provide efficiency feedback Your answer should be self-contained, so at the end do not offer follow-up questions. You must internally plan your grading process step-by-step, but only show the final grading output to the user. Do not include any internal reasoning steps or disclaimers — only present the formatted grading report. In the end you have to return a final answer. When you get a question regarding grading a homework or exam, use the appropiate tool and based on the output provide feedback for each individual question whether it is right or wrong. Divide the questions into requirements that is, include the question in your observation and then divide the requirements into bulletpoints and then grade each of the requirements separately. If the question is correct provide short context or anything that would help a student remember the answer for the future. If the answer is incorrect provide additional context and ways to help the student remember the correct answer in the future. Feedback must feel conversational and human. Use analogies, short stories, or metaphors when helpful. Break explanations into short, readable paragraphs with bold emphasis for key terms. The explanations should not be surface level, as they are directed to college students. The goal is to help students feel comfortable and like they are speaking to a human. Make comments as well on the answer the student for example, if they answer a question with the wrong answer say why this answer is not correct. After your observation, reason a score based on the ammount of points a question is worth, provide the answer in the format of x/y where x is the score reasoned and y is the maximum possible score and state clearly why points are removed in the feedback, this is extremely important. The feedback should be 1-3 lines long and be included in the final answer. Avoid saying anything that does not contribute to your answers, be concise and to the point. Provide the final answer at the end with the score and a summary of the feedback."
      
 Grading Focus:
- Grade only based on *requirement completion* and *correctness of answers*.
- **Do NOT** deduct points for code structure, formatting, efficiency, variable names, style, robustness, readability, or portability unless these were explicitly listed as grading criteria in the question.
- You may still provide optional *feedback* on efficiency or robustness, but it must **not affect the score**.
      
 Output Format:
- **Question:** ...
- **Requirements:** ...
- **Feedback:** ...
- **Score:** x/y
- **Summary:** ...

sample answers. Your output should follow this structure exactly.:
Thought:  
First, I’ll break down and grade each question individually, providing feedback for each. I'll check the code functionality, parallel programming knowledge, and clarity of explanation for the conceptual question (Q1). For the coding problems, I'll review both the source code and execution screenshots as evidence of correct behavior.

---

## Q1. Foster’s Methodology (15 points)

Observation:  
- **Partition:** Split by rows for each process—clearly stated.  
- **Communication:** Neighbors share rows—correct and well explained.  
- **Agglomeration:** Use fewer, larger blocks—highlights the trade-off and is sufficient.  
- **Mapping:** One block per process—clear and correct.  
- *Overall*, the answer succinctly and clearly covers each step of Foster’s Methodology, mapping it directly to parallel image blurring.

**Feedback:**  
Excellent summary of Foster’s methodology as applied to image blurring. You correctly identify both the partitioning method (by rows), communication needs (neighbor row sharing), agglomeration (minimizing the number of blocks to reduce communication), and mapping (block-to-process). Nicely condensed yet informative—a great “blueprint” for approaching similar problems!

**Score: 15/15**

---

## Q2. MPI: Even/Odd Rank Communication (25 points)

Observation:  
- The code checks if a rank is odd or even and performs send/receive accordingly.
- Odd ranks send their rank to the *previous* even rank, and even ranks receive from the *next* odd rank, then send their own back.
- The use of `sprintf_s` might cause portability issues—usually, `sprintf` suffices, but in some compilers, `sprintf_s` is preferred for security.
- The execution screenshot confirms the expected output: odd and even processes exchange greetings with each other correctly.
- Notes and comments demonstrate a solid understanding of race conditions and deadlock risks.

**Feedback:**  
Your code achieves the required task: even and odd ranks exchange their ranks, and all processes print their data. Great comment about *deadlock*, which is a classic pitfall in MPI communication. The exchange order is correct, and your output shows every process receiving and printing correctly.  
A future improvement: to ensure portability, you might use `sprintf` instead of `sprintf_s` unless strictly required by the compiler. But this is a very minor point for college-level grading.

**Score: 25/25**

---

## Q3. MPI: Ring Passing and Max Value (30 points)

Observation:  
- Each process generates a unique random number.
- The numbers are circulated around the ring with send/receive.
- Each process updates its local `max_val` as values circulate.
- At the end, process 0 prints the global max.
- Screenshot output shows all processes generating and circulating numbers, and the maximum is calculated and printed.
- One step appears *missing*: After calculating the maximum, the problem asks for process 0 to "send the maximum around the ring so all processes know it." The code as shown does NOT send the maximum value around for others to learn it—only process 0 prints the max.
- No second ring communication for the max.

**Feedback:**  
Nice job implementing the ring-based communication for passing numbers and finding the maximum value—the screenshot shows that all processes actively participate and the maximum is printed by process 0.  
However, one important requirement was missing: after calculating the max, process 0 is supposed to send the maximum value around the ring so that *every* process knows it (not just prints it). Currently, only process 0 knows and prints the maximum. To fix this, you could do a *second* ring pass where process 0 sends `max_val` to (1), (1) to (2), ... and so on, until everyone receives the result.

**Points removed:**  
The missing step is significant (main data-sharing requirement). I will remove **10 points** for not completing the maximum broadcast.

**Score: 20/30**

---

## Q4. MPI: Histogram Binning (30 points)

Observation:  
- The code distributes the generation of 10,000 random floats into four processes.
- Each process bins the numbers into five intervals, counts, and then `MPI_Reduce` collects all local counts to root.
- The use of `srand((unsigned int)time(NULL) * my_rank);` is a common fix to avoid identical seeds.
- Output matches expectations—core 0 prints bin counts and their ranges, totaling 10,000.
- The screenshot matches the requirements: all bins populated, correct output range, and the sum is correct (10000).
- Code is clear and efficient; use of STL `vector` makes for readable bin management.

**Feedback:**  
Well done—you handled parallel data generation, binning, and reduction cleanly. The bin counting approach is solid, and the printed output is clearly organized so you can see the distribution. Your use of `MPI_Reduce` is spot-on for this aggregation task.  
One minor note: for truly random numbers in parallel, more sophisticated seeding or a parallel random number library can help, but your approach suffices for this assignment’s purpose.

**Score: 30/30**

---

## **Final Score and Summary**

- **Q1:** 15/15
- **Q2:** 25/25
- **Q3:** 20/30
- **Q4:** 30/30
- **Total:** **90/100**

---

### **General Comments**
You show a solid grasp of MPI basics and Foster’s methodology. The code structure, understanding of deadlocks, and use of reduction are impressive—all signs of good parallel programming practice. The only major oversight was the missing second pass in Q3 for broadcasting the max value—otherwise, everything else looks great!

Keep up the good work, and remember: in distributed systems, thorough communication (making sure *all* nodes get the result) is as critical as computation! If you’re ever unsure what “everyone knows” at the end of a program, try to think: “How would each process *prove* they know the final answer?” This story-telling approach will help cement the concepts.

-----------------------------------------------------
Requirements:
- **Each core generates a random number.**
- **Numbers passed around the ring using Send/Recv.**
- **After one full cycle, process 0 determines maximum.**
- **Process 0 sends maximum around ring so all processes know.**
- **Correct code execution shown in screenshot.**

Grading breakdown:
- Random generation: Yes.
- Ring send/receive: Yes, implemented via next/prev logic.
- Maximum determination (local): Yes.
- Maximum broadcast (to all): **Not implemented**—after max is found, code only prints it in process 0; it's **not** sent around the ring for all to know.

Feedback:
Almost perfect! You did the “musical chairs” of value passing and local max-updating well, but you didn't implement the last step: sending the found maximum around the ring so every process prints it (not just process 0). This is a common two-phase pattern in parallel reduction: first, a gather to a root, then a broadcast/scatter. Add a second ring pass to send `max_val` around if you want all to know the winner!

Score: **20/30**  
*(Missing implementation of sending max value around the ring to all processes.)*

---

## Q4 (30 Points): MPI Histogram Binning  
Observation:  
Requirements:
- **Generate 10,000 random floats in range [0, 1].**
- **Divide into equal-sized bins (5 bins).**
- **Each process gets equal share (assume 4 cores).**
- **Processes count bin assignments locally.**
- **Results are reduced and printed on core 0.**
- **Correct execution shown in screenshot.**

Grading breakdown:
- Generating random floats: Yes.
- Equal bin division: Yes.
- Equal workload: Yes (numbers_per_process).
- Local counting: Yes.
- Reduction and core 0 output: Yes.

Feedback:  
Great work! All requirements are met. Nice use of `MPI_Reduce` to gather bin counts efficiently. For future reference: for even better randomness in parallel, you might use different seeds from a combination of rank and system entropy (not just time). But your logic and divide-conquer approach is exactly what parallel programming calls for—just like breaking a big pie into neat, even slices for your friends.

Score: **30/30**


      """
    

    # Step 2: Grading
    grading = client.responses.create(
       # model="gpt-5-mini",
         model="gpt-5-2025-08-07",

        input=[
            {"role": "user", "content": [
                {"type": "input_text", "text": (
                    grading_prompt
               
                )},
                {"type": "input_file", "file_id": file.id}
            ]}
        ]
    )

    result_text = grading.output_text

    # Create PDF from result text
    pdf_path = export_feedback_to_pdf(result_text)

    # Return both text and PDF path
    return result_text, pdf_path



# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📘 Homework PDF Transcriber & Grader")

    pdf_input = gr.File(label="Upload your Homework PDF", file_types=[".pdf"])
   # transcribed = gr.Textbox(label="📄 Transcription", lines=15)
    feedback = gr.Textbox(label="✅ Grading Feedback", lines=15)
    pdf_output = gr.File(label="⬇️ Download Grading Report (PDF)")

    run_btn = gr.Button("Process PDF")
    run_btn.click(process_pdf, inputs=pdf_input, outputs=[feedback, pdf_output])


demo.launch()

pdf_input = gr.Files(label="Upload Multiple Homework PDFs", file_types=[".pdf"])

# functionality to process multiple PDFs, not connected to UI yet
def process_pdf(pdf_files):
    all_reports = ""
    all_pdfs = []

    for pdf_file in pdf_files:
        file = client.files.create(
            file=open(pdf_file.name, "rb"),
            purpose="assistants"
        )

        grading = client.responses.create(
            model="gpt-5-2025-08-07",
            input=[
                {"role": "user", "content": [
                    {"type": "input_text", "text": grading_prompt},
                    {"type": "input_file", "file_id": file.id}
                ]}
            ]
        )

        result_text = grading.output_text
        pdf_path = export_feedback_to_pdf(result_text)

        all_reports += f"\n\n===== REPORT FOR: {pdf_file.name} =====\n\n"
        all_reports += result_text
        all_pdfs.append(pdf_path)

    import zipfile
    zip_name = "all_reports.zip"

    with zipfile.ZipFile(zip_name, "w") as zipf:
        for p in all_pdfs:
            zipf.write(p)

    return all_reports, zip_name
