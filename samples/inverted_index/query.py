from rich import print
import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ts_type_filter import Index
import sonnets

def go(query):
  # Create an index
  index = Index()

  # Add sonnets to the index
  for sonnet in sonnets.sonnets:
    index.add(sonnet)

  # Perform a search
  results = index.match(query)

  # Display the results
  print(f"Search results for [bold green]'{query}'[/bold green]:")
  print(f"Found {len(results)} results:")
  print()

  for result in results:
    print(index.highlight(query, result))
    print()

  print(f"Total of {len(results)} results found.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python demo.py <query>")
    sys.exit(1)
  query = sys.argv[1]
  go(query)