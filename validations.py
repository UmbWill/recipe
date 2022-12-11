
SOLVERS = ["JijSASampler", # Simulated annealing sampler implemented by Jij.
            "JijSQASampler", #Simulated quantum annealing sampler implemented by Jij.
            "JijSwapMovingSampler", #Simulated annealing sampler with satisfying n-hot constraint conditions implemented by Jij.
            "JijQIOSASampler", #Simulated annealing sampler using one of Microsoft QIO.
            "JijQIOSQASampler", #Simulated quantum annealing sampler using one of Microsoft QIO.
            "JijQIOPASampler", #Sampler using the population annealing of Microsoft QIO.
            "JijQIOPTSampler", #Sampler using the parallel tempering of Microsoft QIO.
            "JijQIOSSMCSampler", #Sampler using the substochastic monte carlo method of Microsoft QIO.
            "JijQIOTBSampler", #Sampler using the tabu search of Microsoft QIO.
            "JijDA3Sampler", #Sampler using Fujitsu Digital Annealer version 3.
            "JijDA4Sampler", #Sampler using Fujitsu Digital Annealer version 4.
            "JijLeapHybridCQMSampler", #Sampler using Leap’s Hybrid Solvers.
            "JijFixstarsAmplifySampler", #Sampler using Fixstars Amplify. 
            ]

def _validation_solver(input_solver):
    if input_solver in SOLVERS:
        return True
    else:
        return False