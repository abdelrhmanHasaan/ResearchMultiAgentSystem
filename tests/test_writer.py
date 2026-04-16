from agents.writer import WriterAgent

if __name__ == "__main__":
    writer = WriterAgent()

    result = writer.run(
        topic="Artificial Intelligence Trends 2025"
    )

    if "error" in result:
        print("❌ Error:", result["error"])
    else:
        print("✅ Report generated!")
        print("📄 PDF file:", result["pdf"])

        print("\n--- Preview ---\n")
        print(result["report"][:500])