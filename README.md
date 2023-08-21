##### FissionBot Rest-API
Please run this command to install required packages in your local
<ul>
<li>For chromadb installation please run in your linux environment:  <b>export HNSWLIB_NO_NATIVE=1</b></li>
<li><b>pip install -r requirements.txt</b></li>

</ul>

There are 3 components in it<br>
<ul>
<li>Azure QnA Maker</li>
<ul>
<li>We have some frequently asked <b>questions cached</b> in QnA maker.</li>
<li>Multiple <b>variations of same question</b> are updated.</li>
<li>If there is a chance of <b>follow-up questions</b> called as <b>prompts</b>.</li>
<li><b>Source urls</b> are also added as metadata.</li>
<li>If a question isn't available in QnA Maker we get <b>No answer Found</b>.</li>
<li>This is pretty much <b>dictionary approach</b> with <b>questions consine similiary score</b> which we set while initializing.</li>
<li>We also need to keep <b>updating</b>> based on most <b>frequently un-answered questions</b> by <b>QnA Maker</b>, and <b>answered by OpenAI</b>.</li>
</ul>
<br>
<li>OPENAI</li>
<ul>
<li>We are loading all the URLS through <b>src.__init__ URLS variable</b> We need keep frequently updating as new endpoints are added to our website.</li>
<li>If questions are un-answered by QnA Maker we hit OpenAI.</li>
<li>We store both QnA Maker & OpenAI answer using ConversationBufferMemory.</li>
<li>Please feel free to further <b>fine-tune prompt</b> if the requirements change.</li>
<li>Try to use <b>ConversationBufferMemory</b> as well, I tried it wasn't working as expected in the given time frame. It would use <b>chat history & context</b> to predict the current answer.</li>
<li><b>Commented of OpenAI code as we are asked to not use for now, Please feel free to un-comment the lines in src/generic_qa.py to use</b></li>
</ul>
<br>
<li>MySql</li>
<ul>
<li><b>SessionId</b> is the primarty Key</li>
<li>DB Schema, SessionId, start_timestamp, update_timestamp, conversation.</li>
<li>We are storing the ConversationBufferMemory as binary in sql.</li>
<li>If sessionId isn't created we create and store both question and answer in db.</li>
<li><b>Creating required table:</b></li>
<ul> 
<li>CREATE TABLE chat_bot(sessionId VARCHAR(255) PRIMARY KEY,
start_timestamp timestamp default current_timestamp not null,
update_timestamp timestamp default current_timestamp not null,
conversation BLOB(65534));</li>
</ul>
<li>If <b>sessionId</b> is there in <b>input as well as db</b>. We update the <b>input and output to memory</b> reading the <b>blob</b>.</li>

</ul>
</ul>


#### To check if the service is up and running wrt local
GET URL: http://127.0.0.1:8000/
<br>
<br>
#### QnA endpoint and input parameters
POST URL: http://127.0.0.1:8000/question_answering <br>
JSON Input: <br>
{"question": "services","sessionId":"....."}<br>
<b>sessionId</b> is optional or give some default value for testing
<br>
Current Architecture
![Chat_arcihtecture drawio](https://github.com/flabdev/AI-ML/assets/8174596/30e4224e-c1c2-4e5a-b15e-7163873e9971)

