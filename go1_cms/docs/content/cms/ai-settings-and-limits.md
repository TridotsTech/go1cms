# AI providers, keys and limits

**AI settings** in the admin sets which AI the site uses and how much people may use it.

## Providers

GO1 CMS calls OpenRouter, Groq, Gemini or DeepSeek through one connection that retries on rate limits and reports errors in plain words. OpenRouter gives access to many models with one key and has its own settings screen:

- **Model**: search OpenRouter's models by name or provider; free models are marked, and a custom model id is accepted.
- **API key**: write-only. The screen shows whether it is connected, and you can change or remove it.
- **Check**: test a key before relying on it. For OpenRouter the check also shows the credit left.
- **Max tokens**, **temperature** and **request timeout**.

Keys stay on the server and are never sent to the browser.

A developer machine can use the locally installed Claude Code CLI instead of a hosted provider.

## Other keys

The same screen holds the Pexels and Unsplash keys for stock photos, a Gemini key for image generation, and a Figma token for reading Figma links. The Image Studio plugin can set those per website instead.

## Who may use AI, and how much

- Only people with the **CMS AI User** role (and administrators) can use paid AI features.
- Limits: a daily budget per person, requests per person per hour, and a daily budget for the whole site.
- Every paid call is recorded with the person, the feature, the model, the tokens and the cost. The settings screen shows today's requests and images.
- When a limit is reached, the request is refused before any work starts, never halfway through a site build.

Non-administrators see the settings read-only.
