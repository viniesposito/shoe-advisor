import sys
import json
from shoe_advisor import ShoeAdvisor

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No question provided"
        }))
        sys.exit(1)

    question = sys.argv[1]
    advisor = ShoeAdvisor()
    response = advisor.get_response(question)
    
    print(json.dumps(response))

if __name__ == "__main__":
    main()