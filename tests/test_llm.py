import time
# Note the dot notation if you're running from the backend root
from tools.LLM import call_local_llm 

def run_test():
    print("Testing...")
    result = call_local_llm("Hi", mode="short")
    print(result)

if __name__ == "__main__":
    run_test()