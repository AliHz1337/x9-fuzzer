import argparse
import urllib.parse

# Function to print the banner
def banner():
    print()
    print(r"   _  __ ____          ______                             ")
    print(r"  | |/ // __ \        / ____/__  __ ____ ____  ___   _____")
    print(r"  |   // /_/ /______ / /_   / / / //_  //_  / / _ \ / ___/")
    print(r" /   | \__, //_____// __/  / /_/ /  / /_ / /_/  __// /    ")
    print(r"/_/|_|/____/       /_/     \__,_/  /___//___/\___//_/     ")
    print()
    print("                        Developed by @AliHz1337    ")
    print()
    print()


# Function to clean and decode URLs
def clean_url(url):
    url = urllib.parse.unquote(url)  # Decode URL-encoded characters
    url = url.replace('\\', '')      # Remove backslashes
    return url

# Function to load data from a file
def load_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to generate URLs based on 'normal' strategy
def generate_normal(links, values, parameters_file, chunk_size):
    results = []
    params = load_file(parameters_file)  # Load parameters from file

    for value in values:
        for link in links:
            clean_link = clean_url(link)
            url = urllib.parse.urlparse(clean_link)
            new_params = {param: [value] for param in params}
            new_query_items = list(new_params.items())

            # Chunk the parameters if necessary
            for i in range(0, len(new_query_items), chunk_size):
                subset_params = dict(new_query_items[i:i + chunk_size])
                new_query = urllib.parse.urlencode(subset_params, doseq=True)
                new_url = url._replace(query=new_query)
                results.append(urllib.parse.urlunparse(new_url))

    return results

# Function to generate URLs based on 'combine' strategy
def generate_combine(links, values, value_strategy, chunk_size):
    results = []
    
    for link in links:
        clean_link = clean_url(link)
        url = urllib.parse.urlparse(clean_link)
        query_params = urllib.parse.parse_qs(url.query)
        base_url = url._replace(query='')

        if value_strategy == 'replace':
            # Replace existing parameter values with new values
            for value in values:
                for param in query_params.keys():
                    new_query = query_params.copy()
                    new_query[param] = [value]
                    query_string = urllib.parse.urlencode(new_query, doseq=True)
                    new_url = base_url._replace(query=query_string)
                    results.append(urllib.parse.urlunparse(new_url))

        elif value_strategy == 'suffix':
            # Append new values to existing parameter values
            for value in values:
                for param in query_params.keys():
                    new_query = query_params.copy()
                    new_query[param] = [v + value for v in query_params[param]]
                    query_string = urllib.parse.urlencode(new_query, doseq=True)
                    new_url = base_url._replace(query=query_string)
                    results.append(urllib.parse.urlunparse(new_url))

    return results

# Function to generate URLs based on 'ignore' strategy
def generate_ignore(links, values, parameters_file, chunk_size):
    results = []
    params = load_file(parameters_file)  # Load parameters from file

    for value in values:
        for link in links:
            clean_link = clean_url(link)
            url = urllib.parse.urlparse(clean_link)
            base_query = urllib.parse.parse_qs(url.query)

            additional_params = {param: [value] for param in params if param not in base_query}
            combined_query = {**base_query, **additional_params}

            base_query_items = list(base_query.items())
            additional_query_items = list(additional_params.items())

            # Chunk the parameters if necessary
            for i in range(0, len(additional_query_items), chunk_size):
                subset = dict(base_query_items + additional_query_items[i:i + chunk_size])
                new_query = urllib.parse.urlencode(subset, doseq=True)
                new_url = url._replace(query=new_query)
                results.append(urllib.parse.urlunparse(new_url))

    return results

# Function to generate URLs based on 'all' strategy
def generate_all(links, values, parameters_file, value_strategy, chunk_size):
    results = []
    results.extend(generate_combine(links, values, value_strategy, chunk_size))
    results.extend(generate_ignore(links, values, parameters_file, chunk_size))
    results.extend(generate_normal(links, values, parameters_file, chunk_size))
    return results

# Main function to parse arguments and execute the script
def main():
    parser = argparse.ArgumentParser(description="URL Fuzzing Tool. Developed By Ali-Hz. https://x.com/AliHz1337")
    parser.add_argument('-u', '--url', help="Single URL")
    parser.add_argument('-l', '--url_list', help="File with links (not used with -u)")
    parser.add_argument('-gs', '--generate_strategy', required=True, choices=['ignore', 'combine', 'normal', 'all'], help="Generate strategy")
    parser.add_argument('-vs', '--value_strategy', choices=['replace', 'suffix'], help="Value strategy (required for 'combine')")
    parser.add_argument('-v', '--values_inline', nargs='*', help="Values provided inline")
    parser.add_argument('-vf', '--values_file', help="File with values (ignored if -vf is provided)")
    parser.add_argument('-p', '--parameters', help="File with parameters (required for 'ignore', 'normal', and 'all' strategies)")
    parser.add_argument('-c', '--chunk', type=int, default=25, help="Number of parameters per URL (default: 25)")
    parser.add_argument('-o', '--output', nargs='?', const='x9-generated-link.txt', help="File to save the output (default: x9-generated-link.txt)")
    parser.add_argument('-s', '--silent', action='store_true', help="Suppress banner")

    args = parser.parse_args()

    if not args.silent:
        banner()  # Print the banner if not in silent mode
    
    if args.url:
        links = [args.url]  # Use single URL if -u is provided
    elif args.url_list:
        links = load_file(args.url_list)  # Use URL list file if -l is provided
    else:
        raise ValueError("Either -l or -u must be provided")
    
    if args.values_inline:
        values = args.values_inline  # Use inline values if -v is provided
    elif args.values_file:
        values = load_file(args.values_file)  # Use values file if -vf is provided
    else:
        raise ValueError("Either -v or -vf must be provided")

    chunk_size = args.chunk

    if args.generate_strategy == 'ignore':
        if not args.parameters:
            raise ValueError("Parameters file is required for 'ignore' strategy")
        results = generate_ignore(links, values, args.parameters, chunk_size)
    
    elif args.generate_strategy == 'combine':
        if not args.value_strategy:
            raise ValueError("Value strategy is required for 'combine' strategy")
        results = generate_combine(links, values, args.value_strategy, chunk_size)

    elif args.generate_strategy == 'normal':
        if not args.parameters:
            raise ValueError("Parameters file is required for 'normal' strategy")
        results = generate_normal(links, values, args.parameters, chunk_size)
    
    elif args.generate_strategy == 'all':
        if not args.parameters:
            raise ValueError("Parameters file is required for 'all' strategy")
        if not args.value_strategy:
            raise ValueError("Value strategy is required for 'combine' strategy in 'all' strategy")
        results = generate_all(links, values, args.parameters, args.value_strategy, chunk_size)
    
    if args.output:
        with open(args.output, 'w') as file:
            for result in results:
                file.write(result + '\n')  # Write results to the specified output file
    
    # Print results to the terminal
    for result in results:
        print(result)

if __name__ == "__main__":
    main()
