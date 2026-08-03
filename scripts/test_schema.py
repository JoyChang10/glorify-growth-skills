import json


FILE = "test_enrichment.json"


def load_data():
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_basic_structure(article):
    print("\n=== Basic Structure Test ===")

    required_fields = [
        "url",
        "title",
        "content"
    ]

    metadata_fields = [
        "sge_category",
        "knowledge_type",
        "platform",
        "industry",
        "frameworks",
        "usable_for",
        "evergreen_score",
        "glorify_relevance"
    ]

    article_data = article["article"]
    metadata = article["metadata"]

    for field in required_fields:
        if field in article_data:
            print(f"✓ article.{field}")
        else:
            print(f"✗ Missing article.{field}")


    for field in metadata_fields:
        if field in metadata:
            print(f"✓ metadata.{field}")
        else:
            print(f"✗ Missing metadata.{field}")



def test_platform_retrieval(article):
    print("\n=== Test 1: TikTok Knowledge Retrieval ===")

    metadata = article["metadata"]

    if "TikTok" in metadata["platform"]:
        print("✓ Found TikTok-related article")
        print("Title:", article["article"]["title"])
    else:
        print("✗ Not TikTok related")



def test_ugc_retrieval(article):
    print("\n=== Test 2: UGC Skill Retrieval ===")

    usable_for = article["metadata"]["usable_for"]

    if "ugc_script_generation" in usable_for:
        print("✓ This article can power UGC generation")

        frameworks = article["metadata"]["frameworks"]

        for f in frameworks:
            print("\nFramework:")
            print("-", f["name"])
            print("-", f["description"])

    else:
        print("✗ Not useful for UGC")



def test_glorify_relevance(article):
    print("\n=== Test 3: Glorify Relevance ===")

    score = article["metadata"]["glorify_relevance"]

    print("Glorify relevance score:", score)

    if score >= 7:
        print("✓ Worth keeping for Glorify growth knowledge")
    else:
        print("△ Low relevance")



def test_framework_quality(article):
    print("\n=== Test 4: Framework Quality ===")

    frameworks = article["metadata"]["frameworks"]

    for framework in frameworks:

        required = [
            "name",
            "description",
            "when_to_use",
            "example"
        ]

        for field in required:
            if field in framework and framework[field]:
                print(f"✓ Framework has {field}")
            else:
                print(f"✗ Missing framework {field}")



def simulate_growth_agent(article):

    print("\n=== Test 5: Simulate Future Growth Agent ===")

    query = "Give me TikTok ideas for Glorify Ring"


    metadata = article["metadata"]


    score = 0


    if "TikTok" in metadata["platform"]:
        score += 1

    if "content_ideation" in metadata["usable_for"]:
        score += 1

    if metadata["glorify_relevance"] >= 7:
        score += 1


    print("Query:")
    print(query)

    print("\nRetrieval score:", score, "/3")


    if score == 3:
        print("✓ Agent would retrieve this knowledge")
    else:
        print("✗ Schema may need adjustment")



def main():

    data = load_data()

    # support both single object and list
    if isinstance(data, list):
        article = data[0]
    else:
        article = data


    test_basic_structure(article)

    test_platform_retrieval(article)

    test_ugc_retrieval(article)

    test_glorify_relevance(article)

    test_framework_quality(article)

    simulate_growth_agent(article)



if __name__ == "__main__":
    main()