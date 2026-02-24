print("Importing...")
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    print("Imported.")
    print("Instantiating...")
    search = DuckDuckGoSearchRun()
    print("Instantiated.")
    print("Running search...")
    res = search.run("execution in python")
    print("Result:", res[:100])
except Exception as e:
    import traceback
    traceback.print_exc()
