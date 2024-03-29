

The Handhsake server is the component that all devices have knowledge of existence  
Every other component pings to it and requests connection via it , the data transfer between the components are peer to peer  

Backend Server handles the processing taks and orchestrating agents - store audio , transcribe and summarize and embed , start agent tasks ( todo , calendar , etc ) ,  agent to make conversations ~ via a seperate telegram bot hosted in the backend itself [ FUTURE IDEA ]  

python pendant client is the actual client that records and tramsits audio to the backend server  
python telegram client is a software level iteration of the pendant logic  

python web console is the dashboard to see all the audio transcription and play through your voice  

# TODO
- paginate lists view
- telegram bot sends audio
- build transcription summarization embedding queue and update db
- OPTIONAL : build delegation model queue and tasks and calendar list db tables and working memory of user info or context ( personality , pref , things to remember , etc )
- rework networking ( @aasish )
