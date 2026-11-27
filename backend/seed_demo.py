import os
import json
from datetime import datetime, timedelta
from database import init_db, SessionLocal, User, Document, Topic, QuizAttempt, QuizQuestion, RevisionPlan
from ingestion import process_and_ingest_file
from diagnostic import build_adaptive_revision_plan

STORAGE_UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "uploads"))
os.makedirs(STORAGE_UPLOADS_DIR, exist_ok=True)

# Sample Documents Content
SYLLABUS_CONTENT = """
COURSE SYLLABUS: CS301 - OPERATING SYSTEMS & SYSTEM ARCHITECTURE
Total Credits: 4 | Examination Weightage: 100 Marks

MODULE 1: PROCESS MANAGEMENT & CPU SCHEDULING
- Topic 1.1: Process States, Process Control Block (PCB), Context Switching
- Topic 1.2: CPU Scheduling Algorithms: FCFS, SJF, Round Robin, Multi-level Queue
- Topic 1.3: Inter-Process Communication (IPC): Shared Memory, Message Passing

MODULE 2: CONCURRENCY, SYNCHRONIZATION & DEADLOCKS
- Topic 2.1: The Critical Section Problem, Race Conditions, Peterson's Algorithm
- Topic 2.2: Synchronization Primitives: Semaphores, Mutexes, Monitors
- Topic 2.3: Deadlocks: Coffman Conditions, Deadlock Detection, Banker's Algorithm for Avoidance

MODULE 3: MEMORY MANAGEMENT & VIRTUAL MEMORY
- Topic 3.1: Logical vs Physical Addressing, Contiguous Allocation, Fragmentation
- Topic 3.2: Paging Architecture, Page Tables, Translation Lookaside Buffer (TLB)
- Topic 3.3: Virtual Memory, Demand Paging, Page Fault Handling, Page Replacement Algorithms (FIFO, LRU, Optimal)
- Topic 3.4: Thrashing, Working Set Model

MODULE 4: STORAGE & FILE SYSTEM IMPLEMENTATION
- Topic 4.1: File Attributes, Directory Structures, Inodes
- Topic 4.2: File Allocation Methods: Contiguous, Linked, Indexed Allocation
- Topic 4.3: Secondary Storage Management, Disk Scheduling Algorithms (FCFS, SSTF, SCAN, C-SCAN)
"""

PROCESSES_NOTES_CONTENT = """
CS301 STUDY NOTES - CHAPTER 1: PROCESS MANAGEMENT & SCHEDULING
Filename: OS_Chapter1_Processes_and_Threads.txt

[Page 1]
1.1 Process Lifecycle & Control Structures
A process is a program in execution. It represents the fundamental unit of work in a modern time-sharing operating system.
A process's state changes during its execution:
- NEW: The process is being created.
- READY: The process is waiting to be assigned to a CPU core.
- RUNNING: Instructions are being executed on the CPU core.
- WAITING (or BLOCKED): The process is waiting for some event (such as I/O completion or signal).
- TERMINATED: The process has finished execution.

The Process Control Block (PCB), also called a Task Control Block, stores all vital information associated with a specific process:
- Process Identifier (PID)
- Process State (Ready, Running, Waiting, etc.)
- Program Counter (PC): Contains the address of the next machine instruction to execute.
- CPU Registers: Accumulators, index registers, stack pointers, general-purpose registers.
- CPU-Scheduling Information: Priorities, scheduling queue pointers.
- Memory-Management Information: Page tables or segment tables.
- Accounting & I/O Status Information: Amount of CPU used, list of open file descriptors.

[Page 2]
1.2 Context Switching Overhead & Mechanics
Switching the CPU core to another process requires performing a state save of the current process and a state restore of a different process. This task is known as a Context Switch.
When a context switch occurs, the kernel saves the context of the running process in its PCB and loads the saved context of the new process scheduled to run.
Context switch time is pure overhead because the system does no useful work while switching. Speed varies from machine to machine, typically ranging from a few microseconds to several tens of microseconds, depending on memory speed, the number of registers, and the presence of special instructions (such as a single instruction to save all registers).

[Page 3]
1.3 CPU Scheduling Algorithms
CPU scheduling is the basis of multi-programmed operating systems. By switching the CPU among processes, the OS makes the computer more productive.
1. First-Come, First-Served (FCFS): The process that requests the CPU first is allocated the CPU first. Non-preemptive. Suffers severely from the Convoy Effect, where small processes wait behind a long CPU-burst process.
2. Shortest-Job-First (SJF): Associates with each process the length of its next CPU burst. SJF is provably optimal in terms of minimizing average waiting time. However, predicting the future CPU burst length requires exponential smoothing.
3. Round Robin (RR): Designed specifically for time-sharing systems. A small unit of time called a Time Quantum (or time slice), typically 10 to 100 milliseconds, is defined. If the time quantum is extremely large, RR degenerates into FCFS. If it is too small, context switch overhead dominates system performance.
"""

MEMORY_NOTES_CONTENT = """
CS301 STUDY NOTES - CHAPTER 2: MEMORY MANAGEMENT & VIRTUAL MEMORY
Filename: OS_Chapter2_Memory_Management_and_Paging.txt

[Page 1]
2.1 Address Binding & Paging Architecture
Memory consists of a large array of bytes, each with its own physical address. The CPU fetches instructions from memory according to the value of the Program Counter.
Physical address spaces are decoupled from logical address spaces through Paging.
Paging is a memory-management scheme that permits a process's physical address space to be non-contiguous.
- Physical memory is broken into fixed-sized blocks called Frames.
- Logical memory is broken into blocks of the same size called Pages.
Every address generated by the CPU is divided into two parts: a Page Number (p) and a Page Offset (d).
The page number is used as an index into a per-process Page Table. The page table entry contains the base address of the frame in physical memory.

[Page 2]
2.2 The Translation Lookaside Buffer (TLB)
Because page tables are stored in main memory, accessing a memory location requires two memory accesses: one for the page-table entry and one for the actual byte. This 50% slowdown is resolved using a fast hardware cache called the Translation Lookaside Buffer (TLB).
The TLB is associative, high-speed memory. Each TLB entry consists of a key (tag) and a value.
- If the page number is found in the TLB (TLB Hit), the frame number is immediately available without accessing main memory.
- If the page number is not found (TLB Miss), a memory reference to the page table must be made.
Effective Access Time (EAT) = (Hit_Ratio * (TLB_Search_Time + Memory_Access_Time)) + ((1 - Hit_Ratio) * (TLB_Search_Time + 2 * Memory_Access_Time)).

[Page 3]
2.3 Virtual Memory, Demand Paging & Thrashing
Virtual memory involves the separation of user logical memory from physical memory. This separation allows an extremely large virtual memory to be provided for programmers when only a smaller physical memory is available.
Demand Paging brings pages into memory only when they are needed during execution.
A Page Fault occurs when an instruction references a page that is marked invalid (not currently loaded in RAM).
When a page fault happens:
1. Trap to the OS kernel.
2. Save user registers and process state.
3. Determine that the reference was a valid page on secondary backing store.
4. Issue a read from disk to a free physical memory frame.
5. While waiting, CPU may be allocated to another process.
6. When I/O completes, update internal page table (mark valid bit = 1).
7. Restore user registers and restart the faulting instruction.

Thrashing occurs when a process spends more time paging (swapping pages in and out of disk) than executing code. If the sum of sizes of the working sets exceeds total physical memory, thrashing is inevitable and CPU utilization drops to near zero.
"""

CONCURRENCY_NOTES_CONTENT = """
CS301 STUDY NOTES - CHAPTER 3: CONCURRENCY, SYNCHRONIZATION & DEADLOCKS
Filename: OS_Chapter3_Concurrency_and_Deadlocks.txt

[Page 1]
3.1 The Critical Section Problem & Race Conditions
A race condition occurs when multiple processes or threads read and write shared data concurrently, and the final outcome depends on the order of execution.
To prevent race conditions, concurrent processes must be synchronized.
The Critical Section is a segment of code in which the process accesses shared resources.
Any valid solution to the critical-section problem must satisfy three strict requirements:
1. Mutual Exclusion: If process P is executing in its critical section, then no other processes can be executing in their critical sections.
2. Progress: If no process is executing in its critical section and some processes wish to enter, only those processes not in their remainder sections can participate in deciding who enters next.
3. Bounded Waiting: There must be a bound on the number of times that other processes are allowed to enter their critical sections after a process has made a request to enter.

[Page 2]
3.2 Semaphores and Mutex Locks
A Mutex (mutual exclusion) lock is the simplest synchronization tool. A process acquires the lock before entering a critical section and releases it upon exit.
A Semaphore is an integer variable that, apart from initialization, is accessed only through two standard atomic operations: wait() (historically called P) and signal() (historically called V).
- Counting Semaphore: Value can range over an unrestricted domain. Used to control access to a given resource consisting of a finite number of instances.
- Binary Semaphore: Value can range only between 0 and 1. Behaves identically to a mutex lock.
A major danger in using semaphores is Deadlock, where two or more processes are waiting indefinitely for an event that can be caused only by one of the waiting processes.

[Page 3]
3.3 Deadlock Conditions & Banker's Algorithm
A deadlock situation can arise if and only if all four Coffman conditions hold simultaneously:
1. Mutual Exclusion: At least one resource must be held in a non-shareable mode.
2. Hold and Wait: A process must be concurrently holding at least one resource and waiting to acquire additional resources held by other processes.
3. No Preemption: Resources cannot be preempted; a resource can be released only voluntarily by the process holding it.
4. Circular Wait: A set {P0, P1, ..., Pn} of waiting processes must exist such that P0 is waiting for a resource held by P1, P1 is waiting for P2, and Pn is waiting for P0.

Banker's Algorithm: An avoidance algorithm for systems with multiple instances of each resource type. It dynamically checks the resource-allocation state to ensure that a Circular Wait condition can never exist by testing for a Safe State.
"""

STORAGE_NOTES_CONTENT = """
CS301 STUDY NOTES - CHAPTER 4: STORAGE & FILE SYSTEM ARCHITECTURE
Filename: OS_Chapter4_Storage_and_FileSystems.txt

[Page 1]
4.1 File Systems & Inodes
A file is an abstract data type representing a contiguous logical address space.
In Unix/Linux file systems, metadata for each file is encapsulated in an Inode (index node).
An Inode contains:
- File ownership, file mode (permissions), file size, timestamps (access, modification, change).
- Direct block pointers pointing directly to disk data blocks.
- Single indirect, double indirect, and triple indirect pointers to accommodate huge files.

[Page 2]
4.2 Disk Scheduling Algorithms
Magnetic disks provide bulk secondary storage. Disk access time consists of Seek Time (time to move disk arm to target cylinder), Rotational Latency (time for sector to rotate under head), and Transfer Time.
1. FCFS: Serves requests in arrival order. Fair, but does not optimize head movement.
2. Shortest Seek Time First (SSTF): Selects the request with the minimum seek time from current head position. May cause starvation for distant requests.
3. SCAN (Elevator Algorithm): Disk arm moves in one direction servicing requests until it reaches the end of the disk, then reverses direction.
4. C-SCAN (Circular SCAN): Moves in one direction, but upon reaching the end, immediately returns to the beginning without servicing requests on the return trip, providing a more uniform wait time.
"""

PAST_EXAMS_CONTENT = """
PAST EXAMINATION QUESTIONS (2022 - 2024 COMPILATION)
Filename: OS_Past_Exams_2022_2024.txt

[Question 1] (Final Exam 2024)
Topic: Memory Management & Virtual Memory
Calculate the Effective Access Time (EAT) for a demand-paged system with a memory access time of 100ns and page fault service time of 8ms. If hit ratio of TLB is 95%, evaluate the maximum acceptable page fault rate.

[Question 2] (Midterm 2024)
Topic: Memory Management & Virtual Memory
Explain the mechanics of page fault handling step-by-step from instruction trap to instruction restart. Distinguish between a page fault and a TLB miss.

[Question 3] (Final Exam 2023)
Topic: Memory Management & Virtual Memory
What is thrashing? How does the operating system detect thrashing, and how does the working set model prevent severe drops in CPU utilization?

[Question 4] (Final Exam 2023)
Topic: Memory Management & Virtual Memory
Compare FIFO, LRU, and Optimal page replacement algorithms given the page reference string: 7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2 with 3 physical frames.

[Question 5] (Final Exam 2022)
Topic: Memory Management & Virtual Memory
Describe the structure and purpose of the Translation Lookaside Buffer (TLB). Why are two memory accesses required without a TLB?

[Question 6] (Midterm 2023)
Topic: Concurrency, Synchronization & Deadlocks
State the four Coffman conditions necessary for deadlock to occur. Show how breaking the Hold and Wait condition prevents deadlock.

[Question 7] (Final Exam 2024)
Topic: Concurrency, Synchronization & Deadlocks
Apply the Banker's Algorithm to determine if the following system state is safe: 5 processes (P0-P4) and 3 resource types (A, B, C).

[Question 8] (Midterm 2024)
Topic: Concurrency, Synchronization & Deadlocks
Implement a bounded-buffer producer-consumer solution using counting semaphores and a mutex lock. What happens if the order of wait() calls is reversed?

[Question 9] (Final Exam 2023)
Topic: Process Management & CPU Scheduling
Given 4 processes with arrival times [0, 1, 2, 3] and CPU bursts [8, 4, 9, 5], calculate average turnaround and waiting times under Round Robin scheduling (quantum = 4).

[Question 10] (Midterm 2023)
Topic: Process Management & CPU Scheduling
Explain what information is stored in the Process Control Block (PCB). Why is context switching considered pure system overhead?

[Question 11] (Final Exam 2022)
Topic: Storage & File Systems
Compare FCFS, SSTF, and SCAN disk scheduling algorithms for a disk with 200 cylinders given request queue: 98, 183, 37, 122, 14, 124, 65, 67 with initial head position at 53.
"""


def seed_demo_data():
    init_db()
    db = SessionLocal()

    print("Checking / seeding demo user: student@demo.com...")
    user = db.query(User).filter(User.email == "student@demo.com").first()
    if not user:
        user = User(
            email="student@demo.com",
            name="Alex Student (Demo)",
            password="demo123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user_id = user.id
    print(f"Demo user confirmed with ID: {user_id}")

    # Write files to storage
    file_specs = [
        ("OS_Course_Syllabus.txt", "syllabus", SYLLABUS_CONTENT),
        ("OS_Chapter1_Processes_and_Threads.txt", "notes", PROCESSES_NOTES_CONTENT),
        ("OS_Chapter2_Memory_Management_and_Paging.txt", "notes", MEMORY_NOTES_CONTENT),
        ("OS_Chapter3_Concurrency_and_Deadlocks.txt", "notes", CONCURRENCY_NOTES_CONTENT),
        ("OS_Chapter4_Storage_and_FileSystems.txt", "notes", STORAGE_NOTES_CONTENT),
        ("OS_Past_Exams_2022_2024.txt", "past_paper", PAST_EXAMS_CONTENT)
    ]

    for fname, dtype, content in file_specs:
        fpath = os.path.join(STORAGE_UPLOADS_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content.strip())

        # Check if already in documents table
        doc_record = db.query(Document).filter(
            Document.user_id == user_id,
            Document.filename == fname
        ).first()

        ingest_res = process_and_ingest_file(fpath, fname, dtype, user_id)

        if not doc_record:
            doc_record = Document(
                user_id=user_id,
                filename=fname,
                doc_type=dtype,
                file_path=fpath,
                page_count=ingest_res["page_count"],
                chunk_count=ingest_res["chunk_count"],
                uploaded_at=datetime.utcnow()
            )
            db.add(doc_record)
        else:
            doc_record.page_count = ingest_res["page_count"]
            doc_record.chunk_count = ingest_res["chunk_count"]
        db.commit()

    print("Documents ingested and indexed into vector store.")

    # Seed Topics Hierarchy with Exam Frequencies
    topics_data = [
        {
            "name": "Memory Management & Virtual Memory",
            "desc": "Paging architecture, TLB caching, Page Replacement Algorithms (LRU/FIFO), Virtual Memory & Thrashing",
            "exam_frequency": 5,
            "weightage": "High",
            "subtopics": [
                "Paging & Page Tables",
                "Translation Lookaside Buffer (TLB)",
                "Demand Paging & Page Faults",
                "Thrashing & Working Set Model"
            ]
        },
        {
            "name": "Concurrency, Synchronization & Deadlocks",
            "desc": "Critical Section Problem, Race Conditions, Semaphores, Mutexes, Coffman Conditions, Banker's Algorithm",
            "exam_frequency": 3,
            "weightage": "High",
            "subtopics": [
                "Critical Section & Race Conditions",
                "Semaphores & Mutex Locks",
                "Deadlock Coffman Conditions",
                "Banker's Algorithm Avoidance"
            ]
        },
        {
            "name": "Process Management & CPU Scheduling",
            "desc": "Process states, Process Control Block (PCB), Context Switching overhead, FCFS, SJF, Round Robin scheduling",
            "exam_frequency": 2,
            "weightage": "Medium",
            "subtopics": [
                "Process Lifecycle & PCB",
                "Context Switching Mechanics",
                "CPU Scheduling Algorithms"
            ]
        },
        {
            "name": "Storage & File System Architecture",
            "desc": "File concepts, Unix Inodes, Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN)",
            "exam_frequency": 1,
            "weightage": "Low",
            "subtopics": [
                "File Systems & Inodes",
                "Disk Scheduling Algorithms"
            ]
        }
    ]

    db_topics_map = {}
    for td in topics_data:
        t_record = db.query(Topic).filter(
            Topic.user_id == user_id,
            Topic.name == td["name"]
        ).first()

        if not t_record:
            t_record = Topic(
                user_id=user_id,
                name=td["name"],
                description=td["desc"],
                exam_frequency=td["exam_frequency"],
                weightage_level=td["weightage"]
            )
            db.add(t_record)
            db.commit()
            db.refresh(t_record)

        db_topics_map[td["name"]] = t_record

        # Seed subtopics
        for st_name in td["subtopics"]:
            st_rec = db.query(Topic).filter(
                Topic.user_id == user_id,
                Topic.name == st_name
            ).first()
            if not st_rec:
                st_rec = Topic(
                    user_id=user_id,
                    name=st_name,
                    parent_topic_id=t_record.id,
                    description=f"Subtopic under {td['name']}",
                    exam_frequency=max(0, td["exam_frequency"] - 1),
                    weightage_level=td["weightage"]
                )
                db.add(st_rec)
                db.commit()

    print("Topics and Subtopics hierarchy created.")

    # Seed baseline diagnostic quiz attempts to produce an authentic Gap Report
    # Check if attempts already exist
    existing_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count()
    if existing_attempts == 0:
        print("Seeding baseline diagnostic quiz attempts...")

        # 1. Attempt on Memory Management (Weak: 1/3 correct = 33.3%)
        mem_topic = db_topics_map["Memory Management & Virtual Memory"]
        att1 = QuizAttempt(
            user_id=user_id,
            topic_id=mem_topic.id,
            score=1,
            total_questions=3,
            accuracy_pct=33.3,
            status="Weak",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(att1)
        db.commit()
        db.refresh(att1)

        q1 = QuizQuestion(
            quiz_attempt_id=att1.id,
            question_text="What is the primary function of the Translation Lookaside Buffer (TLB)?",
            options_json=json.dumps([
                {"id": "A", "text": "Hardware cache to accelerate page-table translation and avoid second memory reference"},
                {"id": "B", "text": "Stores dirty frames waiting for disk write-back"},
                {"id": "C", "text": "Acts as the secondary swap space on NVMe storage"},
                {"id": "D", "text": "Resolves race conditions during concurrent CPU bursts"}
            ]),
            correct_answer="A",
            student_answer="A",
            is_correct=True,
            explanation="Grounded in OS_Chapter2_Memory_Management_and_Paging.txt, Page 2: The TLB is an associative high-speed cache that maps page numbers to frame numbers without requiring a main memory page table lookup.",
            citation="OS_Chapter2_Memory_Management_and_Paging.txt, Page 2"
        )
        q2 = QuizQuestion(
            quiz_attempt_id=att1.id,
            question_text="During demand paging, what exact hardware event initiates the operating system page fault handler?",
            options_json=json.dumps([
                {"id": "A", "text": "A CPU clock interrupt occurring every 10ms"},
                {"id": "B", "text": "An instruction referencing a page table entry marked with an invalid bit"},
                {"id": "C", "text": "The TLB hit ratio exceeding 98%"},
                {"id": "D", "text": "The operating system running out of disk swap blocks"}
            ]),
            correct_answer="B",
            student_answer="A",  # Student missed this!
            is_correct=False,
            explanation="Grounded in OS_Chapter2_Memory_Management_and_Paging.txt, Page 3: A page fault occurs when an instruction references a page marked invalid in the page table, generating a trap to the OS kernel.",
            citation="OS_Chapter2_Memory_Management_and_Paging.txt, Page 3"
        )
        q3 = QuizQuestion(
            quiz_attempt_id=att1.id,
            question_text="Under what condition does thrashing occur in virtual memory systems?",
            options_json=json.dumps([
                {"id": "A", "text": "When page tables are loaded directly into L1 CPU cache"},
                {"id": "B", "text": "When the sum of working set sizes across active processes exceeds available physical memory frames"},
                {"id": "C", "text": "When the CPU burst time is shorter than the time quantum in Round Robin"},
                {"id": "D", "text": "When direct block pointers in an Inode exceed 12 entries"}
            ]),
            correct_answer="B",
            student_answer="C",  # Student missed this!
            is_correct=False,
            explanation="Grounded in OS_Chapter2_Memory_Management_and_Paging.txt, Page 3: Thrashing occurs when processes spend more time paging in and out of backing store than executing code, triggered when aggregate working sets exceed RAM frames.",
            citation="OS_Chapter2_Memory_Management_and_Paging.txt, Page 3"
        )
        db.add_all([q1, q2, q3])
        db.commit()

        # 2. Attempt on Process Management (Medium: 2/3 correct = 66.7%)
        proc_topic = db_topics_map["Process Management & CPU Scheduling"]
        att2 = QuizAttempt(
            user_id=user_id,
            topic_id=proc_topic.id,
            score=2,
            total_questions=3,
            accuracy_pct=66.7,
            status="Medium",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(att2)
        db.commit()
        db.refresh(att2)

        pq1 = QuizQuestion(
            quiz_attempt_id=att2.id,
            question_text="Why is context switching described as pure system overhead?",
            options_json=json.dumps([
                {"id": "A", "text": "Because the system does no useful computational work while saving and restoring process state"},
                {"id": "B", "text": "Because it permanently overwrites the program counter with null values"},
                {"id": "C", "text": "Because it halts disk spindle rotation during I/O"},
                {"id": "D", "text": "Because it doubles the size of the process page table in memory"}
            ]),
            correct_answer="A",
            student_answer="A",
            is_correct=True,
            explanation="Grounded in OS_Chapter1_Processes_and_Threads.txt, Page 2: Context switch time is pure overhead because the system executes no user work while performing state save and restore.",
            citation="OS_Chapter1_Processes_and_Threads.txt, Page 2"
        )
        pq2 = QuizQuestion(
            quiz_attempt_id=att2.id,
            question_text="Which CPU scheduling algorithm is mathematically provable to yield the minimum average waiting time?",
            options_json=json.dumps([
                {"id": "A", "text": "First-Come, First-Served (FCFS)"},
                {"id": "B", "text": "Shortest-Job-First (SJF)"},
                {"id": "C", "text": "Round Robin (RR) with large quantum"},
                {"id": "D", "text": "SCAN elevator scheduling"}
            ]),
            correct_answer="B",
            student_answer="B",
            is_correct=True,
            explanation="Grounded in OS_Chapter1_Processes_and_Threads.txt, Page 3: SJF is provably optimal for minimizing average waiting time for a given set of processes.",
            citation="OS_Chapter1_Processes_and_Threads.txt, Page 3"
        )
        pq3 = QuizQuestion(
            quiz_attempt_id=att2.id,
            question_text="What detrimental condition occurs in FCFS scheduling when short processes queue behind a long process?",
            options_json=json.dumps([
                {"id": "A", "text": "Convoy Effect"},
                {"id": "B", "text": "Thrashing Cycle"},
                {"id": "C", "text": "Deadlock Inversion"},
                {"id": "D", "text": "TLB Degeneration"}
            ]),
            correct_answer="A",
            student_answer="C",  # Student missed this!
            is_correct=False,
            explanation="Grounded in OS_Chapter1_Processes_and_Threads.txt, Page 3: FCFS suffers from the Convoy Effect, where small processes wait behind a heavy CPU-burst process.",
            citation="OS_Chapter1_Processes_and_Threads.txt, Page 3"
        )
        db.add_all([pq1, pq2, pq3])
        db.commit()

        # 3. Attempt on Storage (Strong: 3/3 correct = 100%)
        stor_topic = db_topics_map["Storage & File System Architecture"]
        att3 = QuizAttempt(
            user_id=user_id,
            topic_id=stor_topic.id,
            score=3,
            total_questions=3,
            accuracy_pct=100.0,
            status="Strong",
            created_at=datetime.utcnow() - timedelta(hours=6)
        )
        db.add(att3)
        db.commit()
        db.refresh(att3)

        sq1 = QuizQuestion(
            quiz_attempt_id=att3.id,
            question_text="What primary component stores metadata including permissions, timestamps, and block pointers in Unix file systems?",
            options_json=json.dumps([
                {"id": "A", "text": "The Inode (index node)"},
                {"id": "B", "text": "The Translation Lookaside Buffer"},
                {"id": "C", "text": "The Process Control Block"},
                {"id": "D", "text": "The Banker's Allocation Matrix"}
            ]),
            correct_answer="A",
            student_answer="A",
            is_correct=True,
            explanation="Grounded in OS_Chapter4_Storage_and_FileSystems.txt, Page 1: File metadata in Unix/Linux is encapsulated in an Inode.",
            citation="OS_Chapter4_Storage_and_FileSystems.txt, Page 1"
        )
        db.add(sq1)
        db.commit()

        # Seed initial revision plan
        print("Building baseline adaptive revision plan...")
        all_topics = db.query(Topic).filter(Topic.user_id == user_id, Topic.parent_topic_id.is_(None)).all()
        plan_topic_list = []
        for t in all_topics:
            latest_att = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.topic_id == t.id
            ).order_by(QuizAttempt.created_at.desc()).first()

            acc = (latest_att.accuracy_pct / 100.0) if latest_att else 0.0
            status = latest_att.status if latest_att else ("Weak" if t.exam_frequency >= 3 else "Medium")
            priority = round((1.0 - acc) * (1.0 + t.exam_frequency * 0.2), 2)

            plan_topic_list.append({
                "id": t.id,
                "name": t.name,
                "status": status,
                "weightage_level": t.weightage_level,
                "exam_frequency": t.exam_frequency,
                "priority_score": priority
            })

        schedule = build_adaptive_revision_plan(plan_topic_list, target_days=5, daily_hours=2.0)
        plan_rec = RevisionPlan(
            user_id=user_id,
            target_days=5,
            daily_hours=2.0,
            plan_json=json.dumps(schedule)
        )
        db.add(plan_rec)
        db.commit()

    db.close()
    print("Seed demo data process completed successfully!")


if __name__ == "__main__":
    seed_demo_data()
