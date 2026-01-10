from browser import search_web

print("Starting search test...\n")

results = search_web("LLM models", max_results=5, time_range="recent")

print(f"\n{'='*60}")
print(f"TOTAL RESULTS: {len(results)}")
print('='*60)

if results:
    for i, r in enumerate(results, start=1):
        print(f"\n[{i}] {r['title']}")
        print(f"     {r['url']}")
        print(f"     {r['snippet'][:150]}...")
else:
    print("\n⚠ No results found.")