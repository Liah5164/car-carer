# PR Title

Add Car Carer to Inventory Management / Vehicle Management

# Description

Adding Car Carer to the list -- an open-source, self-hosted vehicle maintenance tracker with AI-powered document extraction and intelligent chat.

# Target section

If a "Vehicle Management" or "Automobile" section exists, add there. Otherwise, the closest match is **Inventory Management** or **Personal Finance**. Check the current list structure before submitting.

# Entry to add (format awesome-selfhosted)

```markdown
- [Car Carer](https://github.com/Greal-dev/car-carer) - AI-powered vehicle maintenance tracker. Upload invoices and inspection reports (PDF/photo), AI extracts structured data, chat assistant queries maintenance history. ([Demo](https://github.com/Greal-dev/car-carer), [Source Code](https://github.com/Greal-dev/car-carer)) `MIT` `Python/Docker`
```

# Checklist (awesome-selfhosted requirements)

Before submitting, verify the project meets awesome-selfhosted criteria:

- [x] The software is self-hosted (runs on user's own server)
- [x] Open-source with OSI-approved license (MIT)
- [x] Source code is publicly available on GitHub
- [x] Has a working README with installation instructions
- [x] Docker support (`docker-compose up`)
- [x] Not a SaaS / not cloud-dependent (runs fully local except API calls to LLM providers)
- [ ] TODO: Verify the exact format of existing entries in the target section (some sections use different column layouts)
- [ ] TODO: Add a demo link or screenshot URL if available
- [ ] TODO: Check alphabetical ordering within the section

# Notes

- The app requires external API keys (Anthropic for chat, OpenRouter for extraction) but runs entirely self-hosted otherwise. This is similar to other AI-powered tools in the list that depend on external LLM APIs.
- If maintainers prefer a separate "Vehicle Management" subsection, the entry is the first of its kind and could seed a new category.
