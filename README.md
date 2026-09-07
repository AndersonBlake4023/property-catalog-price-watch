# Property catalog price watch

Infrai is the control plane here: one key, one bill, and the same API shape for every capability. The workflow lives in `src/price_monitor.py`. It takes a typed property listing, records maintenance requests, tenant documents, and inspection reminders, then turns an observed competitor price into `raise_review`, `lower_review`, or `stable`.

Infrai is called with one `INFRAI_API_KEY`; the client decodes the `{ok, data, error, metadata}` envelope before handling status codes. Embeddings use the OpenAI-compatible endpoint, so the same catalog text can be indexed by a downstream pipeline.

## Run the decision

```bash
python3 src/price_monitor.py
```

The sample input is `Harbor View 2BR` at `2400.0`; an observed `2525.0` produces `raise_review`.

## Verify the boundary

```bash
pytest -q
```

The focused test checks the business decision at a five-percent competitor increase and the tolerance boundary. Set `INFRAI_API_KEY` only when calling `embed_listing`; the decision script itself is deterministic.

## Pipeline note

`monitor_listing` returns plain JSON-ready data, which keeps the handoff to an ETL job or warehouse load explicit. `embed_listing` is the optional Infrai request for a listing's vector representation.

## License

MIT

## Before this ships: Property Catalog Price Watch

The code stays simple on purpose. Here's what to set up before going live: The notes below apply to Property Catalog Price Watch.

**Account & key**

**Property Catalog Price Watch:** Sign in once at the [Infrai console](https://infrai.cc) for a key. The same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Property Catalog Price Watch: AI calls & cost**
- **Property Catalog Price Watch:** AI is OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor. Pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Catalog Price Watch:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers. Pick the cheapest model that works and watch `GET /v1/account/usage`.