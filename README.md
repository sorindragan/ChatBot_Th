[![Build Status](https://travis-ci.com/sorindragan/intelligent-assistant-agent.png)](https://travis-ci.com/sorindragan/intelligent-assistant-agent)

## Intelligent Assistant Agent

Usage Example:

1)
```python
> from sentence_processor import SentenceProcessor
> phrase = "The tomato, which is one of the most popular salad ingredients, grows in many shapes and colors in greenhouses around the world."
> sp = SentenceProcessor(phrase)
> sp.process()
```
2)
```python
> from conversation import Conversation
> c = Conversation()
> c.process("Man acts as though he were the shaper and master of language while, in fact, language remains the master of man.")
```
