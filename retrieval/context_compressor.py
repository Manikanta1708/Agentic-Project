"""
=========================================================
Context Compressor
=========================================================
"""

from difflib import SequenceMatcher


def similarity(a, b):

    return SequenceMatcher(

        None,

        a.lower(),

        b.lower()

    ).ratio()


def compress_context(

    candidates,

    max_documents=5,

    similarity_threshold=0.85,

    max_characters=2500

):

    compressed = []

    total_chars = 0

    for item in candidates:

        text = item.get("document", "").strip()

        if not text:

            continue

        duplicate = False

        for existing in compressed:

            score = similarity(

                text,

                existing["document"]

            )

            if score >= similarity_threshold:

                duplicate = True

                break

        if duplicate:

            continue

        if total_chars + len(text) > max_characters:

            break

        compressed.append(item)

        total_chars += len(text)

        if len(compressed) >= max_documents:

            break

    return compressed


if __name__ == "__main__":

    sample = [

        {

            "branch":"ECE",

            "document":"Machine Learning Deep Learning IoT"

        },

        {

            "branch":"ECE",

            "document":"Machine Learning Deep Learning IoT"

        },

        {

            "branch":"CSE",

            "document":"Algorithms Operating Systems"

        },

        {

            "branch":"AIML",

            "document":"Knowledge Graph RAG LLM"

        }

    ]

    results = compress_context(sample)

    print("\n========== COMPRESSED ==========\n")

    for r in results:

        print(r["branch"])

    print("\nDocuments Retained :", len(results))