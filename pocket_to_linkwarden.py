import csv
import html
import time
import argparse

def convert_pocket_csv_to_html_bookmarks(csv_filepath, html_filepath):
    """
    Converts a Pocket export CSV to a Netscape Bookmark HTML file.

    Expected CSV columns: title, url, time_added, tags, status
    - title: The title of the saved item.
    - url: The URL of the saved item.
    - time_added: Unix timestamp of when the item was added.
    - rags: Comma-separated string of tags.
    - status: Pocket's status (0=unread, 1=read, 2=archived) - mostly ignored for Netscape format.
    """
    bookmarks_added = 0
    skipped_due_to_missing_url = 0

    try:
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile, \
             open(html_filepath, 'w', encoding='utf-8') as htmlfile:

            # Write Netscape Bookmark File Header
            htmlfile.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
            htmlfile.write("<!--This is an automatically generated file.\n")
            htmlfile.write("It will be read and overwritten.\n")
            htmlfile.write("Do Not Edit! -->\n")
            htmlfile.write("<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">\n")
            htmlfile.write("<TITLE>Bookmarks</TITLE>\n")
            htmlfile.write("<H1>Bookmarks</H1>\n")
            htmlfile.write("<DL><p>\n") # Start of the main list

            reader = csv.DictReader(csvfile)
            if not all(col in reader.fieldnames for col in ['title', 'url', 'time_added', 'tags']):
                print("Error: CSV file is missing one or more required columns: 'title', 'url', 'time_added', 'tags'.")
                print(f"Found columns: {reader.fieldnames}")
                return

            for row_num, row in enumerate(reader, 1):
                title = row.get('title', f'Untitled Link {row_num}')
                url = row.get('url')
                time_added_str = row.get('time_added')
                tags_str = row.get('tags', '')
                # status = row.get('status', '0') # We don't directly use status for Netscape format

                if not url:
                    print(f"Warning: Skipping row {row_num} due to missing URL. Title: '{title}'")
                    skipped_due_to_missing_url += 1
                    continue

                # Ensure title and tags are properly HTML escaped
                escaped_title = html.escape(title)

                # Tags for Netscape format should be comma-separated.
                # If Pocket's tags are already comma-separated, this is fine.
                # If tags might have spaces or special chars within them, quote them (though TAGS attribute usually handles this well)
                escaped_tags = html.escape(tags_str) if tags_str else ""

                add_date_attr = ""
                if time_added_str:
                    try:
                        # Ensure it's an integer timestamp
                        add_date_attr = f" ADD_DATE=\"{int(float(time_added_str))}\""
                    except ValueError:
                        print(f"Warning: Invalid time_added format for '{title}': {time_added_str}. Skipping ADD_DATE.")

                # Construct the bookmark item
                # <DT><A HREF="url" ADD_DATE="timestamp" TAGS="tag1,tag2">Title</A>
                htmlfile.write(f"    <DT><A HREF=\"{html.escape(url)}\"{add_date_attr}")
                if escaped_tags:
                    htmlfile.write(f" TAGS=\"{escaped_tags}\"")
                htmlfile.write(f">{escaped_title}</A>\n")
                bookmarks_added += 1

            # Write Netscape Bookmark File Footer
            htmlfile.write("</DL><p>\n") # End of the main list

        print(f"\nSuccessfully coverted {bookmarks_added} bookmarks.")
        if skipped_due_to_missing_url > 0:
            print(f"Skipped {skipped_due_to_missing_url} items due to missing URLs.")
        print(f"Output HTML file saved to: {html_filepath}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Pocket CSV export to Netscape Bookmark HTML format for Linkwarden.")
    parser.add_argument("csv_input_file", help="Path to the Pocket CSV export file.")
    parser.add_argument("html_output_file", help="Path for the generated HTML bookmarks file (e.g., linkwarden_import.html).")

    args = parser.parse_args()

    convert_pocket_csv_to_html_bookmarks(args.csv_input_file, args.html_output_file)

    print("\n--- Instructions for Linkwarden ---")
    print(f"1. Go to your Linkwarden instance and log in.")
    print(f"2. Find the 'Import Links' option (usually on the dashboard).")
    print(f"3. Select 'HTML Bookmarks File' (or a similar option like 'Netscape Bookmarks').")
    print(f"4. Upload the generated file: {args.html_output_file}")
    print(f"5. Follow Linkwarden's prompts to complete the import.")
