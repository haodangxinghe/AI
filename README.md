# Shijing Vocabulary Processing

This repository provides utilities to validate and expand a predefined《诗经》关键词词表。

## Key files
- `process_shijing.py`: Processes the full《诗经》文本，交叉验证先验词表、发现高频新词并提取关键词。
- `先验词表.txt`: The manually curated initial lexicon.
- `自动化词表输出.txt`: Generated output containing校验后的先验词表、新词发现、关键词提取以及合并词表，生成位置在仓库根目录（即与本文件同级）。
- `shijing_plain.txt` / `shijing.json`: Source corpus used by the processing script.

## How to generate the automated vocabulary
1. Ensure Python 3 is available.
2. Run `python process_shijing.py` from the repository root.
3. After completion, check `自动化词表输出.txt` (in the repository root) for the merged, cleaned vocabulary results.
