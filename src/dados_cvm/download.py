from __future__ import annotations

import io
import time
from typing import Final

import requests

from .endpoints import DocType, UrlBuilder

__all__ = ["ZipDownloader"]


class ZipDownloader:
    """Responsável por baixar os arquivos ZIP da CVM com retries simples."""

    DEFAULT_RETRIES: Final[int] = 3
    BACKOFF_SECONDS: Final[float] = 1.5
    TIMEOUT_SECONDS: Final[float] = 60.0

    @classmethod
    def download_zip(
        cls,
        doc_type: DocType,
        ano: int,
        retries: int | None = None,
        timeout: float | None = None,
    ) -> io.BytesIO:
        """Baixa o ZIP para o tipo/ano informado com retries e validações básicas.

        Args:
            doc_type: Tipo de documento (ex.: DocType.DFP, DocType.ITR)
            ano: Ano de referência (ex.: 2024)
            retries: Número de tentativas em caso de falha (default: 3)
            timeout: Timeout da requisição em segundos (default: 60)

        Returns:
            BytesIO contendo o conteúdo do zip.

        Raises:
            requests.HTTPError: quando a resposta HTTP não é 2xx.
            requests.RequestException: para outros erros de rede após esgotar retries.
        """
        url = UrlBuilder.build_zip_url(doc_type, ano)
        attempts = retries if retries is not None else cls.DEFAULT_RETRIES # atribui retries se for None
        timeout_s = timeout if timeout is not None else cls.TIMEOUT_SECONDS # atribui timeout se for None

        last_exc: Exception | None = None # variável para armazenar a última exceção
        for attempt in range(1, attempts + 1):
            try:
                resp = requests.get(url, timeout=timeout_s)
                resp.raise_for_status() # levanta exceção para códigos de erro HTTP

                # Validação leve de conteúdo
                content_type = resp.headers.get("Content-Type", "").lower() # pega o Content-Type da resposta
                # Alguns servidores podem retornar octet-stream; aceitamos zip ou octet-stream
                if "zip" not in content_type and "octet-stream" not in content_type:
                    # Ainda assim aceitamos se o conteúdo começar com bytes PK (assinatura de zip)
                    if not resp.content.startswith(b"PK"):
                        raise requests.RequestException(
                            f"Conteúdo inesperado (Content-Type={content_type!r})."
                        )

                return io.BytesIO(resp.content)
            except requests.HTTPError as e:
                # Erros 4xx/5xx: decide retry para >=500; 4xx normalmente não resolve com retry
                last_exc = e
                status = getattr(e.response, "status_code", None)
                if status is not None and 400 <= status < 500 and status != 429:
                    # 4xx exceto 429: falha imediata
                    raise
            except requests.RequestException as e:
                last_exc = e
            # Backoff antes do próximo attempt (se houver)
            if attempt < attempts:
                time.sleep(cls.BACKOFF_SECONDS * attempt)
        # Esgotou tentativas
        assert last_exc is not None
        raise last_exc
