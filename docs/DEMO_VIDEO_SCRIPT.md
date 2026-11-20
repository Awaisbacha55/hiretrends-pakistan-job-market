# HireTrends — Video Walkthrough & Presentation Script
## 2–3 Minute Executive Demo Script for LogicBlaze Technologies Internship

**Project:** HireTrends — Pakistan Tech Job Market Intelligence  
**Author:** Awais Bacha  
**YouTube Demonstration Video:** [https://youtu.be/Gcz30Iix90Q](https://youtu.be/Gcz30Iix90Q)  
**Live Interactive Dashboard:** [https://hiretrends-pakistan-job-market-zcyjuxxmt7gyyq3e6dfsl2.streamlit.app/skill_cooccurrence](https://hiretrends-pakistan-job-market-zcyjuxxmt7gyyq3e6dfsl2.streamlit.app/skill_cooccurrence)  
**Target Video Duration:** 2 minutes 30 seconds to 3 minutes  
**Target Audience:** Technical Mentors, Hiring Managers, Internship Evaluators  
**Recommended Screen Setup:** 1920x1080 or 1440x900 browser window, Streamlit sidebar expanded, light SaaS theme active.

---

## Slide / Screen Timing & Storyboard

```
00:00 - 00:25 | Scene 1: Introduction & The Core Problem (Market Overview)
00:25 - 00:55 | Scene 2: Skills Explorer & Technical Demand Hierarchy
00:55 - 01:25 | Scene 3: The USD-PKR Divide & Salary Insights
01:25 - 01:55 | Scene 4: Geographic Hubs & Remote Realities
01:55 - 02:25 | Scene 5: Skill Co-occurrence & Occupational Career Stacks
02:25 - 02:50 | Scene 6: Architecture, Ethics, Testing & Deployment
```

---

## Full Presentation Script

### Scene 1: Introduction & The Core Problem (00:00 – 00:25)
**Visual:** Show the **Market Overview** page (`http://localhost:8501`). Highlight the 4 top KPI cards (Total Postings: 4,491; Confirmed Tech Roles: 1,075; Disclosed Salaries: 174; Localized Cities: 2,684).

> **Presenter Voiceover:**  
> "Hello! My name is Awais Bacha, and this is **HireTrends** — an ethical, empirical job market intelligence platform built during Week 3 of the LogicBlaze Technologies Data Engineering Internship.
> 
> Computer science students and job seekers in Pakistan often ask: *What skills are truly in demand? Does remote work actually pay more? Which cities lead hiring?*  
> 
> Instead of guessing, HireTrends answers these questions with hard empirical evidence collected from **4,491 genuine job postings** in Pakistan via the official Headcount Labs API under Open Database License."

---

### Scene 2: Skills Explorer & Technical Demand Hierarchy (00:25 – 00:55)
**Visual:** Navigate to the **Skills Explorer** page. Show the top skills bar chart (Python, SQL, JavaScript, React, AWS). Type "Docker" into the search box to demonstrate dynamic filtering, then show the CSV download button.

> **Presenter Voiceover:**  
> "Navigating to our **Skills Explorer**, we analyze 69 standardized technical frameworks extracted using word-boundary regular expressions across more than 4,300 job descriptions.
> 
> **Python** leads as Pakistan’s number-one technology skill, required in **33.3%** of all confirmed engineering roles, driven by backend microservices and AI workloads. **SQL** ranks second at nearly 30%, followed by **JavaScript** and **React** at over 20%. 
> 
> We can filter by domain cluster—such as Cloud & DevOps or AI—search for specific skills like Docker or AWS, and export our demand tables directly to CSV."

---

### Scene 3: The USD-PKR Divide & Salary Insights (00:55 – 01:25)
**Visual:** Navigate to **Salary Insights**. Point to the Currency Distribution bar chart and the Compensation Quartile Benchmarks table.

> **Presenter Voiceover:**  
> "On the **Salary Insights** page, we tackle Pakistan's tech compensation landscape. Because pay in emerging markets is heavily right-skewed, we model compensation non-parametrically using medians and quartiles rather than easily distorted averages.
> 
> Across 174 disclosed compensation records converted to monthly PKR via official State Bank of Pakistan exchange rates, we uncover a fascinating dual economy:  
> Domestic companies quoting in PKR have a median monthly wage of **PKR 75,000**. In contrast, international employers hiring remote contractors quote in USD with a median wage of **PKR 278,500**—roughly 1,000 dollars a month—creating an immediate 3.7x salary multiplier for developers who can work internationally."

---

### Scene 4: Geographic Hubs & Workplace Distribution (01:25 – 01:55)
**Visual:** Click **Location Analysis** and then **Workplace Analysis**. Show the Big Three concentration donut chart and the workplace arrangement horizontal bar chart.

> **Presenter Voiceover:**  
> "Looking at **Location Analysis**, Pakistan’s tech hiring is overwhelmingly concentrated. The 'Big Three' metropolises—**Lahore at 38%**, **Karachi at 32%**, and **Islamabad at 23%**—command more than 93% of all localized tech postings.
> 
> Meanwhile, on the **Workplace Analysis** page, we see that **51.8%** of postings with explicit workplace policies are fully remote. This proves that Pakistani developers are increasingly competing on the global stage without relocating."

---

### Scene 5: Skill Co-occurrence & Career Specialization (01:55 – 02:25)
**Visual:** Click **Skill Co-occurrence**. Show the 12x12 heatmap and the top co-occurring skill pairs table. Click on **Role Explorer** to show a Full Stack Engineer profile.

> **Presenter Voiceover:**  
> "In the **Skill Co-occurrence** page, we analyze pairwise affinities. Skills rarely exist in isolation: we see high correlation between **React and Node.js**, **Python and SQL**, and **AWS and Docker**.  
> 
> Using our **Role Explorer**, students can inspect exact skill profiles for 12 core occupations—such as Full Stack Engineer, DevOps Engineer, or AI Scientist—giving them a clear, data-driven learning curriculum."

---

### Scene 6: Architecture, Ethics, Testing & Deployment (02:25 – 02:50)
**Visual:** Open the **Data & Methodology** page. Scroll down to show the census reconciliation table, test suite badge, and ODbL license statement.

> **Presenter Voiceover:**  
> "Under the hood, HireTrends is built with Python 3.12, Pandas, Plotly, and Streamlit. The codebase is tested offline by **125 automated pytest unit tests** with a 100% pass rate.
> 
> We adhere strictly to data collection ethics: our system audits platform permissions, prevents credential leaks, and protects employer copyright by excluding full-text job descriptions.  
> 
> HireTrends is fully containerized, reproducible, and ready for deployment on Streamlit Community Cloud. Thank you!"

---

## Presenter Delivery Tips
- **Pacing:** Speak clearly with steady confidence. Do not rush through the numbers.
- **Mouse Movements:** Keep the cursor purposeful; point to chart elements as you mention them.
- **Browser State:** Use fullscreen browser mode (`F11`) with browser address bar hidden if possible.
- **Audio:** Use a clean external microphone with background noise cancellation.
