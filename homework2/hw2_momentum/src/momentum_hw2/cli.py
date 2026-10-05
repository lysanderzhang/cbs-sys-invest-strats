import argparse
import yaml
from .data_sources import ROOT,fetch,import_csv
from .data_validation import validate

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['fetch','validate-data','run','report','import-csv'])
    parser.add_argument('--config',default=str(ROOT/'config/base.yaml'))
    parser.add_argument('--offline',action='store_true',help='run/validate/report never access network')
    parser.add_argument('--ticker');parser.add_argument('--input');parser.add_argument('--provider')
    args=parser.parse_args();cfg=yaml.safe_load(open(args.config))
    if args.command=='fetch':
        if args.offline:raise ValueError('fetch requires network; cached run uses run --offline')
        fetch(cfg)
    elif args.command=='validate-data':validate(cfg)
    elif args.command=='import-csv':import_csv(args.ticker,args.input,args.provider)
    elif args.command=='run':
        from .pipeline import run
        run(cfg)
    elif args.command=='report':
        from .reporting import report
        report(cfg)

if __name__=='__main__':main()
