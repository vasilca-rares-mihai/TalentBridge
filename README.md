# TalentBridge 
Last tasks: [Google Sheets](https://docs.google.com/spreadsheets/d/17YalRHokuakujgC83qbFbex8E6gTnH7TYdwfByrpPls/edit?gid=0#gid=0)
<br>
[Interim report not updated](https://github.com/user-attachments/files/25413252/Raport_1_licenta__Rares_Vasilca__ENG.pdf)

### Short description
TalentBridge is an application that wants to solve the problems of current football scouting. It is a service-oriented software application that uses video analysis (MediaPipe Pose) and calculates attributes such as speed, acceleration, shot power, agility, etc., enabling athletes to be filtered based on the qualities they possess. The result is a player profile that is stored in the database for potential selection by sports clubs.
* Biomechanical analysis: Implementing the analysis service using MediaPipe Pose to detect the 33 key points (landmarks) of the human body and interpret them depending on the exercise.
* High-performance backend: Developing a robust API using FastAPI and securing routes through the JWT (JSON Web Token) standard.
* Communication efficiency: Optimizing data transfer between the API service and the AI service using gRPC (Google Remote Procedure Call).
* Automatic scoring: Creating an algorithm for assigning ratings to physical attributes (speed, shooting, passing) based on extracted data.


### Problems the app solves:
TalentBridge wants to help football teams that are finding it increasingly difficult to find players compatible with their needs, but also players who are having a hard time getting noticed by teams.


### Features
The TalentBridge system architecture was built in a modular way, following the principles of a microservices-based architecture. As shown in Figure 1, the system consists of 3 distinct microservices: Auth Service: manages user identity and issues JWT tokens. Core Service: handles HTTP requests and the application logic (microservice explained in detail in section 2). Analysis Worker: a background service that runs the complex computer vision algorithm. The components communicate asynchronously through a message queue. This decision was made out of the need to manage limited resources efficiently. Because of the heavy data processing that takes place during a video analysis, when a large number of users
upload a video at the same time, the server would not operate within good parameters, producing high latency. Using a message queue (implemented with Redis) brings the following benefits to the system: Analyzing a video clip with processing algorithms (MediaPipe) is a time-consuming process. In a synchronous (Request - Response) architecture, the user would have to wait with the application blocked until the analysis is completed. By doing this, the API only confirms receipt of the file (202 Accepted), freeing the user interface, while the heavy processing takes place in the background, asynchronously.
<div align="center">
  <img width="540" height="540" alt="Untitled" src="https://github.com/user-attachments/assets/96ebb6e9-ec82-484c-8ae3-32f4ef543e4a" />
</div>
<br>

The analysis model is a costly operation (CPU-intensive). A synchronous (blocking) approach would have led to high response times for users. To solve this problem, I implemented the Producer-Consumer model using Redis as a message broker. The flow is as follows: The user (the athlete) uploads the challenge video via the POST/upload route. The Core Service saves the file to a directory, places a task in the Redis queue, and returns the HTTP 202 Accepted code to the athlete. The worker, which listens to the message queue, picks up the task as soon as it has free resources and starts the MediaPipe analysis. The result is then written to the database.
<div align="center">
  <img width="830" height="590" alt="Untitled2" src="https://github.com/user-attachments/assets/739e9d3d-fbba-4e80-a2d7-e6a60d025176" />
</div>
<br>

### Database Tables

* **users**: Stores authentication data, keeping fields such as email, password, and the user's role within the application.
* **athlete**: When a user creates an athlete account, they complete a profile with data for this table (e.g., age, field position, country of origin, height). These details are used in the player search process based on specific filters.
* **attribute**: Contains physical and technical data such as acceleration, finishing, agility, etc. These are initialized to 0 upon account creation and are updated with the extracted values after video analyses are completed.
* **challenge**: Stores the types of challenges that athletes can complete. This table can only be modified by an administrator.
* **challenge_result**: Stores the scores obtained by athletes for each challenge. A challenge result cannot be overwritten unless more than 3 months have passed since the last completed challenge of the same type.
* **football_club**: Stores information related to football clubs that register on the platform to carry out their scouting process.
* **trial**: Represents the selection events organized by clubs. It stores the application deadline (until_date), general info, and specific requirements (saved in JSON format to allow for flexible, dynamic filtering).
* **trial_applications**: Manages the actual enrollments, linking an athlete to a specific trial organized by a club.
* **favorite_athlete**: Acts as a shortlist for clubs, allowing scouts to save players of interest by storing the club ID and the athlete ID.

### Relationships Between Tables

* The relationships between the **users** table and the **athlete** / **football_club** tables are 1-to-1. The foreign keys are established using the primary key id from the users table (mapped to user_id), ensuring each account is uniquely associated with either an athlete or a club profile.
* The **athlete** table has a 1-to-1 relationship with **attribute**, since an athlete has a single set of attributes. It also has a 1-to-n (one-to-many) relationship with **hallenge_result**, as an athlete can have multiple challenge results recorded over time.
* The **challenge** table has a 1-to-n (one-to-many) relationship with **challenge_result**, because a specific challenge can be completed by multiple athletes.
* The relationship between **football_club** and **trial** is 1-to-n (one-to-many), as a football club can organize and post multiple trials.
* The relationship between **trial** and **athlete** is many-to-many (n-to-m), managed by the junction table **trial_applications**. An athlete can apply to multiple trials, and a trial can receive applications from multiple athletes.
* The relationship between **football_club** and **athlete** for scouting purposes is also many-to-many (n-to-m), handled by the **favorite_athlete** junction table. A club can shortlist multiple athletes, and an athlete can be favorited by multiple clubs.
<div align="center">
  <img width="1526" height="863" alt="DB" src="https://github.com/user-attachments/assets/651f504c-03f3-4e63-a190-15ad489da99c" />
</div>
<br>


### Requirements
To run and develop this project locally, you will need the following installed on your PC:

* **[Docker](https://docs.docker.com/get-docker/)** (și Docker Compose, care vine integrat în Docker Desktop)
* **[Git](https://git-scm.com/)** (pentru a clona repository-ul)

### Installation

1. **Clone the repository:**
```
git clone https://github.com/vasilca-rares-mihai/TalentBridge.git
cd TalentBridge/src/service
```

2. **Build and start the services**
Use Docker Compose to start the entire system (API, Redis, Database, Worker) in the background:
```
docker compose up --build -d
```

3. Check the status of the containers:
```
docker compose ps
```

4. Start/Stop containers
```
docker compose start
docker compose stop
```

### Usage
**Unauthenticated:**
* POST/api/unauthenticated/create/first_admin - creates the first admin account when no other account of this type exists in the database
* POST/api/unauthenticated/create/athlete - creates an athlete account 
* POST/api/unauthenticated/create/football_club - creates a football club account
* POST/api/unauthenticated/login - login; returns a jwt token used for auth
* POST/api/unauthenticated/logout - logout; add to blacklist jwt token

**User:**
* PUT/api/user/update/email - update a user's login email
* PUT/api/user/update/password - update a user's login password

**Admin:**
* POST/api/create/admin - create an admin account
* POST/api/create/challenge - create a new challenge
* DELETE/api/delete/challenge/{challenge_id} - delete a challenge
* DELETE/api/delete/wipe - Delete db input
* DELETE/api/admin/delete/account - delete user account

**Admin & Football Club:**
* POST/api/athletes - get all athletes from db
* POST/api/football_club/search/athlete - search an athlete by filters

**Athlete & Football Club:**
* GET/api/athlete/me - return user info
* GET/api/athlete/attributes/me - return my attributes
* GET/api/athlete/all_trials - get all trials
* DELETE/api/football_club/delete/football_club/{user_id} - delete football_club

**Athlete:**
* PUT/api/athlete/update/me - update user info
* POST/api/athlete/video/upload - upload video
* GET/api/athlete/video/display/{result_id} - returns the processed video (analyzed video)
* POST/api/athlete/video/analyze - run analysis
* GET/api/athlete/challenge_result/{challenge_id} - get challenge result
* GET/api/athlete/challenge_results - get all challenges results
* DELETE/api/athlete/delete/athlete/{user_id} - delete user/athlete/attribute
* GET/api/athlete/challenges - returns challenges. index = 0 for all challenges. index = 1 for uncompleted challenges. index = 2 fro completed challenges
* GET/api/athlete/challenges/{challenment_id}/leaderboard - leaderboard
* POST/api/athlete/trial/apply/{id_trial} - apply for a trial
* DELETE/api/athlete/delete/trial/application/{id_trial} - delete a trial application
* PUT/api/athlete/update/attributes - update user attributes


**Football Club:**
* GET/api/football_club/compare/athletes - compare 2 athletes
* POST/api/football_club/scouting/watchlist/{athlete_id} - add to watchlist
* DELETE/api/football_club/scouting/watchlist/{athlete_id} - delete from watchlist
* POST/api/football_club/publish/tria - add to trial table
* DELETE/api/football_club/delete/trial - delete from trial table
* GET/api/football_club/my_trials - get all trials
* GET/api/football_club/trial/applications/{id_trial} - get trial application


### RESULTS AND EXPERIMENTAL VALIDATION
A. Testing scenario For the testing part, I used test videos with a resolution of 480p at 30fps, with the tests run on the local machine.

B. Visual results shows how the analysis is performed. The athlete can view their video with the MediaPipe skeleton overlaid.

<img width="300" height="300" alt="71493d3efc96b15bd12aeab8d32d97b18f3a7656 " src="https://github.com/user-attachments/assets/a2848af9-d6fe-4879-bc8f-4e97ea5d8db8" />
<img width="450" height="300" alt="cec15d7709baa1ee4f4338905280913f30f08625" src="https://github.com/user-attachments/assets/1115bdca-a501-43bb-a146-7cd37742c901" />

The chart represents the evolution of the knee angle in each frame analyzed by the algorithm. On the X axis, the frames are shown, while on the Y axis, the angles formed by the quadriceps and the shin are plotted.

C. Performance
To validate the system’s scalability, I performed repeated measurements on datasets with progressively longer durations. The table below presents the execution times obtained in the test environment (CPU only)

| Video duration | Processing time | Load factor |
|:--------------:|:---------------:|:-----------:|
| 10s            | 13.46s          | 1.34x       |
| 20s            | 25.50s          | 1.27x       |
| 30s            | 37.88s          | 1.26x       |
| 60s            | 75.75s          | 1.26x       |
| 100s           | 124.50s         | 1.24x       |



### Opinions of experienced professionals in the field

Micu Bogdan, Video Analyst at Hagi Academy
```
Question: What matters more in the beginning: technical qualities (ball touch, dribbling, passing) or physical qualities (speed, endurance, coordination)? 
Answer: "It's a combination of both elements. However, I would tip the scales towards technical qualities because you can still work on the physical side."

Question: Do you use a scoring system or more of a subjective evaluation based on experience? 
Answer: "Technical and physical tests, and we draw conclusions based on expertise grounded in experience and video footage."
```
Youth Coach at FCSB (ANONYMOUS)
```
Question: What are the main criteria you look for when you see a child for the first time?
Answer: "The main criterion is intelligence and the capacity for intrinsic motivation."

Question: What types of exercises or tests do you use to evaluate children's abilities?
Answer: "Tests on motor qualities and motor skills."

Question: What matters more in the beginning: technical qualities (ball touch, dribbling, passing) or physical qualities (speed, endurance, coordination)?
Answer: "Speed, coordination, and striking the ball are important for the start."

Question: Do you use a scoring system or more of a subjective evaluation based on experience?
Answer: "Empirical evaluation is not necessarily the correct one."

Question: How do you observe or evaluate these aspects in children?
Answer: "Psychological tests and/or attitude in matches and training."

Question: Is the child's attitude important in the selection stage, or is it developed during sports development?
Answer: "It is important at selection, and if they pass the selection, then an improvement of all training factors follows."

Question: What criteria do you consider when deciding whether a child is better suited for a large club or a smaller one?
Answer: "There is no such criterion; the club where they go for selection decides whether to keep them or not."
```
Turcu Lucian Dan, Physical Trainer at Universitatea Cluj, Liga1 Romania Team
```
Question: What types of exercises or tests do you use to evaluate athletes' abilities?
Answer: "To evaluate athletes physically, we use a set of periodic tests that start in the Pre-Competitive period and are repeated monthly or every 6 weeks. To test Work Capacity, we use one of the '30-15' tests, the YO-YO Intermittent Recovery test, or the 5-minute Test. We use FMS to evaluate mobility. For strength, we use a device called an Encoder which shows the athlete's explosive strength and estimates maximal strength. To see maximal speed, we use the GPS system which shows the athlete's maximal speed and sprint meters.
From a technical-tactical point of view, the athlete is evaluated during training and matches, and certain points are tracked. The cognitive part is very important: how quickly they adapt to new situations arising in training, what solutions they find, how they respond to the coaches' instructions, and how quickly they assimilate information. However, there are certain tests used in Football Academies during the formation period. Examples: Cognitive and perception-decision tests, the mentioned physical tests, technical tests, psychological and behavioral tests, growth and biological maturity tests."

Question: What matters more in the beginning: technical qualities (ball touch, dribbling, passing) or physical qualities (speed, endurance, coordination)?
Answer: "In the (optimal) learning period, the most important are cognitive and psycho-social qualities. Another very important component is the understanding of the game of football (decision-making)."

Question: Do you use a scoring system or more of a subjective evaluation based on experience?
Answer: "In the personal development files, there is both an objective score (e.g., physical tests) and a subjective score (e.g., understanding the game and instructions). Considering that an athlete in the formation period does not have linear development, it is wrong to assign only grades. (See cases of famous footballers who were rejected in the past because they had poor results or parameters in certain tests. Yet they went on to achieve significant performance)."

Question: How do you observe or evaluate psychological and attitude aspects in athletes?
Answer: "Interpretable. As I mentioned above, we aim to set clear tasks and objectives. Through video analysis, we can see much more accurately whether these tasks are fulfilled. The analysis is done predominantly 'in the office' and not on the field. Following video analysis, we draw conclusions, set training objectives, and help athletes develop."

Question: How important do you consider visual feedback (graphs, slow-motion clips) for athlete development?
Answer: "If we are talking about motor skills, it is very difficult to change an athlete's movement pattern without knowing what determines them to move in that way. That is why we concretely test mobility, flexibility, muscular imbalances, the agonist-antagonist muscle ratio. From this, we can draw fairly clear conclusions. For example, an athlete who runs with their toes turned outward may have hyperactive gluteus medius muscles and hypoactive adductors (this is just an example). You will not be able to correct their movement unless you intervene on these imbalances. For this reason, we do not rely on images and movement patterns. The running biomechanics of Cristiano Ronaldo are different from Messi's and Usain Bolt's. Is any of them wrong? Probably not; they are just adapted to the needs of each."

Question: Can you tell me some simple tests through which you extract some attributes?
Answer: "It is possible to extract some valuable information even from a slow-motion video. I'll give you an example. If an athlete is very prone to injuries despite all the tests I mentioned being within normal parameters, it is possible that these injuries are due to running biomechanics. During slow-motion running, I would look very closely at: hip flexion (if they lift the thigh sufficiently), knee extension before ground contact, dorsi-flexion at the moment the foot pushes off the ground, spine and shoulder position, if the hip internally rotates when the foot touches the ground."
```

### So far:
Exercise Evaluation: The system analyzes a range of exercises, including:
```
-Push-ups
-Squats
-Pull-ups
-Treadmill Running
-Vertical Jumps
```



