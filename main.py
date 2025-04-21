#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
import sys
import argparse
import urllib.parse
from typing import List, Dict, Generator, Optional, Union, Iterable


class URLFuzzer:
    # A class to handle URL fuzzing operations with improved efficiency and error handling

    @staticmethod
    def print_banner() -> None:
        # Print the tool's banner
        print("", file=sys.stderr)
        print("    _  __ ____          ______ __  __ _____ _____    ______ ____ ", file=sys.stderr,)
        print("   | |/ // __ \\        / ____// / / //__  //__  /   / ____// __ \\", file=sys.stderr,)
        print("   |   // /_/ /______ / /_   / / / /   / /   / /   / __/  / /_/ /", file=sys.stderr,)
        print("  /   | \\__, //_____// __/  / /_/ /   / /__ / /__ / /___ / _, _/ ", file=sys.stderr,)
        print(" /_/|_|/____/       /_/     \\____/   /____//____//_____//_/ |_|  ", file=sys.stderr,)
        print("                                                                ", file=sys.stderr,)
        print("                        Developed by @AliHz1337    ", file=sys.stderr)
        print("\n", file=sys.stderr)
    
    def __init__(self, chunk_size: int = 25):
        # Initialize the URLFuzzer with chunk size
        self.chunk_size = chunk_size

    @staticmethod
    def clean_url(url: str) -> str:
        # Clean and decode a URL
        try:
            url = urllib.parse.unquote(url)  # Decode URL-encoded characters
            url = url.replace("\\", "")  # Remove backslashes
            return url
        except Exception as e:
            print(f"Error cleaning URL '{url}': {e}", file=sys.stderr)
            return url  # Return original URL if cleaning fails

    @staticmethod
    def load_file(filename: str) -> List[str]:
        # Load data from a file with error handling
        try:
            with open(filename, "r") as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        except (IOError, FileNotFoundError) as e:
            print(f"Error loading file '{filename}': {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def validate_url(url: str) -> bool:
        # Validate if a string is a proper URL
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def preprocess_urls(self, urls: List[str]) -> List[urllib.parse.ParseResult]:
        # Preprocess all URLs once to avoid redundant operations
        processed_urls = []
        for url in urls:
            clean_url = self.clean_url(url)
            if not self.validate_url(clean_url):
                print(
                    f"Warning: URL '{url}' appears to be invalid. Skipping.",
                    file=sys.stderr,
                )
                continue
            try:
                processed_urls.append(urllib.parse.urlparse(clean_url))
            except Exception as e:
                print(f"Error parsing URL '{url}': {e}", file=sys.stderr)
        return processed_urls

    def chunk_parameters(
        self, params: Dict[str, List[str]]
    ) -> Generator[Dict[str, List[str]], None, None]:
        # Chunk parameters efficiently using generators
        items = list(params.items())
        for i in range(0, len(items), self.chunk_size):
            yield dict(items[i : i + self.chunk_size])

    def generate_urls(
        self,
        strategy: str,
        urls: List[str],
        values: List[str],
        params_file: Optional[str] = None,
        value_strategy: Optional[str] = None,
    ) -> Generator[str, None, None]:
        # Generate URLs based on specified strategy
        # Preprocess URLs once
        processed_urls = self.preprocess_urls(urls)
        if not processed_urls:
            print("No valid URLs to process.", file=sys.stderr)
            return

        # Load parameters if needed
        params = []
        if params_file and strategy in ["ignore", "normal", "all"]:
            try:
                params = self.load_file(params_file)
            except Exception as e:
                print(f"Error loading parameters file: {e}", file=sys.stderr)
                return

        # Generate URLs based on strategy
        if strategy == "normal":
            yield from self._generate_normal(processed_urls, values, params)
        elif strategy == "combine":
            if not value_strategy:
                print(
                    "Value strategy is required for 'combine' strategy", file=sys.stderr
                )
                return
            yield from self._generate_combine(processed_urls, values, value_strategy)
        elif strategy == "ignore":
            yield from self._generate_ignore(processed_urls, values, params)
        elif strategy == "all":
            if not value_strategy:
                print(
                    "Value strategy is required for 'combine' strategy in 'all' strategy",
                    file=sys.stderr,
                )
                return
            yield from self._generate_all(
                processed_urls, values, params, value_strategy
            )

    def _generate_normal(
        self,
        processed_urls: List[urllib.parse.ParseResult],
        values: List[str],
        params: List[str],
    ) -> Generator[str, None, None]:
        # Generate URLs based on 'normal' strategy using generators
        for value in values:
            for url in processed_urls:
                new_params = {param: [value] for param in params}

                for chunked_params in self.chunk_parameters(new_params):
                    try:
                        new_query = urllib.parse.urlencode(chunked_params, doseq=True)
                        new_url = url._replace(query=new_query)
                        yield urllib.parse.urlunparse(new_url)
                    except Exception as e:
                        print(f"Error generating normal URL: {e}", file=sys.stderr)

    def _generate_combine(
        self,
        processed_urls: List[urllib.parse.ParseResult],
        values: List[str],
        value_strategy: str,
    ) -> Generator[str, None, None]:
        # Generate URLs based on 'combine' strategy using generators
        for url in processed_urls:
            try:
                query_params = urllib.parse.parse_qs(url.query)
                base_url = url._replace(query="")

                for value in values:
                    for param in query_params.keys():
                        new_query = query_params.copy()

                        if value_strategy == "replace":
                            new_query[param] = [value]
                        elif value_strategy == "suffix":
                            new_query[param] = [v + value for v in query_params[param]]

                        query_string = urllib.parse.urlencode(new_query, doseq=True)
                        new_url = base_url._replace(query=query_string)
                        yield urllib.parse.urlunparse(new_url)
            except Exception as e:
                print(f"Error generating combine URL: {e}", file=sys.stderr)

    def _generate_ignore(
        self,
        processed_urls: List[urllib.parse.ParseResult],
        values: List[str],
        params: List[str],
    ) -> Generator[str, None, None]:
        # Generate URLs based on 'ignore' strategy using generators
        for value in values:
            for url in processed_urls:
                try:
                    base_query = urllib.parse.parse_qs(url.query)
                    additional_params = {
                        param: [value] for param in params if param not in base_query
                    }

                    # Always include the base query params
                    for chunked_additional in self.chunk_parameters(additional_params):
                        combined_query = {**base_query, **chunked_additional}
                        new_query = urllib.parse.urlencode(combined_query, doseq=True)
                        new_url = url._replace(query=new_query)
                        yield urllib.parse.urlunparse(new_url)
                except Exception as e:
                    print(f"Error generating ignore URL: {e}", file=sys.stderr)

    def _generate_all(
        self,
        processed_urls: List[urllib.parse.ParseResult],
        values: List[str],
        params: List[str],
        value_strategy: str,
    ) -> Generator[str, None, None]:
        # Generate URLs based on 'all' strategy using generators
        yield from self._generate_combine(processed_urls, values, value_strategy)
        yield from self._generate_ignore(processed_urls, values, params)
        yield from self._generate_normal(processed_urls, values, params)


def process_and_output_results(
    generator: Iterable[str], output_file: Optional[str] = None
) -> None:
    # Process results from the generator and handle output streaming
    count = 0

    # Open output file if specified
    output_handle = None
    if output_file:
        try:
            output_handle = open(output_file, "w")
        except IOError as e:
            print(f"Error opening output file '{output_file}': {e}", file=sys.stderr)
            output_file = None

    try:
        # Process each URL as it's generated
        for url in generator:
            count += 1
            # Print to stdout for proper piping or redirection
            print(url)

            # Write to file if specified
            if output_handle:
                output_handle.write(f"{url}\n")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.", file=sys.stderr)
    except Exception as e:
        print(f"Error processing results: {e}", file=sys.stderr)
    finally:
        if output_handle:
            output_handle.close()

    print(f"\nGenerated {count} URLs.", file=sys.stderr)


def main():
    # Main function to parse arguments and execute the script
    parser = argparse.ArgumentParser(
        description="URL Fuzzing Tool. Developed By Ali Hamidi. https://x.com/AliHz1337",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument(
        "-u",
        "--url",
        help="Single URL"
    )
    url_group.add_argument(
        "-l",
        "--url_list",
        help="File with links"
    )
    parser.add_argument(
        "-gs",
        "--generate_strategy",
        required=True,
        choices=["all", "combine", "normal", "ignore"],
        help="Generate strategy",
    )
    parser.add_argument(
        "-vs",
        "--value_strategy",
        choices=["replace", "suffix"],
        help="Value strategy ( required for 'all' and 'combine' )",
    )
    value_group = parser.add_mutually_exclusive_group(required=True)
    value_group.add_argument(
        "-v",
        "--values_inline",
        nargs="+",
        help="Values provided inline"
    )
    value_group.add_argument(
        "-vf",
        "--values_file",
        help="File with values"
    )
    parser.add_argument(
        "-p",
        "--parameters",
        help="File with parameters ( required for 'ignore', 'normal', and 'all' strategies )",
    )
    parser.add_argument(
        "-c",
        "--chunk",
        type=int,
        default=25,
        help="Number of parameters per URL"
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        const="x9-generated-link.txt",
        help="File to save the output",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Suppress banner"
    )

    args = parser.parse_args()

    # Parameter validation
    if args.generate_strategy in ["ignore", "normal", "all"] and not args.parameters:
        parser.error(
            f"Parameter file (-p) is required for '{args.generate_strategy}' strategy"
        )

    if args.generate_strategy in ["combine", "all"] and not args.value_strategy:
        parser.error(
            f"Value strategy (-vs) is required for '{args.generate_strategy}' strategy"
        )

    # Print banner if not in silent mode
    if not args.silent:
        URLFuzzer.print_banner()

    # Set up fuzzer with specified chunk size
    fuzzer = URLFuzzer(chunk_size=args.chunk)

    # Get links from URL or file
    links = [args.url] if args.url else fuzzer.load_file(args.url_list)

    # Get values from inline arguments or file
    values = (
        args.values_inline if args.values_inline else fuzzer.load_file(args.values_file)
    )

    # Generate and process URLs
    url_generator = fuzzer.generate_urls(
        strategy=args.generate_strategy,
        urls=links,
        values=values,
        params_file=args.parameters,
        value_strategy=args.value_strategy,
    )

    # Process and output results
    process_and_output_results(url_generator, args.output)


if __name__ == "__main__":
    main()