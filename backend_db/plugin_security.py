"""
Plugin Security Scanner for OmniScope AI
Provides static code analysis and vulnerability scanning for plugins
"""

import os
import subprocess
import json
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
import re


class SecurityScanner:
    """Security scanner for plugin code and dependencies"""
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = {
        'python': [
            (r'eval\s*\(', 'Use of eval() - potential code injection'),
            (r'exec\s*\(', 'Use of exec() - potential code injection'),
            (r'__import__\s*\(', 'Dynamic import - potential security risk'),
            (r'compile\s*\(', 'Dynamic code compilation - potential security risk'),
            (r'os\.system\s*\(', 'System command execution - potential security risk'),
            (r'subprocess\.call\s*\(', 'Subprocess execution - potential security risk'),
            (r'subprocess\.Popen\s*\(', 'Subprocess execution - potential security risk'),
            (r'open\s*\([^)]*[\'"]w', 'File write operation - verify permissions'),
            (r'pickle\.loads?\s*\(', 'Pickle deserialization - potential code execution'),
            (r'yaml\.load\s*\(', 'Unsafe YAML loading - use safe_load instead'),
            (r'requests\.get\s*\([^)]*verify\s*=\s*False', 'SSL verification disabled'),
        ],
        'r': [
            (r'system\s*\(', 'System command execution - potential security risk'),
            (r'eval\s*\(', 'Use of eval() - potential code injection'),
            (r'parse\s*\(', 'Code parsing - potential security risk'),
            (r'source\s*\(', 'Source external file - verify source'),
            (r'load\s*\(', 'Load external data - verify source'),
            (r'readRDS\s*\(', 'Read serialized data - verify source'),
        ]
    }
    
    # Suspicious imports/libraries
    SUSPICIOUS_IMPORTS = {
        'python': [
            'socket', 'telnetlib', 'ftplib', 'smtplib',
            'ctypes', 'cffi', 'subprocess', 'pty'
        ],
        'r': [
            'RCurl', 'httr', 'curl'
        ]
    }
    
    @staticmethod
    def scan_plugin(
        plugin_path: str,
        language: str,
        dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security scan on plugin
        
        Args:
            plugin_path: Path to plugin files
            language: Programming language
            dependencies: List of dependencies
        
        Returns:
            Dict: Security scan results
        """
        results = {
            'overall_status': 'safe',
            'risk_level': 'low',
            'issues': [],
            'warnings': [],
            'info': [],
            'scans_performed': []
        }
        
        # Static code analysis
        static_results = SecurityScanner._static_code_analysis(
            plugin_path, language
        )
        results['scans_performed'].append('static_analysis')
        results['issues'].extend(static_results.get('issues', []))
        results['warnings'].extend(static_results.get('warnings', []))
        
        # Pattern matching for dangerous code
        pattern_results = SecurityScanner._pattern_scan(
            plugin_path, language
        )
        results['scans_performed'].append('pattern_matching')
        results['issues'].extend(pattern_results.get('issues', []))
        results['warnings'].extend(pattern_results.get('warnings', []))
        
        # Dependency vulnerability scan
        if dependencies:
            dep_results = SecurityScanner._dependency_scan(
                dependencies, language
            )
            results['scans_performed'].append('dependency_scan')
            results['issues'].extend(dep_results.get('issues', []))
            results['warnings'].extend(dep_results.get('warnings', []))
        
        # File permission check
        perm_results = SecurityScanner._check_file_permissions(plugin_path)
        results['scans_performed'].append('permission_check')
        results['warnings'].extend(perm_results.get('warnings', []))
        
        # Determine overall status and risk level
        if results['issues']:
            results['overall_status'] = 'unsafe'
            results['risk_level'] = 'high' if len(results['issues']) > 5 else 'medium'
        elif results['warnings']:
            results['overall_status'] = 'warning'
            results['risk_level'] = 'medium' if len(results['warnings']) > 3 else 'low'
        
        return results
    
    @staticmethod
    def _static_code_analysis(
        plugin_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Perform static code analysis using language-specific tools"""
        results = {'issues': [], 'warnings': []}
        
        if language == 'python':
            # Use Bandit for Python security analysis
            try:
                result = subprocess.run(
                    ['bandit', '-r', plugin_path, '-f', 'json'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0 or result.stdout:
                    bandit_output = json.loads(result.stdout)
                    
                    for issue in bandit_output.get('results', []):
                        severity = issue.get('issue_severity', 'LOW')
                        
                        issue_data = {
                            'type': 'security_issue',
                            'severity': severity.lower(),
                            'message': issue.get('issue_text', ''),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'code': issue.get('code', ''),
                            'cwe': issue.get('issue_cwe', {}).get('id', '')
                        }
                        
                        if severity in ['HIGH', 'CRITICAL']:
                            results['issues'].append(issue_data)
                        else:
                            results['warnings'].append(issue_data)
            
            except FileNotFoundError:
                results['warnings'].append({
                    'type': 'scan_unavailable',
                    'message': 'Bandit not installed - static analysis skipped'
                })
            except subprocess.TimeoutExpired:
                results['warnings'].append({
                    'type': 'scan_timeout',
                    'message': 'Static analysis timed out'
                })
            except Exception as e:
                results['warnings'].append({
                    'type': 'scan_error',
                    'message': f'Static analysis error: {str(e)}'
                })
        
        return results
    
    @staticmethod
    def _pattern_scan(
        plugin_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Scan for dangerous code patterns"""
        results = {'issues': [], 'warnings': []}
        
        patterns = SecurityScanner.DANGEROUS_PATTERNS.get(language, [])
        if not patterns:
            return results
        
        # Scan all files
        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                # Check file extension
                if language == 'python' and not file.endswith('.py'):
                    continue
                if language == 'r' and not (file.endswith('.R') or file.endswith('.r')):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for pattern, description in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                # Get line number
                                line_num = content[:match.start()].count('\n') + 1
                                
                                results['warnings'].append({
                                    'type': 'dangerous_pattern',
                                    'severity': 'medium',
                                    'message': description,
                                    'file': os.path.relpath(file_path, plugin_path),
                                    'line': line_num,
                                    'code': match.group(0)
                                })
                
                except Exception as e:
                    results['warnings'].append({
                        'type': 'scan_error',
                        'message': f'Error scanning {file}: {str(e)}'
                    })
        
        # Check for suspicious imports
        suspicious_imports = SecurityScanner.SUSPICIOUS_IMPORTS.get(language, [])
        if suspicious_imports:
            for root, dirs, files in os.walk(plugin_path):
                for file in files:
                    if language == 'python' and not file.endswith('.py'):
                        continue
                    if language == 'r' and not (file.endswith('.R') or file.endswith('.r')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            for imp in suspicious_imports:
                                if language == 'python':
                                    pattern = rf'import\s+{imp}|from\s+{imp}\s+import'
                                else:  # R
                                    pattern = rf'library\s*\(\s*{imp}\s*\)|require\s*\(\s*{imp}\s*\)'
                                
                                if re.search(pattern, content, re.IGNORECASE):
                                    results['warnings'].append({
                                        'type': 'suspicious_import',
                                        'severity': 'low',
                                        'message': f'Suspicious import: {imp}',
                                        'file': os.path.relpath(file_path, plugin_path)
                                    })
                    
                    except Exception:
                        pass
        
        return results
    
    @staticmethod
    def _dependency_scan(
        dependencies: List[str],
        language: str
    ) -> Dict[str, Any]:
        """Scan dependencies for known vulnerabilities"""
        results = {'issues': [], 'warnings': []}
        
        if language == 'python':
            # Use safety to check Python dependencies
            try:
                # Create temporary requirements file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.txt',
                    delete=False
                ) as f:
                    for dep in dependencies:
                        f.write(f"{dep}\n")
                    req_file = f.name
                
                try:
                    result = subprocess.run(
                        ['safety', 'check', '--file', req_file, '--json'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.stdout:
                        try:
                            safety_output = json.loads(result.stdout)
                            
                            for vuln in safety_output:
                                results['issues'].append({
                                    'type': 'dependency_vulnerability',
                                    'severity': 'high',
                                    'message': vuln.get('advisory', ''),
                                    'package': vuln.get('package', ''),
                                    'version': vuln.get('version', ''),
                                    'cve': vuln.get('cve', '')
                                })
                        except json.JSONDecodeError:
                            pass
                
                finally:
                    os.unlink(req_file)
            
            except FileNotFoundError:
                results['warnings'].append({
                    'type': 'scan_unavailable',
                    'message': 'Safety not installed - dependency scan skipped'
                })
            except Exception as e:
                results['warnings'].append({
                    'type': 'scan_error',
                    'message': f'Dependency scan error: {str(e)}'
                })
        
        return results
    
    @staticmethod
    def _check_file_permissions(plugin_path: str) -> Dict[str, Any]:
        """Check file permissions for security issues"""
        results = {'warnings': []}
        
        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    # Check if file is executable
                    if os.access(file_path, os.X_OK):
                        # Check if it's a script file
                        if not (file.endswith('.sh') or file.endswith('.py') or 
                               file.endswith('.R') or file.endswith('.r')):
                            results['warnings'].append({
                                'type': 'permission_issue',
                                'severity': 'low',
                                'message': 'Unexpected executable file',
                                'file': os.path.relpath(file_path, plugin_path)
                            })
                
                except Exception:
                    pass
        
        return results
    
    @staticmethod
    def generate_security_report(scan_results: Dict[str, Any]) -> str:
        """
        Generate human-readable security report
        
        Args:
            scan_results: Results from scan_plugin()
        
        Returns:
            str: Formatted security report
        """
        report = []
        report.append("=" * 60)
        report.append("PLUGIN SECURITY SCAN REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Overall Status: {scan_results['overall_status'].upper()}")
        report.append(f"Risk Level: {scan_results['risk_level'].upper()}")
        report.append(f"Scans Performed: {', '.join(scan_results['scans_performed'])}")
        report.append("")
        
        # Issues
        if scan_results['issues']:
            report.append(f"CRITICAL ISSUES ({len(scan_results['issues'])}):")
            report.append("-" * 60)
            for i, issue in enumerate(scan_results['issues'], 1):
                report.append(f"{i}. {issue.get('message', 'Unknown issue')}")
                if 'file' in issue:
                    report.append(f"   File: {issue['file']}")
                if 'line' in issue:
                    report.append(f"   Line: {issue['line']}")
                if 'severity' in issue:
                    report.append(f"   Severity: {issue['severity'].upper()}")
                report.append("")
        
        # Warnings
        if scan_results['warnings']:
            report.append(f"WARNINGS ({len(scan_results['warnings'])}):")
            report.append("-" * 60)
            for i, warning in enumerate(scan_results['warnings'], 1):
                report.append(f"{i}. {warning.get('message', 'Unknown warning')}")
                if 'file' in warning:
                    report.append(f"   File: {warning['file']}")
                report.append("")
        
        if not scan_results['issues'] and not scan_results['warnings']:
            report.append("No security issues detected.")
        
        report.append("=" * 60)
        
        return "\n".join(report)
