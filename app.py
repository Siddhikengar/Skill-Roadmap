# app.py
from flask import Flask, request, jsonify
import json
import time
from collections import defaultdict

# --- IMPORTANT: These global variables are provided by the Canvas environment for Firestore integration.
# We will not be using Firestore in this example, but they are included here as a best practice.
# The `__app_id`, `__firebase_config`, and `__initial_auth_token` are not used in this specific app,
# but would be essential for any app requiring data persistence.
__app_id = "default-app-id"
__firebase_config = "{}"
__initial_auth_token = ""
# --------------------------------------------------------------------------------------------------

app = Flask(__name__)

# --- Data for engineering domains and skills ---
# This data now includes specific job roles within each domain.
engineering_domains = {
    'Software / IT / Data': {
        'Data Analyst': ['Python (Pandas, NumPy)', 'SQL', 'Excel', 'Power BI / Tableau', 'Statistics & Probability', 'Data Cleaning & EDA', 'Google Sheets', 'Communication Skills'],
        'Data Scientist': ['Python (NumPy, Pandas, Scikit-learn)', 'Machine Learning', 'Deep Learning (TensorFlow / PyTorch)', 'SQL', 'Statistics', 'Data Visualization (Seaborn, Matplotlib)', 'Big Data (Spark, Hadoop)', 'NLP / Computer Vision'],
        'Machine Learning Engineer': ['Python, Scikit-learn, TensorFlow', 'Algorithms', 'MLOps', 'Model Deployment (Flask / Streamlit)', 'Git & CI/CD', 'Kubernetes / Docker'],
        'AI Engineer': ['Natural Language Processing (NLP)', 'Computer Vision', 'Reinforcement Learning', 'Deep Learning Frameworks (PyTorch, TensorFlow)', 'Data Structures & Algorithms', 'Cloud Platforms (AWS, GCP, Azure)'],
        'Full Stack Developer': ['HTML, CSS, JavaScript', 'React / Angular (Frontend)', 'Node.js / Django / Flask (Backend)', 'MongoDB / SQL', 'REST APIs', 'Git, GitHub', 'Deployment (Vercel, Heroku, Netlify)'],
        'Frontend Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Vue.js', 'Angular', 'Responsive Design', 'SASS/SCSS', 'Webpack', 'Figma/Sketch'],
        'Backend Developer': ['Node.js', 'Python (Django, Flask)', 'Java (Spring)', 'Go', 'Database Management (SQL, NoSQL)', 'RESTful APIs', 'Microservices', 'Authentication & Authorization'],
        'Android Developer': ['Java / Kotlin', 'Android SDK', 'XML', 'Jetpack Compose', 'UI/UX Design for Mobile', 'Git'],
        'iOS Developer': ['Swift', 'SwiftUI', 'Xcode', 'CocoaPods', 'UIKit', 'API Integration', 'UI/UX Design for Mobile'],
        'Mobile App Developer': ['Flutter / React Native (Cross-platform)', 'Firebase', 'API Integration', 'UI/UX Design', 'State Management'],
        'DevOps Engineer': ['AWS / Azure / GCP', 'Linux', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'CI/CD Pipelines', 'Ansible', 'Networking Basics'],
        'Cloud Engineer': ['AWS / Azure / GCP', 'Virtualization', 'Containerization (Docker, Kubernetes)', 'Cloud Security', 'Serverless Architecture', 'Networking'],
        'Cybersecurity Analyst': ['Networking (TCP/IP, OSI)', 'Kali Linux', 'Wireshark', 'Nmap', 'Python for Security', 'Web Security (OWASP Top 10)', 'Ethical Hacking Tools (Burp Suite, Metasploit)'],
        'Ethical Hacker': ['Penetration Testing', 'Web Security', 'Network Scanning', 'Social Engineering', 'Cryptography', 'Reverse Engineering', 'Metasploit'],
        'Blockchain Developer': ['Solidity', 'Smart Contracts', 'Web3.js', 'Truffle', 'Ganache', 'Cryptography', 'Consensus Algorithms'],
        'UI/UX Designer': ['Figma / Sketch / Adobe XD', 'Wireframing', 'Prototyping', 'User Research', 'Usability Testing', 'Design Systems', 'HTML/CSS'],
        'Software Tester / QA Engineer': ['Test Automation (Selenium, Cypress)', 'Jira', 'TestRail', 'SQL', 'Bug Reporting', 'Manual Testing', 'Performance Testing'],
        'Game Developer': ['Unity / Unreal Engine', 'C++ / C#', 'Game Physics', '3D Modeling', 'Graphics Programming', 'Level Design'],
        'Technical Support Engineer': ['Troubleshooting', 'Linux / Windows OS', 'Networking Fundamentals', 'Scripting (Bash/Python)', 'Customer Service', 'Ticketing Systems (Jira, Zendesk)'],
        'IT Consultant': ['Project Management', 'Business Analysis', 'System Integration', 'Cloud Migration', 'Cybersecurity Strategy', 'Client Management'],
    },
    'Core Engineering': {
        'Mechanical Design Engineer': ['AutoCAD', 'SolidWorks / CATIA / Creo', 'GD&T', 'Thermodynamics', 'Ansys / FEA', 'Engineering Drawing', 'Material Science'],
        'Product Design Engineer': ['Industrial Design', 'Prototyping (3D Printing)', 'DFM (Design for Manufacturing)', 'SolidWorks / Creo', 'User-centered Design', 'Market Analysis'],
        'HVAC Engineer': ['HVAC System Design', 'Refrigeration', 'Thermodynamics', 'Fluid Mechanics', 'Energy Auditing', 'Building Automation Systems'],
        'CAD/CAM Engineer': ['AutoCAD', 'SolidWorks', 'Mastercam', 'CATIA', 'CNC Programming', 'Geometric Dimensioning and Tolerancing (GD&T)'],
        'CAE Analyst': ['FEA (Finite Element Analysis)', 'CFD (Computational Fluid Dynamics)', 'Ansys / ABAQUS', 'Material Properties', 'Simulation'],
        'Civil Site Engineer': ['Project Management', 'Construction Management', 'Quantity Surveying', 'AutoCAD', 'MS Project', 'Surveying'],
        'Structural Engineer': ['AutoCAD', 'STAAD.Pro / ETABS', 'Revit', 'Structural Analysis', 'Concrete & Steel Design', 'Project Management'],
        'Transportation Engineer': ['Traffic Flow Analysis', 'GIS', 'Highway Design', 'Pavement Engineering', 'Transportation Planning Software'],
        'Quantity Surveyor': ['Cost Estimation', 'BIM', 'Contract Management', 'Measurement & Valuation', 'Construction Law'],
        'Electrical Design Engineer': ['MATLAB / Simulink', 'AutoCAD Electrical', 'Embedded Systems', 'Power Systems Design', 'PLC / SCADA', 'Circuit Simulation Tools (Proteus, LTspice)'],
        'Power System Engineer': ['Power Generation', 'Transmission & Distribution', 'Renewable Energy Systems', 'ETAP', 'Grid Stability Analysis', 'Protection Relays'],
        'Embedded Systems Engineer': ['Embedded C/C++', 'Microcontrollers (Arduino, STM32)', 'RTOS', 'Circuit Design', 'IoT Protocols', 'Debugging Tools'],
        'Control Systems Engineer': ['PLC / SCADA', 'PID Control', 'DCS', 'MATLAB / Simulink', 'Control Theory', 'HMI Design'],
        'Instrumentation Engineer': ['Automation & Control Systems', 'Sensor Design', 'Calibration Engineering', 'Process Instrumentation', 'P&ID Diagrams'],
        'Robotics Engineer': ['Arduino, Raspberry Pi', 'ROS / ROS2', 'Python / C++', 'Kinematics', 'Embedded Systems', 'Computer Vision', 'Control Systems'],
        'Mechatronics Engineer': ['Robotics', 'Embedded Systems', 'Control Systems', 'CAD Software', '3D Printing', 'Actuators & Sensors'],
        'Process Engineer': ['Process Simulation (ASPEN)', 'P&ID Diagrams', 'Chemical Reactors', 'Fluid Dynamics', 'Safety Analysis'],
        'Industrial Engineer': ['Lean Manufacturing', 'Six Sigma', 'ERP Systems', 'Supply Chain Management', 'Operations Research', 'Time & Motion Study'],
        'Production Engineer': ['Quality Assurance', 'Process Optimization', 'CAD/CAM', 'CNC Machining', 'Material Handling Systems'],
    },
    'Emerging Technologies': {
        'IoT Engineer': ['Arduino / Raspberry Pi', 'Embedded C', 'Sensors & Actuators', 'MQTT, HTTP, Node-RED', 'Cloud Platforms (Firebase, AWS IoT)', 'Python / C++'],
        'Drone Engineer': ['Aerodynamics', 'Flight Controllers (Pixhawk)', 'ROS', 'C++ / Python', '3D Printing', 'Image Processing'],
        'AR/VR Developer': ['Unity / Unreal Engine', 'C# / C++', '3D Modeling', 'Virtual Reality SDKs (Oculus, SteamVR)', 'Augmented Reality SDKs (ARKit, ARCore)'],
        'Smart Grid Engineer': ['Power Systems', 'Renewable Energy Integration', 'SCADA', 'Cybersecurity for Grids', 'Grid Modernization'],
        'EV (Electric Vehicle) Engineer': ['Battery Management Systems (BMS)', 'Power Electronics', 'Motor Control', 'Embedded Systems', 'CAN Bus Protocol'],
        'Automation Engineer': ['PLC Programming', 'SCADA', 'Robotics', 'Control Systems', 'HMI Design', 'Industrial Networks'],
        'Renewable Energy Engineer': ['Solar PV System Design', 'Wind Turbine Technology', 'Energy Storage Systems', 'MATLAB', 'Energy Policy'],
        'Smart City Analyst': ['GIS', 'Data Analytics', 'IoT Sensor Data', 'Urban Planning', 'Public Policy'],
    },
    'Biotech / Biomedical': {
        'Biomedical Engineer': ['Medical Devices', 'Biomaterials', 'Signal Processing', 'LabVIEW', 'Anatomy & Physiology', 'Medical Imaging'],
        'Genetic Engineer': ['CRISPR', 'Gene Editing Techniques', 'Bioinformatics', 'DNA Sequencing', 'Molecular Biology'],
        'Clinical Research Associate': ['Clinical Trials', 'GCP (Good Clinical Practice)', 'Data Collection', 'Regulatory Affairs', 'Statistics'],
        'Bioinformatics Scientist': ['Python / R', 'Genomic Data Analysis', 'BLAST', 'Sequencing Data', 'Machine Learning for Biology'],
        'Lab Technician': ['PCR', 'ELISA', 'Cell Culture', 'Spectrophotometry', 'Microscopy', 'Data Logging'],
        'Pharma QA/QC Engineer': ['GMP (Good Manufacturing Practice)', 'Quality Control', 'Validation', 'Auditing', 'Regulatory Compliance'],
    },
    'Interdisciplinary / Business Roles': {
        'Business Analyst': ['Business Process Modeling', 'Data Analysis', 'SQL', 'Project Management', 'Communication Skills', 'Requirements Gathering'],
        'Product Manager': ['Agile & Scrum', 'Jira / Trello', 'Roadmapping', 'Competitive Analysis', 'User Interviews', 'Technical Basics (API, DB, Dev cycle)', 'Communication & Leadership'],
        'Digital Marketing Analyst': ['SEO', 'SEM', 'Google Analytics', 'Social Media Marketing', 'A/B Testing', 'Content Strategy'],
        'Technical Writer': ['Documentation Software (Confluence)', 'API Documentation', 'Markdown', 'Technical Editing', 'Git', 'UML'],
        'Data Journalist': ['Data Visualization (D3.js, Tableau)', 'SQL', 'Python (Pandas)', 'Storytelling', 'Fact-Checking', 'HTML/CSS'],
        'SEO Specialist': ['Keyword Research', 'Technical SEO', 'Link Building', 'Content Optimization', 'Google Search Console', 'Analytics'],
        'EdTech Content Creator': ['Instructional Design', 'LMS Platforms', 'Video Production', 'Curriculum Development', 'Scripting', 'Subject Matter Expertise'],
        'Freelance Developer': ['Project Management', 'Client Communication', 'Portfolio Management', 'Pricing Strategy', 'Full Stack Skills', 'Marketing'],
        'Startup Founder / Co-founder': ['Business Plan Development', 'Fundraising', 'Market Validation', 'Product-Market Fit', 'Leadership', 'Networking'],
    }
}

# --- Predefined YouTube video links for skills, now structured by domain and job role ---
skill_video_links = {
    'Software / IT / Data': {
        'Data Analyst': {
            'Python (Pandas, NumPy)': 'https://www.youtube.com/watch?v=vmEHCJofslg',
            'SQL': 'https://www.youtube.com/watch?v=HXV3zeQKqGY',
            'Excel': 'https://www.youtube.com/watch?v=Vl0H-qTclOg',
            'Power BI / Tableau': 'https://www.youtube.com/watch?v=AGrl-H87pRU',
            'Statistics & Probability': 'https://www.youtube.com/watch?v=XXDLuG5n2WY',
            'Data Cleaning & EDA': 'https://www.youtube.com/watch?v=5RduIEaXcZk',
            'Google Sheets': 'https://www.youtube.com/watch?v=ANnZf0JD3fg',
            'Communication Skills': 'https://www.youtube.com/watch?v=oVZ6P5GJS50'
        },
        'Data Scientist': {
            'Python (NumPy, Pandas, Scikit-learn)': 'https://www.youtube.com/watch?v=Iqjy9UqKKuo',
            'Machine Learning': 'https://www.youtube.com/watch?v=Gv9_4yMHFhI',
            'Deep Learning (TensorFlow / PyTorch)': 'https://www.youtube.com/watch?v=aircAruvnKk',
            'SQL': 'https://www.youtube.com/watch?v=HXV3zeQKqGY',
            'Statistics': 'https://www.youtube.com/watch?v=Vfo5le26IhY',
            'Data Visualization (Seaborn, Matplotlib)': 'https://www.youtube.com/watch?v=0P7QnIQDBJY',
            'Big Data (Spark, Hadoop)': 'https://www.youtube.com/watch?v=Ck1QDL5MD4I',
            'NLP / Computer Vision': 'https://www.youtube.com/watch?v=8u-wyP2G2Uo'
        },
        'Machine Learning Engineer': {
            'Python, Scikit-learn, TensorFlow': 'https://www.youtube.com/watch?v=tPYj3fFJGjk',
            'Algorithms': 'https://www.youtube.com/watch?v=rL8X2mlNHPM',
            'MLOps': 'https://www.youtube.com/watch?v=vGk9EjBQB64',
            'Model Deployment (Flask / Streamlit)': 'https://www.youtube.com/watch?v=JwSS70SZdyM',
            'Git & CI/CD': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'Kubernetes / Docker': 'https://www.youtube.com/watch?v=3c-iBn73dDE'
        },
        'AI Engineer': {
            'Natural Language Processing (NLP)': 'https://www.youtube.com/watch?v=8u-wyP2G2Uo',
            'Computer Vision': 'https://www.youtube.com/watch?v=YRhxdVk_sIs',
            'Reinforcement Learning': 'https://www.youtube.com/watch?v=2pWv7GOvuf0',
            'Deep Learning Frameworks (PyTorch, TensorFlow)': 'https://www.youtube.com/watch?v=aircAruvnKk',
            'Data Structures & Algorithms': 'https://www.youtube.com/watch?v=8hly31xKli0',
            'Cloud Platforms (AWS, GCP, Azure)': 'https://www.youtube.com/watch?v=ulprqHHWlng'
        },
        'Full Stack Developer': {
            'HTML, CSS, JavaScript': 'https://www.youtube.com/watch?v=mU6anWqZJcc',
            'React / Angular (Frontend)': 'https://www.youtube.com/watch?v=bMknfKXIFA8',
            'Node.js / Django / Flask (Backend)': 'https://www.youtube.com/watch?v=Oe421EPjeBE',
            'MongoDB / SQL': 'https://www.youtube.com/watch?v=-56x56UppqQ',
            'REST APIs': 'https://www.youtube.com/watch?v=SLauY6PpjW4',
            'Git, GitHub': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'Deployment (Vercel, Heroku, Netlify)': 'https://www.youtube.com/watch?v=SrwxAScdyT0'
        },
    },
    'Core Engineering': {
        'Mechanical Design Engineer': {
            'AutoCAD': 'https://www.youtube.com/playlist?list=PLrOFa8sDv6jfA_7hRj94PBu2MUhjBPBfa',
            'SolidWorks / CATIA / Creo': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'Ansys / FEA': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'Thermodynamics': 'https://www.youtube.com/watch?v=ctjTX4kdQgQ'
        },
        'Product Design Engineer': {
            'Prototyping (3D Printing)': 'https://www.youtube.com/playlist?list=PLrOFa8sDv6jfA_7hRj94PBu2MUhjBPBfa',
            'SolidWorks / Creo': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ'
        },
        'HVAC Engineer': {
            'AutoCAD': 'https://www.youtube.com/playlist?list=PLrOFa8sDv6jfA_7hRj94PBu2MUhjBPBfa',
            'Thermodynamics': 'https://www.youtube.com/watch?v=ctjTX4kdQgQ'
        },
        'CAD/CAM Engineer': {
            'AutoCAD': 'https://www.youtube.com/c/CADCAMTutorials/playlists',
            'Mastercam': 'https://www.youtube.com/c/CADCAMTutorials/playlists'
        },
        'CAE Analyst': {
            'FEA (Finite Element Analysis)': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'Ansys / ABAQUS': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ'
        }
    },
    'Emerging Technologies': {
        'IoT Engineer': {
            'Arduino / Raspberry Pi': 'https://www.youtube.com/watch?v=piPe6P5fLa8 (Edureka – IoT Full Course)',
            'MQTT, HTTP, Node-RED': 'https://www.youtube.com/user/arduino (Arduino channel covers Node-RED projects)',
            'Cloud Platforms (Firebase, AWS IoT)': 'https://www.youtube.com/watch?v=piPe6P5fLa8 (Edureka IoT course touches on cloud)'
        },
        'Drone Engineer': {
            'Aerodynamics': 'https://www.youtube.com/watch?v=4O6XQEs2JS0 (Hovergames – Drone Aerodynamics basics)',
            'Flight Controllers (Pixhawk)': 'https://www.youtube.com/playlist?list=PLsVb2b0oP2N5_fQf_nkYGyD8Kve5bSXz8 (The Construct – ROS tutorials)',
            '3D Printing': 'https://www.youtube.com/c/CADCAMTutorials/playlists (CAD CAM Tutorials)'
        },
        'AR/VR Developer': {
            'Unity / Unreal Engine': 'https://www.youtube.com/playlist?list=PLe14nNaaiSTH7drEfnSQqcmOk0vs3vxWH (Unity Basics playlist)',
            'Virtual Reality SDKs (Oculus, SteamVR)': 'https://www.youtube.com/playlist?list=PLb1h4A0yB97873ng20yhj9usfGH6ODmFr (AR Foundation by Dinesh Punni)',
            '3D Modeling': 'https://www.youtube.com/playlist?list=PLe14nNaaiSTH7drEfnSQqcmOk0vs3vxWH'
        },
        'Smart Grid Engineer': {
            'Power Systems': 'https://www.youtube.com/watch?v=ulprqHHWlng (Simplilearn – Power Engineering Basics)',
            'Cybersecurity for Grids': 'https://www.youtube.com/c/TheCyberMentor',
            'SCADA': 'https://www.youtube.com/watch?v=oqCio0IHsNE (CAD/FEA channel covers SCADA layouts)'
        },
        'EV (Electric Vehicle) Engineer': {
            'Battery Management Systems (BMS)': 'https://www.youtube.com/watch?v=ulprqHHWlng',
            'Power Electronics': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'Motor Control': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'CAN Bus Protocol': 'https://www.youtube.com/watch?v=ulprqHHWlng'
        },
        'Automation Engineer': {
            'PLC Programming': 'https://www.youtube.com/watch?v=H5QopU-0f8E (RealPars – PLC SCADA Basics)',
            'SCADA': 'https://www.youtube.com/watch?v=H5QopU-0f8E (RealPars – PLC SCADA Basics)',
            'Robotics': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ',
            'Control Systems': 'https://www.youtube.com/channel/UCOOVWyeqLgZOIC2HSvHAlIQ'
        },
        'Renewable Energy Engineer': {
            'Solar PV System Design': 'https://www.youtube.com/watch?v=ulprqHHWlng',
            'Wind Turbine Technology': 'https://www.youtube.com/watch?v=ulprqHHWlng',
            'Energy Storage Systems': 'https://www.youtube.com/watch?v=ulprqHHWlng',
            'MATLAB': 'https://www.youtube.com/playlist?list=PLn8PRpmsu08q6GQjWAHE5hPRQ0tL6XxwG'
        },
        'Smart City Analyst': {
            'GIS': 'https://www.youtube.com/c/ETAPrime',
            'IoT Sensor Data': 'https://www.youtube.com/watch?v=piPe6P5fLa8',
            'Public Policy': 'https://www.youtube.com/watch?v=ulprqHHWlng'
        }
    },
    'Biotech / Biomedical': {
        'Biomedical Engineer': {
            'Medical Devices': 'https://www.youtube.com/watch?v=jAhjPd4uNFY (Kurzgesagt – CRISPR & devices)',
            'Biomaterials': 'https://www.youtube.com/watch?v=jAhjPd4uNFY',
            'LabVIEW': 'https://www.youtube.com/watch?v=aircAruvnKk',
            'Medical Imaging': 'https://www.youtube.com/watch?v=aircAruvnKk'
        },
        'Genetic Engineer': {
            'CRISPR': 'https://www.youtube.com/watch?v=jAhjPd4uNFY',
            'Gene Editing Techniques': 'https://www.youtube.com/playlist?list=PLqRdN8LKr3nWhgKaH-Xu04ZEXrb0lcKJU',
            'Bioinformatics': 'https://www.youtube.com/playlist?list=PLqRdN8LKr3nWhgKaH-Xu04ZEXrb0lcKJU'
        },
        'Clinical Research Associate': {
            'Clinical Trials': 'https://www.youtube.com/c/joshstarmer',
            'GCP (Good Clinical Practice)': 'https://www.youtube.com/c/joshstarmer',
            'Statistics': 'https://www.youtube.com/c/joshstarmer'
        },
        'Bioinformatics Scientist': {
            'Python / R': 'https://www.youtube.com/watch?v=tPYj3fFJGjk',
            'Genomic Data Analysis': 'https://www.youtube.com/playlist?list=PLqRdN8LKr3nWhgKaH-Xu04ZEXrb0lcKJU',
            'Machine Learning for Biology': 'https://www.youtube.com/playlist?list=PLZoTAELRMXVPBTrWtJkn3wWQxZkmTXGwe'
        },
        'Lab Technician': {
            'PCR': 'https://www.youtube.com/watch?v=oqCio0IHsNE',
            'ELISA': 'https://www.youtube.com/watch?v=oqCio0IHsNE',
            'Cell Culture': 'https://www.youtube.com/watch?v=aircAruvnKk',
            'Spectrophotometry': 'https://www.youtube.com/watch?v=aircAruvnKk'
        },
        'Pharma QA/QC Engineer': {
            'GMP (Good Manufacturing Practice)': 'https://www.youtube.com/watch?v=Vfo5le26IhY',
            'Validation': 'https://www.youtube.com/watch?v=Vfo5le26IhY'
        }
    },
    'Interdisciplinary / Business Roles': {
        'Business Analyst': {
            'Business Process Modeling': 'https://www.youtube.com/watch?v=bMknfKXIFA8',
            'SQL': 'https://www.youtube.com/watch?v=bMknfKXIFA8',
            'Project Management': 'https://www.youtube.com/watch?v=RGOj5yH7evk'
        },
        'Product Manager': {
            'Agile & Scrum': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'Technical Basics (API, DB, Dev cycle)': 'https://www.youtube.com/watch?v=Oe421EPjeBE'
        },
        'Digital Marketing Analyst': {
            'SEO': 'https://www.youtube.com/watch?v=nJodYfE_J6M',
            'SEM': 'https://www.youtube.com/watch?v=nJodYfE_J6M',
            'Google Analytics': 'https://www.youtube.com/watch?v=nJodYfE_J6M',
            'A/B Testing': 'https://www.youtube.com/watch?v=nJodYfE_J6M'
        },
        'Technical Writer': {
            'Documentation Software (Confluence)': 'https://developers.google.com/tech-writing',
            'API Documentation': 'https://developers.google.com/tech-writing',
            'Git': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'UML': 'https://www.youtube.com/watch?v=RGOj5yH7evk'
        },
        'Data Journalist': {
            'Data Visualization (D3.js, Tableau)': 'https://www.youtube.com/watch?v=Ts26-Tf1npk',
            'SQL': 'https://www.youtube.com/watch?v=tPYj3fFJGjk',
            'Python (Pandas)': 'https://www.youtube.com/watch?v=tPYj3fFJGjk',
            'Storytelling': 'https://www.youtube.com/watch?v=oVZ6P5GJS50'
        },
        'SEO Specialist': {
            'Keyword Research': 'https://www.youtube.com/playlists?list=PLJR61fXkAx11mtiKuCEt3XjG0KWggzA37',
            'Technical SEO': 'https://www.youtube.com/playlists?list=PLJR61fXkAx11mtiKuCEt3XjG0KWggzA37'
        },
        'EdTech Content Creator': {
            'Instructional Design': 'https://www.youtube.com/watch?v=oVZ6P5GJS50',
            'Video Production': 'https://www.youtube.com/watch?v=oVZ6P5GJS50',
            'Scripting': 'https://www.youtube.com/watch?v=oVZ6P5GJS50'
        },
        'Freelance Developer': {
            'Portfolio Management': 'https://www.youtube.com/watch?v=mU6anWqZJcc',
            'Full Stack Skills': 'https://www.youtube.com/watch?v=mU6anWqZJcc',
            'Marketing Basics': 'https://www.youtube.com/watch?v=nJodYfE_J6M'
        },
        'Startup Founder / Co-founder': {
            'Fundraising': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'Leadership': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
            'Market Validation': 'https://www.youtube.com/watch?v=Oe421EPjeBE'
        }
    }
}

# --- Core logic functions ---
def get_recommended_skills(domain, job_title, user_skills):
    """
    Gathers skills for a specific job title within a domain and recommends
    skills the user doesn't have.
    """
    if domain not in engineering_domains or job_title not in engineering_domains[domain]:
        return []

    # Get the specific skills for the chosen job title
    job_title_skills = set(skill.strip() for skill in engineering_domains[domain][job_title])
    user_skills_set = set(skill.strip() for skill in user_skills)

    # Find the skills from the job title's list that the user doesn't already have
    skills_to_recommend = list(job_title_skills - user_skills_set)
    return skills_to_recommend

def get_video_recommendations(domain, job_title, skills):
    """
    Looks up predefined YouTube video links for a list of skills based on the
    selected domain and job title.
    """
    recommendations = defaultdict(list)
    
    # Check if the domain and job title exist in our structured video links
    if domain in skill_video_links and job_title in skill_video_links[domain]:
        job_links = skill_video_links[domain][job_title]
        for recommended_skill in skills:
            # Match the recommended skill to the keys in the job_links dictionary
            # This is a more precise check than the previous `in` check.
            for link_key, link_value in job_links.items():
                if recommended_skill == link_key or recommended_skill in link_key:
                    # Split the URL from the description if present
                    url = link_value.split(' ')[0].strip()
                    recommendations[recommended_skill].append(url)
    return recommendations


# --- Flask Routes and HTML content ---
@app.route('/')
def index():
    """
    Renders the main page of the application with inline HTML.
    """
    domains_list = sorted(list(engineering_domains.keys()))
    
    # Build the HTML select options for domains
    domain_options_html = "".join([f'<option value="{domain}">{domain}</option>' for domain in domains_list])

    # The HTML template is defined here as a single string
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Engineering Skill Recommender</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css" />
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
        }}
        .select2-container .select2-selection--multiple {{
            min-height: 44px;
            border-color: #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="container mx-auto p-4 md:p-8">
        <div class="bg-white rounded-xl shadow-lg p-6 md:p-10 max-w-3xl mx-auto">
            <h1 class="text-3xl md:text-4xl font-bold text-center text-gray-800 mb-6">Engineering Skill Recommender</h1>
            <p class="text-center text-gray-600 mb-8">Select your engineering domain and current skills to get recommendations for your next steps!</p>
            
            <form id="analysis-form" class="space-y-6">
                <div>
                    <label for="domain_select" class="block text-sm font-medium text-gray-700">Select your Engineering Domain</label>
                    <select id="domain_select" name="domain" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm p-3 border">
                        <option value="">-- Choose a domain --</option>
                        {domain_options_html}
                    </select>
                </div>
                <div id="job_title_container" class="hidden">
                    <label for="job_title_select" class="block text-sm font-medium text-gray-700">Select your Job Title</label>
                    <select id="job_title_select" name="job_title" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm p-3 border">
                        <option value="">-- Choose a job title --</option>
                    </select>
                </div>
                <div id="skills_container" class="hidden">
                    <label for="skills_select" class="block text-sm font-medium text-gray-700">Select your existing Skills</label>
                    <select id="skills_select" name="skills" multiple="multiple" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm p-3 border">
                        <!-- Skills will be populated dynamically -->
                    </select>
                </div>
                
                <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out">
                    Get Recommendations
                </button>
            </form>

            <div id="loading" class="hidden text-center mt-8">
                <svg class="animate-spin h-8 w-8 text-indigo-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.91l1-1.719zm14-5.291a7.962 7.962 0 01-2 5.291l1 1.719a8 0 003-7.91h-4z"></path>
                </svg>
                <p class="mt-2 text-sm text-gray-600">Generating recommendations...</p>
            </div>

            <div id="results" class="hidden mt-8 space-y-6">
                <div id="recommendation-summary" class="bg-gray-50 p-4 rounded-lg shadow-inner">
                    <h2 class="text-xl font-semibold text-gray-800">Recommended Skills for <span id="job-title-display" class="font-bold"></span></h2>
                    <div id="skill-list" class="mt-2 text-gray-600"></div>
                </div>
                <div id="recommendations" class="bg-gray-50 p-4 rounded-lg shadow-inner">
                    <h2 class="text-xl font-semibold text-gray-800">Video Recommendations</h2>
                    <div id="video-list" class="mt-4 space-y-4"></div>
                </div>
            </div>
            
            <div id="error-message" class="hidden mt-8 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <strong class="font-bold">Error!</strong>
                <span id="error-text" class="block sm:inline">Something went wrong. Please try again.</span>
            </div>
        </div>
    </div>
    
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
    <script>
        // Embed the Python data structure into the HTML for use in JS
        const engineeringDomains = {engineering_domains};
        const skillVideoLinks = {skill_video_links};

        $(document).ready(function() {{
            // Initialize Select2 on the skills dropdown
            $('#skills_select').select2({{
                placeholder: "Select skills you already have",
                allowClear: true
            }});

            // Event listener for domain selection
            $('#domain_select').on('change', function() {{
                const selectedDomain = $(this).val();
                const jobTitleContainer = $('#job_title_container');
                const jobTitleSelect = $('#job_title_select');
                const skillsContainer = $('#skills_container');
                const skillsSelect = $('#skills_select');

                jobTitleSelect.empty().append('<option value="">-- Choose a job title --</option>');
                skillsSelect.empty();
                skillsSelect.select2('destroy'); // Destroy Select2 instance
                skillsContainer.addClass('hidden');
                
                if (selectedDomain) {{
                    jobTitleContainer.removeClass('hidden');
                    const jobTitles = Object.keys(engineeringDomains[selectedDomain]);
                    jobTitles.sort();
                    jobTitles.forEach(title => {{
                        jobTitleSelect.append(`<option value="${{title}}">${{title}}</option>`);
                    }});
                }} else {{
                    jobTitleContainer.addClass('hidden');
                }}
            }});

            // Event listener for job title selection
            $('#job_title_select').on('change', function() {{
                const selectedJobTitle = $(this).val();
                const selectedDomain = $('#domain_select').val();
                const skillsContainer = $('#skills_container');
                const skillsSelect = $('#skills_select');
                
                skillsSelect.empty();
                
                if (selectedJobTitle) {{
                    skillsContainer.removeClass('hidden');
                    const skills = engineeringDomains[selectedDomain][selectedJobTitle];
                    skills.sort();
                    skills.forEach(skill => {{
                        skillsSelect.append(`<option value="${{skill}}">${{skill}}</option>`);
                    }});
                    // Re-initialize Select2 on the updated skills dropdown
                    skillsSelect.select2({{
                        placeholder: "Select skills you already have",
                        allowClear: true
                    }});
                }} else {{
                    skillsSelect.select2('destroy');
                    skillsContainer.addClass('hidden');
                }}
            }});
        }});

        document.getElementById('analysis-form').addEventListener('submit', async function(event) {{
            event.preventDefault();
            
            const form = event.target;
            const loadingIndicator = document.getElementById('loading');
            const resultsDiv = document.getElementById('results');
            const errorDiv = document.getElementById('error-message');
            
            // Hide previous results and errors, show loading spinner
            resultsDiv.classList.add('hidden');
            errorDiv.classList.add('hidden');
            loadingIndicator.classList.remove('hidden');
            
            const formData = new FormData(form);
            const domain = formData.get('domain');
            const job_title = formData.get('job_title');
            const skills = $('#skills_select').val();

            // Create a URLSearchParams object from the data
            const params = new URLSearchParams();
            params.append('domain', domain);
            params.append('job_title', job_title);
            if (skills) {{
                skills.forEach(skill => params.append('skills', skill));
            }}

            try {{
                const response = await fetch('/analyze', {{
                    method: 'POST',
                    body: params,
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }}
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    displayResults(result.recommended_skills, result.recommendations, job_title);
                }} else {{
                    document.getElementById('error-text').textContent = result.error || 'Something went wrong.';
                    errorDiv.classList.remove('hidden');
                }}
            }} catch (e) {{
                console.error('Fetch error:', e);
                document.getElementById('error-text').textContent = 'An unexpected error occurred. Check the console for details.';
                errorDiv.classList.remove('hidden');
            }} finally {{
                loadingIndicator.classList.add('hidden');
            }}
        }});
        
        function displayResults(recommended_skills, recommendations, job_title) {{
            const jobTitleDisplay = document.getElementById('job-title-display');
            const skillListDiv = document.getElementById('skill-list');
            const videoListDiv = document.getElementById('video-list');
            
            jobTitleDisplay.textContent = job_title;

            // Display recommended skills
            skillListDiv.innerHTML = '';
            if (recommended_skills && recommended_skills.length > 0) {{
                const ul = document.createElement('ul');
                ul.className = 'list-disc list-inside space-y-1';
                recommended_skills.forEach(skill => {{
                    const li = document.createElement('li');
                    li.textContent = skill;
                    ul.appendChild(li);
                }});
                skillListDiv.appendChild(ul);
            }} else {{
                skillListDiv.textContent = 'You have a great foundation! No new skills are recommended for this domain.';
            }}

            // Display video recommendations
            videoListDiv.innerHTML = '';
            const domain = $('#domain_select').val();
            
            if (recommended_skills && recommended_skills.length > 0) {{
                const recsWithVideos = Object.keys(recommendations);
                const recsWithoutVideos = recommended_skills.filter(skill => !recsWithVideos.includes(skill));
                
                if (recsWithVideos.length > 0) {{
                    const videoIntro = document.createElement('p');
                    videoIntro.className = 'text-gray-600 mb-2';
                    videoIntro.textContent = 'Here are video recommendations for some of your new skills:';
                    videoListDiv.appendChild(videoIntro);

                    const ul = document.createElement('ul');
                    ul.className = 'mt-2 space-y-2';
                    recsWithVideos.forEach(subject => {{
                        const linkContainer = document.createElement('div');
                        linkContainer.className = 'border-b border-gray-200 pb-2 last:border-b-0';
                        linkContainer.innerHTML = `<h3 class="text-md font-medium text-gray-700">${{subject}}</h3>`;
                        
                        const linkList = document.createElement('ul');
                        linkList.className = 'list-disc list-inside mt-1 space-y-1';
                        recommendations[subject].forEach(link => {{
                            const li = document.createElement('li');
                            li.innerHTML = `<a href="${{link}}" target="_blank" class="text-indigo-600 hover:text-indigo-800 hover:underline">${{link}}</a>`;
                            linkList.appendChild(li);
                        }});
                        linkContainer.appendChild(linkList);
                        ul.appendChild(linkContainer);
                    }});
                    videoListDiv.appendChild(ul);
                }}

                if (recsWithoutVideos.length > 0) {{
                    const noVideoMsg = document.createElement('p');
                    noVideoMsg.className = 'text-gray-600 mt-4';
                    noVideoMsg.textContent = 'No video recommendations were found for the following skills: ' + recsWithoutVideos.join(', ') + '.';
                    videoListDiv.appendChild(noVideoMsg);
                }}

                if (recsWithVideos.length === 0 && recsWithoutVideos.length === 0) {{
                     videoListDiv.innerHTML = '<p class="text-gray-600">No new skills were recommended, so no videos were generated. Keep excelling!</p>';
                }}

            }} else {{
                 videoListDiv.innerHTML = '<p class="text-gray-600">No new skills were recommended, so no videos were generated. Keep excelling!</p>';
            }}
            
            document.getElementById('results').classList.remove('hidden');
        }}
    </script>
</body>
</html>
    """
    return html_content

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Handles the student's data submission, performs analysis, and returns
    results and recommendations.
    """
    try:
        # Get data from the form. request.form.getlist is used for multiple selects
        domain = request.form.get('domain')
        job_title = request.form.get('job_title')
        user_skills_list = request.form.getlist('skills')

        if not domain or not job_title:
            return jsonify({'success': False, 'error': 'Please select a domain and a job title.'})
        
        # Get recommended skills based on user's input
        recommended_skills = get_recommended_skills(domain, job_title, user_skills_list)
        
        # Get video recommendations for the newly recommended skills from the static list
        recommended_videos = get_video_recommendations(domain, job_title, recommended_skills)

        return jsonify({
            'success': True,
            'recommended_skills': recommended_skills,
            'recommendations': recommended_videos
        })

    except Exception as e:
        print(f"An error occurred in the /analyze route: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
