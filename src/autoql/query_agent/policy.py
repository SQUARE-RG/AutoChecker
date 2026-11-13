"""Conservative syntactic checks, not a proof of vulnerability semantics."""
import re


def generation_issues(query, spec, task):
    issues = []
    # Ignore query metadata/comments for identity checks; only executable constraints matter.
    code = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', '', query)
    forbidden = [task.buggy_commit, task.fix_commit, task.cve_id] + [e['file'] for e in spec['evidence']]
    if any(value in code for value in forbidden):
        issues.append('Do not hard-code task identity, filenames or source coordinates.')
    packages = set()
    for entry in spec['evidence']:
        packages.update(re.findall(r'\bpackage\s+([\w.]+)\s*;', entry['code']))
        package_path = re.search(r'(?:^|/)src/(?:main|test)/java/(.+)/[^/]+\.java$', entry['file'])
        if package_path:
            packages.add(package_path.group(1).replace('/', '.'))
    if any('"' + p + '"' in code for p in packages):
        issues.append('Remove project-package/type anchors. Model the external API, data/control relationships, not the particular containing helper.')
    return issues
