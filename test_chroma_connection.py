import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings


def main() -> None:
    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
        settings=ChromaSettings(
            anonymized_telemetry=False,
        ),
    )

    heartbeat = client.heartbeat()
    collections = client.list_collections()

    print("ChromaDB heartbeat:", heartbeat)
    print("Collections:", collections)


if __name__ == "__main__":
    main()