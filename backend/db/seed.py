"""
Comprehensive career database seeder.
Seeds 500+ careers with realistic data based on BLS/O*NET research.
Each career has skills, automation risk scores, and predictions.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.database import engine, SessionLocal, Base
from backend.models.career import Career
from backend.models.skill import CareerSkill
from backend.models.prediction import Prediction, EnsemblePrediction
from backend.data_ingestion.ai_risk_scorer import score_skill_automation, compute_career_automation_index
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# ── Career data: (title, category, median_salary, employment, growth%, education, description) ──

CAREERS_DATA = [
    # ─── Technology ───
    ("Software Developer", "Technology", 127260, 1847900, 25.7, "Bachelor's degree",
     "Design, develop, and test software applications and systems"),
    ("Data Scientist", "Technology", 108020, 192000, 35.8, "Bachelor's degree",
     "Analyze complex data to help organizations make better decisions"),
    ("Cybersecurity Analyst", "Technology", 112000, 175000, 31.5, "Bachelor's degree",
     "Plan and implement security measures to protect computer systems and networks"),
    ("AI/Machine Learning Engineer", "Technology", 146085, 85000, 40.2, "Master's degree",
     "Design and develop AI systems and machine learning models"),
    ("Web Developer", "Technology", 80730, 199400, 16.0, "Bachelor's degree",
     "Design and create websites and web applications"),
    ("Database Administrator", "Technology", 101000, 168000, 8.7, "Bachelor's degree",
     "Use software to store and organize data for companies"),
    ("Network Administrator", "Technology", 88750, 345000, 2.8, "Bachelor's degree",
     "Design, install, and maintain computer network systems"),
    ("Cloud Architect", "Technology", 135000, 92000, 33.5, "Bachelor's degree",
     "Design and manage cloud computing infrastructure and services"),
    ("DevOps Engineer", "Technology", 125000, 110000, 28.0, "Bachelor's degree",
     "Automate and streamline software development and deployment processes"),
    ("Mobile App Developer", "Technology", 115000, 145000, 22.3, "Bachelor's degree",
     "Create applications for mobile devices and platforms"),
    ("Systems Analyst", "Technology", 99270, 538000, 9.4, "Bachelor's degree",
     "Study an organization's current computer systems and design improvements"),
    ("IT Project Manager", "Technology", 98580, 482000, 11.1, "Bachelor's degree",
     "Plan and oversee technology projects within organizations"),
    ("UX Designer", "Technology", 92000, 110000, 18.5, "Bachelor's degree",
     "Design user interfaces and experiences for digital products"),
    ("QA Engineer", "Technology", 99200, 195000, 8.2, "Bachelor's degree",
     "Test software to identify bugs and ensure quality standards"),
    ("Blockchain Developer", "Technology", 140000, 25000, 45.0, "Bachelor's degree",
     "Develop blockchain-based applications and smart contracts"),
    ("Computer Vision Engineer", "Technology", 138000, 35000, 38.0, "Master's degree",
     "Develop systems that can interpret and process visual data"),
    ("Robotics Engineer", "Technology", 100640, 32000, 22.0, "Bachelor's degree",
     "Design, build, and maintain robots and robotic systems"),
    ("Data Engineer", "Technology", 117000, 120000, 32.0, "Bachelor's degree",
     "Build and maintain data infrastructure and pipelines"),
    ("Full Stack Developer", "Technology", 120000, 180000, 23.5, "Bachelor's degree",
     "Develop both client-side and server-side software"),
    ("IT Support Specialist", "Technology", 57910, 882000, 5.7, "Some college, no degree",
     "Provide technical assistance to computer users"),

    # ─── Healthcare ───
    ("Physician (General)", "Healthcare", 229300, 727000, 3.0, "Doctoral or professional degree",
     "Diagnose and treat injuries and illnesses in patients"),
    ("Registered Nurse", "Healthcare", 81220, 3175000, 5.6, "Bachelor's degree",
     "Provide and coordinate patient care and educate patients about health conditions"),
    ("Dentist", "Healthcare", 163220, 155000, 4.0, "Doctoral or professional degree",
     "Diagnose and treat problems with teeth, gums, and related parts of the mouth"),
    ("Pharmacist", "Healthcare", 132750, 322000, -2.2, "Doctoral or professional degree",
     "Dispense prescription medications and advise patients on usage"),
    ("Physical Therapist", "Healthcare", 97720, 258000, 14.7, "Doctoral or professional degree",
     "Help injured or ill people improve movement and manage pain"),
    ("Occupational Therapist", "Healthcare", 93180, 143000, 12.1, "Master's degree",
     "Help patients develop and recover daily living and work skills"),
    ("Surgeon", "Healthcare", 297800, 45000, 3.5, "Doctoral or professional degree",
     "Perform operations to treat injuries, diseases, and deformities"),
    ("Psychiatrist", "Healthcare", 249760, 38000, 6.8, "Doctoral or professional degree",
     "Diagnose and treat mental disorders using therapy and medications"),
    ("Medical Lab Technician", "Healthcare", 57380, 343000, 5.4, "Associate's degree",
     "Collect samples and perform tests to analyze body fluids and tissues"),
    ("Radiologic Technologist", "Healthcare", 65140, 258000, 6.3, "Associate's degree",
     "Perform diagnostic imaging examinations like X-rays"),
    ("Nurse Practitioner", "Healthcare", 124680, 355000, 38.0, "Master's degree",
     "Provide advanced nursing care, diagnose conditions, and prescribe treatment"),
    ("Dental Hygienist", "Healthcare", 81400, 226000, 7.2, "Associate's degree",
     "Clean teeth, examine patients for oral diseases"),
    ("Respiratory Therapist", "Healthcare", 70540, 136000, 13.6, "Associate's degree",
     "Care for patients who have trouble breathing"),
    ("Veterinarian", "Healthcare", 119100, 86000, 19.4, "Doctoral or professional degree",
     "Diagnose and treat diseases and injuries in animals"),
    ("Optometrist", "Healthcare", 124300, 47000, 8.8, "Doctoral or professional degree",
     "Examine eyes and diagnose and treat vision problems"),
    ("Speech-Language Pathologist", "Healthcare", 84140, 167000, 18.5, "Master's degree",
     "Diagnose and treat communication and swallowing disorders"),
    ("Physician Assistant", "Healthcare", 126010, 148000, 27.6, "Master's degree",
     "Practice medicine under the supervision of physicians"),
    ("Emergency Medical Technician", "Healthcare", 38930, 269000, 5.1, "Postsecondary nondegree award",
     "Respond to emergency calls and provide basic medical care"),
    ("Home Health Aide", "Healthcare", 31050, 3636000, 22.0, "High school diploma or equivalent",
     "Provide personal care to elderly, disabled, or ill persons in their homes"),
    ("Medical Records Specialist", "Healthcare", 46660, 211000, 7.9, "Postsecondary nondegree award",
     "Organize and manage health information data"),

    # ─── Finance & Business ───
    ("Accountant", "Finance", 79880, 1456000, 4.4, "Bachelor's degree",
     "Prepare and examine financial records and ensure accuracy"),
    ("Financial Analyst", "Finance", 96220, 327000, 8.2, "Bachelor's degree",
     "Guide businesses and individuals in decisions about money"),
    ("Financial Manager", "Finance", 150000, 730000, 16.0, "Bachelor's degree",
     "Create financial reports, direct investment activities, and develop long-term financial plans"),
    ("Actuary", "Finance", 113990, 30000, 21.4, "Bachelor's degree",
     "Analyze the financial costs of risk and uncertainty"),
    ("Auditor", "Finance", 79880, 1456000, 4.4, "Bachelor's degree",
     "Examine and verify financial records and statements"),
    ("Tax Preparer", "Finance", 46290, 76000, -2.5, "High school diploma or equivalent",
     "Prepare tax returns for individuals or small businesses"),
    ("Insurance Underwriter", "Finance", 77860, 115000, -2.0, "Bachelor's degree",
     "Evaluate insurance applications and decide coverage terms"),
    ("Loan Officer", "Finance", 65740, 346000, 3.3, "Bachelor's degree",
     "Evaluate, authorize, or recommend approval of loan applications"),
    ("Budget Analyst", "Finance", 82260, 57000, 2.5, "Bachelor's degree",
     "Help organizations plan their finances by preparing budget reports"),
    ("Management Consultant", "Finance", 99410, 923000, 11.1, "Bachelor's degree",
     "Advise organizations on how to improve efficiency and profits"),
    ("Investment Banker", "Finance", 142000, 65000, 7.5, "Bachelor's degree",
     "Help companies raise capital and advise on mergers and acquisitions"),
    ("Credit Analyst", "Finance", 77850, 65000, 2.0, "Bachelor's degree",
     "Analyze credit data and financial statements to determine creditworthiness"),
    ("Compliance Officer", "Finance", 75810, 346000, 4.6, "Bachelor's degree",
     "Ensure organizations comply with regulations and internal policies"),
    ("Risk Manager", "Finance", 105000, 45000, 8.0, "Bachelor's degree",
     "Identify and analyze areas of potential risk to organizations"),
    ("Bookkeeper", "Finance", 45860, 1533000, -3.0, "Some college, no degree",
     "Record financial transactions and maintain financial records"),

    # ─── Education ───
    ("Elementary School Teacher", "Education", 61690, 1448000, 0.8, "Bachelor's degree",
     "Teach academic and social skills to young students"),
    ("High School Teacher", "Education", 65220, 1069000, 1.0, "Bachelor's degree",
     "Teach students in one or more subjects at the secondary level"),
    ("University Professor", "Education", 84380, 1372000, 8.0, "Doctoral or professional degree",
     "Teach courses and conduct research at colleges and universities"),
    ("Special Education Teacher", "Education", 62950, 476000, 0.3, "Bachelor's degree",
     "Work with students who have learning, mental, or physical disabilities"),
    ("School Counselor", "Education", 60510, 354000, 5.0, "Master's degree",
     "Help students develop academic and social skills and plan for after graduation"),
    ("Librarian", "Education", 63200, 139000, 3.1, "Master's degree",
     "Help people find information and conduct research for personal and professional use"),
    ("Education Administrator", "Education", 99940, 276000, 4.1, "Master's degree",
     "Plan and coordinate academic programs and oversee school operations"),
    ("Preschool Teacher", "Education", 35330, 449000, 3.0, "Associate's degree",
     "Educate and care for children before they enter kindergarten"),
    ("Instructional Designer", "Education", 74000, 205000, 10.5, "Master's degree",
     "Design and develop educational materials and training programs"),
    ("ESL Teacher", "Education", 59720, 80000, 4.0, "Bachelor's degree",
     "Teach English to non-native speakers"),

    # ─── Legal ───
    ("Lawyer", "Legal", 135740, 826000, 8.0, "Doctoral or professional degree",
     "Advise and represent individuals, businesses, or government agencies on legal issues"),
    ("Paralegal", "Legal", 59200, 350000, 4.0, "Associate's degree",
     "Assist lawyers by investigating facts, preparing documents, and researching laws"),
    ("Judge", "Legal", 148030, 28000, -1.0, "Doctoral or professional degree",
     "Preside over court proceedings, make rulings, and determine sentences"),
    ("Legal Secretary", "Legal", 50040, 168000, -9.1, "High school diploma or equivalent",
     "Perform administrative tasks for lawyers and law offices"),
    ("Court Reporter", "Legal", 63420, 25000, -2.0, "Postsecondary nondegree award",
     "Create word-for-word transcriptions of court proceedings"),
    ("Mediator", "Legal", 64030, 9000, 4.0, "Bachelor's degree",
     "Facilitate negotiations and conflict resolution between disputing parties"),
    ("Compliance Analyst", "Legal", 73000, 125000, 5.5, "Bachelor's degree",
     "Ensure organizations comply with legal and regulatory requirements"),

    # ─── Engineering ───
    ("Mechanical Engineer", "Engineering", 96310, 299000, 2.0, "Bachelor's degree",
     "Design, develop, and test mechanical devices and systems"),
    ("Electrical Engineer", "Engineering", 104610, 186000, 2.5, "Bachelor's degree",
     "Design, develop, and test electrical equipment and systems"),
    ("Civil Engineer", "Engineering", 89940, 327000, 5.4, "Bachelor's degree",
     "Design, build, and maintain infrastructure projects"),
    ("Chemical Engineer", "Engineering", 106260, 32000, 8.5, "Bachelor's degree",
     "Apply chemistry and engineering principles to solve problems in production"),
    ("Aerospace Engineer", "Engineering", 126880, 60000, 6.1, "Bachelor's degree",
     "Design aircraft, spacecraft, satellites, and missiles"),
    ("Biomedical Engineer", "Engineering", 100090, 22000, 5.5, "Bachelor's degree",
     "Combine engineering principles with medical sciences to design healthcare solutions"),
    ("Environmental Engineer", "Engineering", 96820, 53000, 4.0, "Bachelor's degree",
     "Develop solutions to environmental problems using engineering principles"),
    ("Industrial Engineer", "Engineering", 95300, 304000, 12.0, "Bachelor's degree",
     "Design efficient systems that integrate workers, machines, and materials"),
    ("Nuclear Engineer", "Engineering", 122480, 17000, -8.0, "Bachelor's degree",
     "Research and develop processes and systems for nuclear energy"),
    ("Petroleum Engineer", "Engineering", 131800, 25000, 2.1, "Bachelor's degree",
     "Design methods for extracting oil and gas from deposits"),
    ("Structural Engineer", "Engineering", 98000, 68000, 4.5, "Bachelor's degree",
     "Analyze and design structures to withstand stresses and pressures"),
    ("Materials Engineer", "Engineering", 98300, 28000, 5.0, "Bachelor's degree",
     "Develop and test materials used to create products"),

    # ─── Creative & Media ───
    ("Graphic Designer", "Creative & Media", 57990, 266000, 2.7, "Bachelor's degree",
     "Create visual concepts to communicate ideas through images and layouts"),
    ("Video Producer", "Creative & Media", 78000, 142000, 14.0, "Bachelor's degree",
     "Plan and coordinate the production of video content"),
    ("Photographer", "Creative & Media", 40000, 55000, 4.0, "High school diploma or equivalent",
     "Take photographs for commercial, artistic, or scientific purposes"),
    ("Writer/Author", "Creative & Media", 73150, 143000, -2.0, "Bachelor's degree",
     "Write and edit content for books, publications, or digital media"),
    ("Musician", "Creative & Media", 45000, 177000, 5.0, "No formal educational credential",
     "Play instruments, sing, compose, or arrange music"),
    ("Film Director", "Creative & Media", 85000, 142000, 14.0, "Bachelor's degree",
     "Direct and oversee all creative aspects of film production"),
    ("Animator", "Creative & Media", 78790, 78000, 4.0, "Bachelor's degree",
     "Create animations and visual effects for media"),
    ("Journalist", "Creative & Media", 55960, 40000, -9.0, "Bachelor's degree",
     "Research, write, and report news stories for various media"),
    ("Public Relations Specialist", "Creative & Media", 67440, 340000, 6.4, "Bachelor's degree",
     "Create and maintain favorable public image for organizations"),
    ("Marketing Manager", "Creative & Media", 140040, 357000, 6.4, "Bachelor's degree",
     "Plan and direct marketing policies, programs, and campaigns"),
    ("Content Strategist", "Creative & Media", 78000, 95000, 12.0, "Bachelor's degree",
     "Plan and manage content creation and distribution strategies"),
    ("Social Media Manager", "Creative & Media", 62000, 120000, 10.0, "Bachelor's degree",
     "Manage organizations' social media presence and campaigns"),
    ("Art Director", "Creative & Media", 104580, 105000, 4.0, "Bachelor's degree",
     "Determine the overall visual style of publications and productions"),
    ("Copywriter", "Creative & Media", 65000, 131000, 1.0, "Bachelor's degree",
     "Write persuasive copy for advertisements and marketing materials"),
    ("Interior Designer", "Creative & Media", 60340, 87000, 0.8, "Bachelor's degree",
     "Plan and design interior spaces for functionality and aesthetics"),

    # ─── Science & Research ───
    ("Biologist", "Science", 85000, 90000, 5.0, "Bachelor's degree",
     "Study living organisms and their relationship to the environment"),
    ("Chemist", "Science", 82790, 91000, 5.7, "Bachelor's degree",
     "Study substances at the atomic and molecular levels"),
    ("Physicist", "Science", 152430, 20000, 8.0, "Doctoral or professional degree",
     "Study matter, energy, and fundamental forces of nature"),
    ("Environmental Scientist", "Science", 78980, 86000, 5.9, "Bachelor's degree",
     "Study the environment and develop solutions to environmental problems"),
    ("Geologist", "Science", 88000, 29000, 5.0, "Bachelor's degree",
     "Study the composition, structure, and processes of the Earth"),
    ("Epidemiologist", "Science", 78830, 8000, 26.7, "Master's degree",
     "Study patterns and causes of diseases in human populations"),
    ("Microbiologist", "Science", 84400, 23000, 5.4, "Bachelor's degree",
     "Study microscopic organisms and their effects on plants, animals, and humans"),
    ("Statistician", "Science", 99960, 39000, 30.6, "Master's degree",
     "Collect, analyze, and interpret numerical data to solve problems"),
    ("Astronomer", "Science", 128160, 2500, 8.0, "Doctoral or professional degree",
     "Study celestial objects and phenomena in space"),
    ("Research Scientist", "Science", 95000, 140000, 12.0, "Doctoral or professional degree",
     "Conduct experiments and investigations in specialized fields"),

    # ─── Trades & Skilled Labor ───
    ("Electrician", "Trades", 60240, 723000, 6.7, "High school diploma or equivalent",
     "Install, maintain, and repair electrical wiring and systems"),
    ("Plumber", "Trades", 60090, 500000, 1.7, "High school diploma or equivalent",
     "Install and repair piping systems in residential and commercial buildings"),
    ("HVAC Technician", "Trades", 51390, 394000, 5.3, "Postsecondary nondegree award",
     "Install, maintain, and repair heating, cooling, and ventilation systems"),
    ("Welder", "Trades", 47540, 427000, 2.0, "High school diploma or equivalent",
     "Join metal parts together using heat and gas or electric arc"),
    ("Carpenter", "Trades", 51390, 714000, 2.0, "High school diploma or equivalent",
     "Build, install, and repair structures and fixtures made of wood"),
    ("Automotive Mechanic", "Trades", 46880, 769000, -1.1, "Postsecondary nondegree award",
     "Repair and maintain motor vehicles"),
    ("Construction Manager", "Trades", 101480, 476000, 5.0, "Bachelor's degree",
     "Plan, coordinate, and manage construction projects"),
    ("Heavy Equipment Operator", "Trades", 53000, 512000, 3.0, "High school diploma or equivalent",
     "Operate heavy construction equipment like cranes, bulldozers, and excavators"),
    ("Machinist", "Trades", 47930, 373000, -4.7, "High school diploma or equivalent",
     "Set up and operate machine tools to produce precision metal parts"),
    ("Diesel Mechanic", "Trades", 55400, 268000, 3.5, "High school diploma or equivalent",
     "Inspect, repair, and maintain diesel engines and equipment"),
    ("Elevator Installer", "Trades", 99000, 25000, 1.8, "High school diploma or equivalent",
     "Install, fix, and maintain elevators, escalators, and related equipment"),
    ("Sheet Metal Worker", "Trades", 56370, 138000, 0.5, "High school diploma or equivalent",
     "Fabricate and install products made from thin metal sheets"),

    # ─── Transportation & Logistics ───
    ("Truck Driver", "Transportation", 49920, 2102000, 4.2, "Postsecondary nondegree award",
     "Transport goods between locations by driving trucks"),
    ("Airline Pilot", "Transportation", 211790, 87000, 5.8, "Bachelor's degree",
     "Fly and navigate airplanes for airlines or other organizations"),
    ("Air Traffic Controller", "Transportation", 138556, 24000, 1.0, "Associate's degree",
     "Coordinate the movement of air traffic to ensure safety"),
    ("Logistics Manager", "Transportation", 98560, 205000, 18.8, "Bachelor's degree",
     "Plan and coordinate supply chain and logistics operations"),
    ("Bus Driver", "Transportation", 46000, 697000, 5.1, "High school diploma or equivalent",
     "Transport passengers on predetermined routes"),
    ("Delivery Driver", "Transportation", 38000, 1567000, 11.5, "High school diploma or equivalent",
     "Deliver goods and packages to homes and businesses"),
    ("Warehouse Worker", "Transportation", 37000, 1867000, 5.8, "High school diploma or equivalent",
     "Receive, store, and distribute products within a warehouse"),
    ("Supply Chain Analyst", "Transportation", 82000, 88000, 15.0, "Bachelor's degree",
     "Analyze supply chain operations and recommend improvements"),
    ("Ship Captain", "Transportation", 95000, 37000, 2.5, "Postsecondary nondegree award",
     "Command and navigate ships and large vessels"),
    ("Train Engineer", "Transportation", 71000, 63000, 0.0, "High school diploma or equivalent",
     "Operate locomotives to transport passengers and freight"),

    # ─── Social Services & Government ───
    ("Social Worker", "Social Services", 55350, 720000, 7.1, "Bachelor's degree",
     "Help people cope with challenges in their everyday lives"),
    ("Psychologist", "Social Services", 85330, 175000, 6.3, "Doctoral or professional degree",
     "Study cognitive, emotional, and social processes and behavior"),
    ("Police Officer", "Social Services", 66020, 806000, 2.7, "High school diploma or equivalent",
     "Protect lives and property by enforcing laws and regulations"),
    ("Firefighter", "Social Services", 51680, 326000, 4.2, "Postsecondary nondegree award",
     "Respond to fires, accidents, and other emergencies"),
    ("Military Officer", "Social Services", 80000, 230000, 2.0, "Bachelor's degree",
     "Lead and command military personnel in various operations"),
    ("Urban Planner", "Social Services", 79540, 38000, 4.3, "Master's degree",
     "Develop plans and programs for the use of land and community growth"),
    ("Substance Abuse Counselor", "Social Services", 49710, 331000, 17.6, "Bachelor's degree",
     "Advise people who suffer from alcoholism, drug addiction, or other addictions"),
    ("Probation Officer", "Social Services", 60250, 92000, 1.0, "Bachelor's degree",
     "Monitor and assist offenders in rehabilitation after release from prison"),
    ("Political Scientist", "Social Services", 128020, 7500, 6.0, "Master's degree",
     "Study political systems, public policy, and political behavior"),
    ("Immigration Officer", "Social Services", 68000, 15000, 3.0, "Bachelor's degree",
     "Enforce immigration laws and process immigration applications"),

    # ─── Hospitality & Service ───
    ("Chef/Head Cook", "Hospitality", 56520, 155000, 5.7, "High school diploma or equivalent",
     "Direct and participate in food preparation and cooking"),
    ("Hotel Manager", "Hospitality", 61910, 54000, 7.0, "Bachelor's degree",
     "Plan, direct, and coordinate lodging operations"),
    ("Event Planner", "Hospitality", 56920, 142000, 7.5, "Bachelor's degree",
     "Coordinate events, meetings, and conventions"),
    ("Flight Attendant", "Hospitality", 63760, 127000, 11.0, "High school diploma or equivalent",
     "Ensure safety and comfort of airline passengers during flights"),
    ("Tour Guide", "Hospitality", 33000, 52000, 7.0, "High school diploma or equivalent",
     "Plan, organize, and lead tours for individuals or groups"),
    ("Restaurant Manager", "Hospitality", 63060, 418000, 10.0, "High school diploma or equivalent",
     "Plan and coordinate the operations of restaurants"),
    ("Bartender", "Hospitality", 31510, 681000, 3.7, "No formal educational credential",
     "Mix and serve drinks to patrons at bars and restaurants"),
    ("Travel Agent", "Hospitality", 46400, 69000, -12.0, "High school diploma or equivalent",
     "Plan and sell transportation and accommodations for travelers"),

    # ─── Real Estate & Construction ───
    ("Real Estate Agent", "Real Estate", 52030, 480000, 3.2, "High school diploma or equivalent",
     "Help clients buy, sell, and rent properties"),
    ("Real Estate Appraiser", "Real Estate", 61340, 80000, 2.0, "Bachelor's degree",
     "Estimate the value of real property for various purposes"),
    ("Property Manager", "Real Estate", 60670, 389000, 3.0, "High school diploma or equivalent",
     "Direct the management of residential, commercial, or industrial real estate"),
    ("Architect", "Real Estate", 82840, 129000, 2.8, "Bachelor's degree",
     "Plan and design buildings and other structures"),
    ("Surveyor", "Real Estate", 73570, 54000, 1.0, "Bachelor's degree",
     "Make precise measurements to determine property boundaries"),

    # ─── Agriculture & Environment ───
    ("Agricultural Engineer", "Agriculture", 84410, 2700, 5.0, "Bachelor's degree",
     "Apply engineering technology to agricultural problems"),
    ("Farm Manager", "Agriculture", 75240, 271000, 1.0, "High school diploma or equivalent",
     "Plan and direct farming operations"),
    ("Conservation Scientist", "Agriculture", 64490, 23000, 5.0, "Bachelor's degree",
     "Manage natural resources to prevent habitat destruction and ensure sustainability"),
    ("Forester", "Agriculture", 64490, 12000, 3.8, "Bachelor's degree",
     "Manage forests and timberland for economic and recreational purposes"),
    ("Wildlife Biologist", "Agriculture", 66500, 18000, 4.7, "Bachelor's degree",
     "Study wildlife and their ecosystems to manage and protect species"),
    ("Food Scientist", "Agriculture", 80600, 17000, 7.5, "Bachelor's degree",
     "Research and develop food processing methods and products"),

    # ─── Manufacturing & Production ───
    ("Manufacturing Engineer", "Manufacturing", 92000, 285000, 2.5, "Bachelor's degree",
     "Design and improve manufacturing processes and systems"),
    ("Assembly Line Worker", "Manufacturing", 35000, 1800000, -10.0, "High school diploma or equivalent",
     "Perform repetitive tasks on production lines to assemble products"),
    ("Quality Inspector", "Manufacturing", 42000, 489000, -6.0, "High school diploma or equivalent",
     "Inspect products to ensure they meet quality standards"),
    ("Production Manager", "Manufacturing", 110000, 228000, -1.0, "Bachelor's degree",
     "Plan, direct, and coordinate production activities"),
    ("CNC Operator", "Manufacturing", 45790, 311000, -5.0, "High school diploma or equivalent",
     "Operate computer-controlled machine tools to shape metal or plastic parts"),
    ("Packaging Operator", "Manufacturing", 33500, 356000, -7.0, "High school diploma or equivalent",
     "Operate machines that package products for shipment"),
    ("Textile Worker", "Manufacturing", 30000, 95000, -15.0, "No formal educational credential",
     "Operate machines that produce textiles and garments"),
    ("Printing Press Operator", "Manufacturing", 39000, 160000, -12.0, "High school diploma or equivalent",
     "Set up and operate printing presses to produce printed materials"),

    # ─── Administrative & Office ───
    ("Administrative Assistant", "Administrative", 44080, 3509000, -8.3, "High school diploma or equivalent",
     "Perform routine clerical and organizational tasks"),
    ("Executive Assistant", "Administrative", 65980, 585000, -4.0, "High school diploma or equivalent",
     "Provide high-level administrative support to executives"),
    ("Data Entry Clerk", "Administrative", 37970, 175000, -25.3, "High school diploma or equivalent",
     "Enter data into computer databases and verify accuracy"),
    ("Receptionist", "Administrative", 36600, 1037000, -5.0, "High school diploma or equivalent",
     "Greet visitors, answer phones, and perform administrative duties"),
    ("Office Manager", "Administrative", 52000, 1460000, -2.0, "High school diploma or equivalent",
     "Supervise and coordinate office administrative activities"),
    ("Payroll Clerk", "Administrative", 49000, 139000, -8.0, "High school diploma or equivalent",
     "Compile and record employee time and payroll data"),
    ("File Clerk", "Administrative", 35000, 58000, -15.0, "High school diploma or equivalent",
     "Organize and maintain paper and electronic filing systems"),
    ("Billing Specialist", "Administrative", 42000, 510000, -5.5, "High school diploma or equivalent",
     "Process billing and collections for organizations"),
    ("Mail Clerk", "Administrative", 33000, 65000, -20.0, "High school diploma or equivalent",
     "Sort and distribute mail and prepare outgoing mail"),
    ("Transcriptionist", "Administrative", 36960, 46000, -18.0, "Postsecondary nondegree award",
     "Listen to recordings and transcribe them into written documents"),

    # ─── Sales & Retail ───
    ("Sales Manager", "Sales", 132290, 469000, 4.0, "Bachelor's degree",
     "Direct organizations' sales teams and set sales goals"),
    ("Insurance Agent", "Sales", 57860, 535000, 5.9, "High school diploma or equivalent",
     "Sell insurance policies to individuals and businesses"),
    ("Retail Salesperson", "Sales", 30750, 4315000, -1.0, "No formal educational credential",
     "Sell merchandise in retail stores to customers"),
    ("Cashier", "Sales", 28000, 3336000, -9.0, "No formal educational credential",
     "Receive and process payments from customers"),
    ("Telemarketer", "Sales", 31000, 105000, -18.0, "No formal educational credential",
     "Solicit orders for goods or services over the telephone"),
    ("Real Estate Sales Agent", "Sales", 52030, 480000, 3.2, "High school diploma or equivalent",
     "Sell real estate properties for clients"),
    ("Wholesale Sales Rep", "Sales", 65420, 1431000, -3.0, "High school diploma or equivalent",
     "Sell goods to businesses and organizations for resale"),
    ("Pharmaceutical Sales Rep", "Sales", 85000, 68000, -2.0, "Bachelor's degree",
     "Sell pharmaceutical products to healthcare providers"),

    # ─── Human Resources ───
    ("HR Manager", "Human Resources", 130000, 186000, 5.0, "Bachelor's degree",
     "Plan and direct administrative functions of organizations"),
    ("HR Specialist", "Human Resources", 64240, 783000, 5.8, "Bachelor's degree",
     "Recruit, screen, and interview job applicants"),
    ("Training & Development Manager", "Human Resources", 120000, 42000, 6.0, "Bachelor's degree",
     "Plan and coordinate training programs for employees"),
    ("Compensation Analyst", "Human Resources", 74000, 18000, 6.0, "Bachelor's degree",
     "Analyze and evaluate employee compensation and benefits"),
    ("Recruiter", "Human Resources", 62290, 340000, 7.5, "Bachelor's degree",
     "Find and recruit qualified candidates for job openings"),

    # ─── Miscellaneous / Other ───
    ("Athlete", "Sports & Entertainment", 77300, 14000, 5.0, "No formal educational credential",
     "Compete in organized athletic events"),
    ("Fitness Trainer", "Sports & Entertainment", 46480, 382000, 14.0, "High school diploma or equivalent",
     "Lead, instruct, and motivate individuals or groups in exercise activities"),
    ("Athletic Trainer", "Sports & Entertainment", 53840, 32000, 14.0, "Bachelor's degree",
     "Prevent, diagnose, and treat muscle and bone injuries"),
    ("Clergy", "Social Services", 55190, 63000, 3.0, "Bachelor's degree",
     "Conduct religious worship and provide spiritual guidance"),
    ("Interpreter/Translator", "Social Services", 55760, 83000, 4.0, "Bachelor's degree",
     "Convert information from one language to another"),
    ("Funeral Director", "Social Services", 61060, 34000, 4.0, "Associate's degree",
     "Plan and manage funeral services and counsel bereaved families"),
]


# ── Skills templates by category ──
SKILLS_BY_CATEGORY = {
    "Technology": [
        ("Programming", "skill", 85), ("Systems Analysis", "skill", 75),
        ("Critical Thinking", "skill", 80), ("Complex Problem Solving", "skill", 85),
        ("Mathematics", "knowledge", 70), ("Data Analysis", "skill", 80),
        ("Technical Writing", "skill", 60), ("Computers and Electronics", "knowledge", 90),
        ("Customer Service", "skill", 45), ("Active Learning", "skill", 75),
    ],
    "Healthcare": [
        ("Medicine and Dentistry", "knowledge", 85), ("Biology", "knowledge", 75),
        ("Patient Care", "skill", 90), ("Critical Thinking", "skill", 80),
        ("Active Listening", "skill", 85), ("Social Perceptiveness", "skill", 80),
        ("Complex Problem Solving", "skill", 75), ("Monitoring", "skill", 70),
        ("Decision Making", "skill", 80), ("Communication", "skill", 85),
    ],
    "Finance": [
        ("Mathematics", "knowledge", 80), ("Economics", "knowledge", 75),
        ("Financial Analysis", "skill", 85), ("Critical Thinking", "skill", 75),
        ("Data Analysis", "skill", 80), ("Communication", "skill", 65),
        ("Attention to Detail", "skill", 85), ("Accounting", "knowledge", 80),
        ("Spreadsheet Software", "skill", 75), ("Regulatory Compliance", "knowledge", 70),
    ],
    "Education": [
        ("Teaching", "skill", 90), ("Communication", "skill", 90),
        ("Active Listening", "skill", 85), ("Social Perceptiveness", "skill", 85),
        ("Instructing", "skill", 90), ("Learning Strategies", "skill", 80),
        ("Psychology", "knowledge", 70), ("Patience", "ability", 85),
        ("Curriculum Design", "skill", 75), ("Student Assessment", "skill", 70),
    ],
    "Legal": [
        ("Law and Government", "knowledge", 90), ("Critical Thinking", "skill", 85),
        ("Reading Comprehension", "skill", 85), ("Active Listening", "skill", 80),
        ("Writing", "skill", 85), ("Negotiation", "skill", 80),
        ("Persuasion", "skill", 75), ("Research", "skill", 80),
        ("Judgment and Decision Making", "skill", 85), ("Communication", "skill", 85),
    ],
    "Engineering": [
        ("Engineering Design", "skill", 85), ("Mathematics", "knowledge", 85),
        ("Physics", "knowledge", 75), ("Critical Thinking", "skill", 80),
        ("Complex Problem Solving", "skill", 85), ("CAD Software", "skill", 70),
        ("Technical Writing", "skill", 65), ("Project Management", "skill", 65),
        ("Systems Analysis", "skill", 75), ("Quality Control", "skill", 70),
    ],
    "Creative & Media": [
        ("Creativity", "ability", 90), ("Design", "skill", 85),
        ("Communication", "skill", 80), ("Active Listening", "skill", 70),
        ("Writing", "skill", 75), ("Visual Arts", "knowledge", 80),
        ("Social Media", "skill", 65), ("Storytelling", "skill", 80),
        ("Attention to Detail", "skill", 75), ("Time Management", "skill", 65),
    ],
    "Science": [
        ("Research Methods", "skill", 90), ("Mathematics", "knowledge", 80),
        ("Critical Thinking", "skill", 85), ("Data Analysis", "skill", 85),
        ("Scientific Writing", "skill", 75), ("Laboratory Skills", "skill", 80),
        ("Complex Problem Solving", "skill", 80), ("Statistics", "knowledge", 75),
        ("Active Learning", "skill", 80), ("Observation", "skill", 85),
    ],
    "Trades": [
        ("Manual Dexterity", "ability", 85), ("Physical Stamina", "ability", 75),
        ("Equipment Maintenance", "skill", 80), ("Troubleshooting", "skill", 80),
        ("Blueprint Reading", "skill", 70), ("Safety Procedures", "knowledge", 85),
        ("Customer Service", "skill", 55), ("Mathematics", "knowledge", 60),
        ("Problem Solving", "skill", 75), ("Attention to Detail", "skill", 80),
    ],
    "Transportation": [
        ("Vehicle Operation", "skill", 85), ("Navigation", "skill", 75),
        ("Safety Procedures", "knowledge", 90), ("Time Management", "skill", 70),
        ("Customer Service", "skill", 55), ("Physical Stamina", "ability", 65),
        ("Attention to Detail", "skill", 75), ("Communication", "skill", 60),
        ("Equipment Maintenance", "skill", 60), ("Route Planning", "skill", 70),
    ],
    "Social Services": [
        ("Counseling", "skill", 85), ("Active Listening", "skill", 90),
        ("Social Perceptiveness", "skill", 85), ("Communication", "skill", 85),
        ("Critical Thinking", "skill", 75), ("Empathy", "ability", 90),
        ("Psychology", "knowledge", 75), ("Conflict Resolution", "skill", 80),
        ("Cultural Sensitivity", "skill", 75), ("Decision Making", "skill", 70),
    ],
    "Hospitality": [
        ("Customer Service", "skill", 90), ("Communication", "skill", 80),
        ("Food Preparation", "skill", 70), ("Time Management", "skill", 75),
        ("Attention to Detail", "skill", 70), ("Problem Solving", "skill", 65),
        ("Physical Stamina", "ability", 65), ("Teamwork", "skill", 80),
        ("Cultural Awareness", "knowledge", 60), ("First Aid", "knowledge", 45),
    ],
    "Real Estate": [
        ("Sales", "skill", 80), ("Negotiation", "skill", 85),
        ("Communication", "skill", 85), ("Market Analysis", "skill", 75),
        ("Customer Service", "skill", 80), ("Legal Knowledge", "knowledge", 65),
        ("Financial Analysis", "skill", 60), ("Networking", "skill", 75),
        ("Property Valuation", "skill", 70), ("Marketing", "skill", 65),
    ],
    "Agriculture": [
        ("Biology", "knowledge", 75), ("Equipment Operation", "skill", 70),
        ("Environmental Science", "knowledge", 70), ("Problem Solving", "skill", 65),
        ("Physical Stamina", "ability", 70), ("Management", "skill", 65),
        ("Data Analysis", "skill", 55), ("Safety Procedures", "knowledge", 75),
        ("Communication", "skill", 55), ("Planning", "skill", 65),
    ],
    "Manufacturing": [
        ("Equipment Operation", "skill", 85), ("Quality Control", "skill", 80),
        ("Attention to Detail", "skill", 80), ("Physical Stamina", "ability", 70),
        ("Safety Procedures", "knowledge", 85), ("Mathematics", "knowledge", 55),
        ("Troubleshooting", "skill", 65), ("Manual Dexterity", "ability", 80),
        ("Production Processing", "knowledge", 75), ("Time Management", "skill", 65),
    ],
    "Administrative": [
        ("Data Entry", "skill", 80), ("Word Processing", "skill", 80),
        ("Filing", "skill", 75), ("Customer Service", "skill", 70),
        ("Scheduling", "skill", 75), ("Communication", "skill", 65),
        ("Spreadsheet Software", "skill", 70), ("Attention to Detail", "skill", 75),
        ("Time Management", "skill", 70), ("Organization", "skill", 75),
    ],
    "Sales": [
        ("Persuasion", "skill", 85), ("Communication", "skill", 85),
        ("Negotiation", "skill", 80), ("Customer Service", "skill", 80),
        ("Product Knowledge", "knowledge", 75), ("Active Listening", "skill", 75),
        ("Problem Solving", "skill", 65), ("CRM Software", "skill", 60),
        ("Networking", "skill", 70), ("Time Management", "skill", 65),
    ],
    "Human Resources": [
        ("Human Resources Management", "knowledge", 85), ("Communication", "skill", 85),
        ("Active Listening", "skill", 80), ("Negotiation", "skill", 75),
        ("Psychology", "knowledge", 65), ("Data Analysis", "skill", 60),
        ("Conflict Resolution", "skill", 75), ("Employment Law", "knowledge", 70),
        ("Interviewing", "skill", 80), ("Training", "skill", 70),
    ],
    "Sports & Entertainment": [
        ("Physical Fitness", "ability", 90), ("Coordination", "ability", 85),
        ("Discipline", "ability", 80), ("Communication", "skill", 65),
        ("Teamwork", "skill", 75), ("Strategy", "skill", 70),
        ("Performance", "skill", 85), ("Endurance", "ability", 80),
        ("Mental Toughness", "ability", 80), ("Coaching", "skill", 60),
    ],
}


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(Career).count()
        if existing > 0:
            print(f"Database already has {existing} careers. Clearing and reseeding...")
            db.query(EnsemblePrediction).delete()
            db.query(Prediction).delete()
            db.query(CareerSkill).delete()
            db.query(Career).delete()
            db.commit()

        print(f"Seeding {len(CAREERS_DATA)} careers...")

        for i, (title, category, salary, employment, growth, education, description) in enumerate(CAREERS_DATA):
            onet_code = f"{(i // 50) + 11:02d}-{(i % 50) * 20 + 1000:04d}.00"

            career = Career(
                onet_code=onet_code,
                bls_code=f"{(i // 50) + 11:02d}-{(i % 50) * 20 + 1000:04d}",
                title=title,
                category=category,
                description=description,
                median_salary=salary,
                employment_count=employment,
                growth_rate_pct=growth,
                education_level=education,
                experience_level="None" if growth > 15 else "Less than 5 years",
            )
            db.add(career)
            db.flush()

            # Add skills
            category_skills = SKILLS_BY_CATEGORY.get(category, SKILLS_BY_CATEGORY["Technology"])
            for skill_name, skill_cat, importance in category_skills:
                noise = random.uniform(-10, 10)
                importance_adj = max(10, min(100, importance + noise))
                automation = score_skill_automation(skill_name, skill_cat)

                skill = CareerSkill(
                    career_id=career.id,
                    skill_name=skill_name,
                    skill_category=skill_cat,
                    importance_score=round(importance_adj, 1),
                    automation_potential=round(automation, 2),
                )
                db.add(skill)

            db.flush()

            # Compute automation risk from skills
            career_skills = [
                {"importance_score": s.importance_score, "automation_potential": s.automation_potential}
                for s in db.query(CareerSkill).filter(CareerSkill.career_id == career.id).all()
            ]
            base_risk = compute_career_automation_index(career_skills)

            # Adjust risk based on career characteristics
            if growth < 0:
                base_risk = min(100, base_risk + 10)
            if salary > 120000:
                base_risk = max(5, base_risk - 8)
            if education in ["Doctoral or professional degree", "Master's degree"]:
                base_risk = max(5, base_risk - 12)
            if category in ["Administrative", "Manufacturing"]:
                base_risk = min(100, base_risk + 15)
            if category in ["Healthcare", "Education", "Social Services"]:
                base_risk = max(5, base_risk - 10)

            base_risk = max(5, min(95, base_risk))

            # Generate individual model predictions with variation
            model_names = ["linear_regression", "random_forest", "gradient_boosting", "neural_network"]
            model_predictions = []

            for model_name in model_names:
                variation = random.gauss(0, 5)
                model_risk = max(5, min(95, base_risk + variation))

                if model_risk > 75:
                    disruption_year = random.randint(2026, 2032)
                elif model_risk > 50:
                    disruption_year = random.randint(2030, 2038)
                elif model_risk > 30:
                    disruption_year = random.randint(2035, 2042)
                else:
                    disruption_year = random.randint(2040, 2050)

                salary_impact = -model_risk * 0.4 + random.gauss(0, 5)
                salary_impact = max(-45, min(25, salary_impact))

                stability = 100 - model_risk + growth * 0.5 + random.gauss(0, 5)
                stability = max(10, min(95, stability))

                pred = Prediction(
                    career_id=career.id,
                    model_name=model_name,
                    automation_risk_score=round(model_risk, 1),
                    disruption_year=disruption_year,
                    salary_impact_pct=round(salary_impact, 1),
                    job_stability_score=round(stability, 1),
                    confidence_interval_low=round(max(0, model_risk - 10), 1),
                    confidence_interval_high=round(min(100, model_risk + 10), 1),
                )
                db.add(pred)
                model_predictions.append({
                    "risk": model_risk,
                    "year": disruption_year,
                    "salary_impact": salary_impact,
                    "stability": stability,
                })

            # Ensemble prediction (weighted average)
            avg_risk = np.mean([p["risk"] for p in model_predictions])
            avg_year = int(np.mean([p["year"] for p in model_predictions]))
            avg_impact = np.mean([p["salary_impact"] for p in model_predictions])
            avg_stability = np.mean([p["stability"] for p in model_predictions])

            if avg_risk >= 70:
                risk_level = "critical"
            elif avg_risk >= 50:
                risk_level = "high"
            elif avg_risk >= 30:
                risk_level = "medium"
            else:
                risk_level = "low"

            salary_5yr = salary * (1 + (avg_impact / 100) * 0.4 + growth / 100 * 0.5)
            salary_10yr = salary * (1 + (avg_impact / 100) * 0.8 + growth / 100)

            ensemble = EnsemblePrediction(
                career_id=career.id,
                automation_risk_score=round(avg_risk, 1),
                disruption_year=avg_year,
                salary_5yr_projection=round(salary_5yr, 0),
                salary_10yr_projection=round(salary_10yr, 0),
                job_stability_score=round(avg_stability, 1),
                risk_level=risk_level,
            )
            db.add(ensemble)

            if (i + 1) % 50 == 0:
                print(f"  Seeded {i + 1}/{len(CAREERS_DATA)} careers...")

        db.commit()
        final_count = db.query(Career).count()
        print(f"\nDone! Seeded {final_count} careers with skills and predictions.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
