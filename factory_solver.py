import datetime
import time
import asyncio
import json
from common.extensions import cache

def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.new_event_loop().run_in_executor(None, f, *args, *kwargs)

    return wrapped

class FactorySolver:

    def set_parameters(self, result_key, json_solver_request):
        '''set parameters for factory solver

        Args:
        - result_key: string
        - json_solver_request: json
       
        '''
        self.result_key = result_key
        self.json_solver_request = json_solver_request
    
    @fire_and_forget
    def solver(self):
        cur_solver = self._get_solver(self.json_solver_request["solver"]) #JijSASampler
        cur_solver()

    def _get_solver(self, solver_type):
        '''call the right solver based on input request

        Args:
        - solver_type: string
        
        Return:
        - solver function

        '''
        do = f"_solver_{solver_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func()
    
    def _solver_JijSASampler(self):
        '''Simulated annealing sampler implemented by Jij.'''
        self._mock_solver()

    def _solver_JijSQASampler(self):
        '''Simulated quantum annealing sampler implemented by Jij.'''
        self._mock_solver()

    def _solver_JijSwapMovingSampler(self):
        ''' Simulated annealing sampler with satisfying n-hot constraint conditions implemented by Jij.'''
        self._mock_solver()

    def _solver_JijQIOSASampler(self):
        '''Simulated annealing sampler using one of Microsoft QIO.'''
        self._mock_solver()

    def _solver_JijQIOSQASampler(self):
        '''Simulated quantum annealing sampler using one of Microsoft QIO.'''
        self._mock_solver()

    def _solver_JijQIOPASampler(self):
        '''Sampler using the population annealing of Microsoft QIO.'''
        self._mock_solver()

    def _solver_JijQIOPTSampler(self):
        '''Sampler using the parallel tempering of Microsoft QIO.'''
        self._mock_solver()

    def _solver_JijQIOSSMCSampler(self):
        '''Sampler using the substochastic monte carlo method of Microsoft QIO.'''
        self._mock_solver()

    def _solver_JijQIOTBSampler(self):
        '''Sampler using the tabu search of Microsoft QIO.'''
        self._mock_solver()
    
    def _solver_JijDA3Sampler(self):
        '''Sampler using Fujitsu Digital Annealer version 3.'''
        self._mock_solver()

    def _solver_JijDA4Sampler(self):
        '''Sampler using Fujitsu Digital Annealer version 4.'''
        self._mock_solver()

    def _solver_JijLeapHybridCQMSampler(self):
        '''Sampler using Leap’s Hybrid Solvers.'''
        self._mock_solver()

    def _solver_JijFixstarsAmplifySampler(self):
        '''Sampler using Fixstars Amplify.'''
        self._mock_solver()
    
    def _mock_solver(self):
        '''Mock solver for test.'''

        try:
            self._set_KV_value("PENDING", "No errors", None)
            cache.set(str(self.result_key), self.json_solver_request)
            #delay for PENDING test
            for i in range(10):
                time.sleep(1)
                print(i, flush=True)
                self.json_solver_request["heartbeat"] = int(datetime.datetime.now().timestamp()) 
                cache.set(str(self.result_key), self.json_solver_request)


            type(self.result_key) 

            test_case = self.json_solver_request["parameters"]["test_case"]
            instance = cache.get(str(self.json_solver_request["instance_key"]))
            if test_case == "SUCCESS":
                self._set_KV_value("SUCCESS", "No errors", instance["instance_data"]["points"])
            elif test_case == "FAILED":
                self._set_KV_value("FAILED", "Solver failed: ... ", None)
            cache.set(str(self.result_key), self.json_solver_request)
        except Exception as e:
            # log somewhere the error
            self._set_KV_value("FAILED", repr(e), None)
            cache.set(str(self.result_key), self.json_solver_request)
        
    def _set_KV_value(self, status, message, result):
        '''Set value in json for KV.'''

        self.json_solver_request["status"] = status
        self.json_solver_request["message"] = message
        self.json_solver_request["result"] = result
        self.json_solver_request["heartbeat"] = int(datetime.datetime.now().timestamp()) 
