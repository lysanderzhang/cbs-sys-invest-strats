"""Regression checks for the old report validator's cross-metric false positive."""
import copy,json,re
from pathlib import Path
import pytest
from src.validate_report import validate_bindings,ROOT

def material():return (ROOT/'report/main.tex').read_text(),json.loads((ROOT/'report/numerical_claims.json').read_text())

def test_current_narrative_has_valid_source_bindings():
    text,claims=material();assert validate_bindings(text,claims)==len(claims)

def test_wrong_number_is_rejected_even_if_it_exists_elsewhere():
    text,claims=material()
    existing=re.search(r'\\newcommand\{\\rCondSharpe\}\{([^}]+)\}',text).group(1)
    changed=re.sub(r'(\\newcommand\{\\rBaseSharpe\}\{)[^}]+',lambda m:m[1]+existing,text)
    with pytest.raises(ValueError,match='binding'):validate_bindings(changed,claims)

@pytest.mark.parametrize('field,value',[('column','geometric'),('scale',100)])
def test_wrong_metric_or_units_cannot_pass(field,value):
    text,claims=material();claims=copy.deepcopy(claims)
    next(c for c in claims if c['label']=='BaseSharpe')[field]=value
    with pytest.raises(ValueError,match='binding'):validate_bindings(text,claims)
