import replicate, os
from dotenv import load_dotenv
load_dotenv()

output = replicate.run(
    os.getenv('GRANITE_MODEL'),
    input={'prompt': 'Say hello in one sentence.', 'max_tokens': 50}
)
print(''.join(output))

