---
language: 
- en
- ar
tags:
- islamic-ai
- chatbot
- conversational
- islamic-qa
- hadith
- quran
- authentic-islamic-knowledge
license: apache-2.0
datasets:
- authentic-islamic-dataset
metrics:
- authenticity_threshold: 0.85
pipeline_tag: conversational
---

# BudulGPT Enhanced - Authentic Islamic AI Chatbot

## Model Description

BudulGPT Enhanced is an Islamic AI chatbot trained on authentic Islamic sources with high authenticity standards. The model provides accurate Islamic guidance based on verified sources from multiple Islamic schools of thought (madhabs).

## Model Details

- **Model Type**: Conversational AI for Islamic Q&A
- **Version**: 2.0 Enhanced
- **Languages**: English, Arabic
- **Enhancement Date**: 2025-08-15T08:14:38.112142
- **Authenticity Threshold**: 0.85
- **Training Examples**: 6

## Features

- ✅ **Authentic Islamic Knowledge**: Based on verified sources
- ✅ **Multi-Madhab Coverage**: Hanafi, Maliki, Shafii, Hanbali
- ✅ **Hadith References**: Includes authentic hadith citations
- ✅ **Quran Integration**: Quranic verses with proper references  
- ✅ **Arabic Support**: Native Arabic text handling
- ✅ **High Authenticity**: 0.85 authenticity threshold

## Madhabs Covered

- **Hanafi**: Predominant in Central Asia, Turkey, India
- **Maliki**: Predominant in North/West Africa
- **Shafii**: Predominant in East Africa, Southeast Asia
- **Hanbali**: Predominant in Saudi Arabia

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model
tokenizer = AutoTokenizer.from_pretrained("yussufabdi/budul-gpt-enhanced")
model = AutoModelForCausalLM.from_pretrained("yussufabdi/budul-gpt-enhanced")

# Ask an Islamic question
question = "What are the five pillars of Islam?"
input_text = f"Human: {question}\nBudulGPT:"
input_ids = tokenizer.encode(input_text, return_tensors='pt')

# Generate response
output = model.generate(
    input_ids,
    max_length=input_ids.shape[1] + 150,
    temperature=0.7,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)
```

## Example Conversations

### Five Pillars of Islam
**Human**: What are the five pillars of Islam?
**BudulGPT**: The five pillars of Islam (أركان الإسلام) are:

1. **Shahada** (الشهادة) - Declaration of Faith
2. **Salah** (الصلاة) - Five daily prayers  
3. **Zakat** (الزكاة) - Obligatory charity
4. **Sawm** (الصوم) - Fasting during Ramadan
5. **Hajj** (الحج) - Pilgrimage to Mecca

These pillars form the foundation of Islamic practice and worship. والله أعلم

### Wudu (Ablution)
**Human**: How do I perform wudu?
**BudulGPT**: Wudu (الوضوء) steps:

1. Make intention (niyyah)
2. Say Bismillah
3. Wash hands 3 times
4. Rinse mouth 3 times
5. Clean nose 3 times
6. Wash face 3 times
7. Wash arms to elbows 3 times
8. Wipe head once
9. Wipe ears once
10. Wash feet to ankles 3 times

The Prophet (ﷺ) said: "Cleanliness is half of faith." [Sahih Muslim]

## Authenticity & Sources

This model is trained on authentic Islamic sources with rigorous verification:

- **Primary Sources**: Quran, Sahih Hadith collections
- **Scholarly Sources**: Ibn Baz Foundation, authenticated Islamic websites
- **Verification Process**: Multi-madhab cross-referencing
- **Quality Control**: 0.85 authenticity threshold

## Limitations

- Responses are for general guidance only
- Complex jurisprudential issues should be referred to qualified scholars
- Model output should be verified with authentic Islamic sources
- Not a replacement for consulting knowledgeable Islamic scholars

## Ethical Considerations

- Trained exclusively on authentic Islamic sources
- Respects Islamic principles and values
- Promotes understanding between different madhabs
- Encourages seeking knowledge from qualified scholars

## License

This model is released under the Apache 2.0 license.

## Citation

```bibtex
@misc{budulgpt-enhanced-2025,
  title={BudulGPT Enhanced: Authentic Islamic AI Chatbot},
  author={Yussuf Abdi},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/yussufabdi/budul-gpt-enhanced}
}
```

## Contact

For questions or feedback about BudulGPT Enhanced, please reach out through the Hugging Face model page.

---

*"And say: My Lord, increase me in knowledge." - Quran 20:114*

والله أعلم (And Allah knows best)
