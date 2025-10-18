from __future__ import annotations

import io
from pathlib import Path
from typing import List
import zipfile

__all__ = ["ZipExtractor"]


class ZipExtractor:
    """Opera sobre um ZIP em memória (BytesIO) para listar e extrair CSVs."""

    @staticmethod
    def list_csv(zip_bytes: io.BytesIO) -> List[str]:
        """Lista os arquivos .csv contidos no zip em memória."""
        with zipfile.ZipFile(zip_bytes, "r") as zf:
            return [name for name in zf.namelist() if name.lower().endswith(".csv")]

    @staticmethod
    def extract_all(zip_bytes: io.BytesIO, dest_dir: Path) -> None:
        """Extrai com segurança todos os arquivos do zip para dest_dir.

        Protege contra path traversal garantindo que nenhum membro escape de dest_dir.

        Args:
            zip_bytes: BytesIO com o conteúdo do zip.
            dest_dir: Diretório para onde os arquivos serão extraídos.

        Returns:
            None
            
        Raises:
            RuntimeError: se houver path traversal detectado.
        """
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_bytes, "r") as zf:
            for member in zf.infolist():
                # Normaliza o caminho do membro
                member_name = member.filename
                # Ignorar entradas de diretório implícitas/absolutas
                if member_name.endswith("/"):
                    continue

                # Remove componentes perigosos
                safe_name = Path(member_name).as_posix().lstrip("/")
                # Bloqueia qualquer tentativa de subir diretórios
                # (zipfile pode conter caminhos como ../../outside)
                target_path = (dest / safe_name).resolve()
                if not str(target_path).startswith(str(dest.resolve())):
                    raise RuntimeError(f"Path traversal detectado: {member_name}")

                # Garante diretório pai
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Extrai o arquivo
                with zf.open(member, "r") as src, open(target_path, "wb") as dst:
                    dst.write(src.read())

