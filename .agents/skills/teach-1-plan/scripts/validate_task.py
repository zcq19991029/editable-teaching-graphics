"""Read-only validation of one explicit teaching-graphics task; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def validate(root, phase):
    root = Path(root).resolve()
    errors = []
    index = root / '提示词索引.md'
    if not index.is_file():
        return ['缺少提示词索引.md'], {}
    lines = index.read_text(encoding='utf-8').splitlines()
    header = next((line for line in lines if line.startswith('|输出页|')), '')
    cols = [re.sub(r'（[^）]*）', '', c.strip()) for c in header.strip('|').split('|')]
    required = ['输出页', '图编号', '标题', '类型／状态', '最终图片路径', '当前提示词路径', '当前提示词SHA-256', '复现清单路径', '最终图片SHA-256']
    if len(cols) != len(set(cols)):
        return ['索引表头存在重复列'], {}
    if any(c not in cols for c in required):
        return errors + ['索引缺少必要列'], {}
    rows = []; seen = set(); paths = set(); blanks = 0
    for line in lines:
        if not re.match(r'\|P\d+\|', line):
            continue
        values = [x.strip() for x in line.strip('|').split('|')]
        if len(values) != len(cols):
            errors.append(values[0] + ' 行列数与表头不一致')
            continue
        row = dict(zip(cols, values)); page = row['输出页']; rows.append(row)
        if page in seen:
            errors.append(page + ' 输出页重复')
        seen.add(page)
        if row['图编号'] == '—':
            blanks += 1
            if any(row[c] != '—' for c in ['最终图片路径', '当前提示词路径', '复现清单路径']):
                errors.append(page + ' 占位页不得有逐图文件路径')
            continue
        if phase == 'generated' and '已核对' not in row['类型／状态']:
            errors.append(page + ' 尚未核对完成')
        for field, folder, digest in [
            ('当前提示词路径', '提示词', '当前提示词SHA-256'),
            ('最终图片路径', '图片', '最终图片SHA-256'),
            ('复现清单路径', '复现清单', None),
        ]:
            value = row[field]
            if value == '—':
                errors.append(page + ' 非占位项缺少' + field); continue
            p = Path(value)
            if not p.is_absolute():
                p = root / p
            p = p.resolve()
            if p.parent != root / folder:
                errors.append(page + ' ' + field + ' 未位于' + folder + '/')
            if p in paths:
                errors.append(page + ' 多条目引用同一逐图文件')
            paths.add(p)
            if not p.name.startswith(page + '-'):
                errors.append(page + ' 文件输出页前缀不对应')
            stem = page + '-' + row['标题']
            expected_stem = stem + ('-提示词' if folder == '提示词' else '-复现清单' if folder == '复现清单' else '')
            if p.stem != expected_stem:
                errors.append(page + ' 标题与文件名不对应: ' + field)
            needed = phase == 'generated' or field == '当前提示词路径'
            if needed and not p.is_file():
                errors.append(page + ' 文件不存在: ' + field)
            if p.is_file() and digest:
                expected = row[digest]
                if not re.fullmatch(r'[0-9a-fA-F]{64}', expected):
                    errors.append(page + ' 缺少有效哈希: ' + digest)
                elif hashlib.sha256(p.read_bytes()).hexdigest() != expected.lower():
                    errors.append(page + ' 哈希不匹配: ' + field)
    if not rows:
        errors.append('索引没有有效条目')
    elif [row['输出页'] for row in rows] != ['P' + str(i).zfill(max(2, len(str(len(rows))))) for i in range(1, len(rows) + 1)]:
        errors.append('完整输出页序不连续或未按确认顺序排列')
    for pattern in ['P*.png', 'P*.jpg', 'P*-提示词.md', 'P*-复现清单.md']:
        if list(root.glob(pattern)):
            errors.append('任务根目录散落逐图文件: ' + pattern)
    for folder in ['图片', '提示词', '复现清单']:
        p = root / folder
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file() and f.resolve() not in paths:
                    errors.append('当前材料目录有未索引文件: ' + folder + '/' + f.name)
    return errors, {'output_pages': len(rows), 'images': len(rows) - blanks, 'blanks': blanks, 'phase': phase}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_dir')
    parser.add_argument('--phase', choices=['plan', 'generated'], required=True)
    args = parser.parse_args()
    errors, stats = validate(args.task_dir, args.phase)
    print(json.dumps({'ok': not errors, **stats, 'errors': errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)
