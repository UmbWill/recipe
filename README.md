<h1>TSP - API Solver</h1>

<p>This is a simple API in Flask & Redis</p>

<h2>Public API</h2>
<p>
<ul>
    <li><em>post_instance</em></li>
    <li><em>solver_request</em></li>
    <li><em>mock_pending</em></li>
</ul>
</p>
<h3>POST instance</h3>
<p>The endpoint POST post_instance receives the problem instance and store it in Redis cache, returning the instance_key.
<br>
Valid input: 
<code>{"type": string,
"instance_data": json}.</code>
<br>
Success output: 
</code>{"instance_key":string}</code></p>
:warning:instance_data value must contain a key "points" with as value a list of strings (see example below).
</p>

<h3>POST solver request</h3>
<p>The endpoint POST solver_request receives the problem parameters and call the right solver.
<br>
Valid input: 
<code>{
    "instance_key": string,
    "solver": string,
    "parameters": json
}.</code>
<br>
Success output: 
</code>{"result_key":string}</code></p>
:warning:parameters value could contain a key "test_case", to test the three cases:
  <ul>
    <li>"SUCCESS"</li>
    <li>"FAILED"</li>
    <li>"PENDING"</li>
  </ul>
</p>
:warning:solver could be:
<ul>
  <li><b>JijSASampler</b>, Simulated annealing sampler implemented by Jij.</li>
  <li><b>JijSQASampler</b>, Simulated quantum annealing sampler implemented by Jij.</li>
  <li><b>JijSwapMovingSampler</b>, Simulated annealing sampler with satisfying n-hot constraint conditions implemented by Jij.</li>
  <li><b>JijQIOSASampler</b>, Simulated annealing sampler using one of Microsoft QIO.</li>
  <li><b>JijQIOSQASampler</b>, Simulated quantum annealing sampler using one of Microsoft QIO.</li>
  <li><b>JijQIOPASampler</b>, Sampler using the population annealing of Microsoft QIO.</li>
  <li><b>JijQIOPTSampler</b>, Sampler using the parallel tempering of Microsoft QIO.</li>
  <li><b>JijQIOSSMCSampler</b>, Sampler using the substochastic monte carlo method of Microsoft QIO.</li>
  <li><b>JijQIOTBSampler</b>, Sampler using the tabu search of Microsoft QIO.</li>
  <li><b>JijDA3Sampler</b>, Sampler using Fujitsu Digital Annealer version 3.</li>
  <li><b>JijDA4Sampler</b>, Sampler using Fujitsu Digital Annealer version 4.</li>
  <li><b>JijLeapHybridCQMSampler</b>, Sampler using Leap’s Hybrid Solvers.</li>
  <li><b>JijFixstarsAmplifySampler</b>, Sampler using Fixstars Amplify.</li> 
</ul>

<h3>GET solver request</h3>
<p>The endpoint GET solver_request return the status of the result_key instance.
<br>
Valid input: 
<code>{
    "result_key": string
}.</code>
<br>
Success output: 
  <ul>
    <li>"SUCCESS": </code>{"status":string, "result":json}</code></p></li>
    <li>"FAILED": </code>{"status":string, "message":string}</code></li>
    <li>"PENDING": </code>{"status":string}</code></li>
  </ul>
</p>

<h3>POST mock pending</h3>
<p>The endpoint POST mock_peding, change the status of the result_key instance into pending. This is useful to test the heartbeat system.
<br>
Valid input: 
<code>{
    "result_key": string
}.</code>
<br>
Success output: 
  </code>{"message": "Set status to pending."}</code>
</p>

<h2>How to run the container</h2>

<p>
  All the used packages are inside the requirements.txt
  Flask and Redis have been insert into Docker containers. 
  To build docker-compose with the command: 
  <code>
  docker-compose up --build
  </code>
</p>

<h2>How to run a test</h2>
<p>
    This is a possible sequence of operations to test the API:
    <ul>
    <li><code>curl -d "{\"type\":\"some_type\",\"instance_data\":{\"points\":[\"Saitama\",\"Tokyo\"]}}" -H "Content-Type:application/json" -X POST http://192.168.99.100:5000/post_instance </code></li>
    <br>Result:
     <ul><li><code>
      {"instance_key":"4055d2ad-44d5-38a7-8029-107fbff1a706"}
      </code></li></ul><br>
    <li><code>curl -d "{\"instance_key\":\"8f161a4a-4489-3f46-8323-642c6c3995a3\", \"solver\":\"JijSASampler\", \"parameters\":{\"test_case\":\"SUCCESS\"}}" -H "Content-Type:application/json" -X POST http://192.168.99.100:5000/solver_request </code></li>
    <br>Result: <ul><li><code>{"result_key": "7cb9f905-ba4e-3473-ba12-933c96de8452"}</code></li></ul><br>
    <li><code>curl -X GET http://192.168.99.100:5000/solver_request?result_key=7cb9f905-ba4e-3473-ba12-933c96de8452 </code>    </li>
    <br>Result:<ul><li><code>{
  "result": [
    "Saitama",
    "Tokyo"
  ],
  "status": "SUCCESS"
}</code></li></ul><br>
    
</ul>
<p>