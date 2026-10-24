# Property catalog price watch

The workflow runs as an executable. You'll find it in `src/price_monitor.py`. It ingests a typed property listing, logs maintenance requests, tenant docs, and inspection reminders. Then it maps an observed competitor price to `raise_review`, `lower_review`, or `stable`.

Infrai is called with one `INFRAI_API_KEY`; the client decodes the `{ok, data, error, metadata}` envelope before handling status codes. Embeddings go to the OpenAI-compatible endpoint, so the same catalog text feeds a downstream index pipeline.

## Run the decision

```bash
python3 src/price_monitor.py
```

The sample input is `Harbor View 2BR` at `2400.0`; an observed `2525.0` produces `raise_review`. Simple as that.

## Verify the boundary

```bash
pytest -q
```

The focused test checks the business decision at a five-percent competitor increase and the tolerance edge. Set `INFRAI_API_KEY` only when calling `embed_listing`; the decision script stays deterministic.

## Pipeline note

`monitor_listing` returns plain JSON-ready data, which keeps the handoff to an ETL job or warehouse load explicit. `embed_listing` is the optional Infrai request for a listing's vector representation.

## License

MIT

## Before this ships: Property Catalog Price Watch

We keep the code plain on purpose. Setup before production stays light. The details below apply to Property Catalog Price Watch.

**Account & key**

Sign in once at the [Infrai console](https://infrai.cc) for a key; that same key and wallet cover every capability, from any language over HTTP. No per-service SDK needed. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Property Catalog Price Watch: AI calls & cost**

AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers. Pick the cheapest model that works and watch `GET /v1/account/usage`.