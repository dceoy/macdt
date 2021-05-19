#!/usr/bin/env python
"""
MACD-based Forex Trader using Oanda API

Usage:
    macdf -h|--help
    macdf --version
    macdf close [--debug|--info] [--oanda-account=<id>] [--oanda-token=<str>]
        [--oanda-env=<str>] [<instrument>...]
    macdf trade [--debug|--info] [--oanda-account=<id>] [--oanda-token=<str>]
        [--oanda-env=<str>] [--quiet] [--dry-run] [--granularity=<str>]
        [--betting-system=<str>] [--scanned-transaction-count=<int>]
        [--feature-type=<str>] [--unit-margin=<ratio>]
        [--preserved-margin=<ratio>] [--take-profit-limit=<float>]
        [--trailing-stop-limit=<float>] [--stop-loss-limit=<float>]
        [--max-spread=<float>] [--fast-ema-span=<int>] [--slow-ema-span=<int>]
        [--macd-ema-span=<int>] <instrument>...

Options:
    -h, --help              Print help and exit
    --version               Print version and exit
    --debug, --info         Execute a command with debug|info messages
    --oanda-account=<id>    Set an Oanda account ID [$OANDA_ACCOUNT]
    --oanda-token=<str>     Set an Oanda API token [$OANDA_TOKEN]
    --oanda-env=<str>       Set an Oanda trading environment [default: trade]
                            { trade, practice }
    --quiet                 Suppress messages
    --dry-run               Invoke a trader with dry-run mode
    --granularity=<str>     Set the granularity [default: D]
                            { S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30,
                              H1, H2, H3, H4, H6, H8, H12, D, W, M }
    --betting-system=<str>  Set the betting system [default: constant]
                            { constant, martingale, paroli, dalembert,
                              oscarsgrind }
    --scanned-transaction-count=<int>
                            Set the transaction count to scan [default: 0]
    --feature-type=<str>    Set the feature type [default: MID]
                            { MID, VEL, LR, LRV, LRA }
    --unit-margin=<ratio>   Set the unit margin ratio to NAV [default: 0.01]
    --preserved-margin=<ratio>
                            Set the preserved margin ratio [default: 0.01]
    --take-profit-limit=<float>
                            Set the take-profit limit ratio [default: 0.01]
    --trailing-stop-limit=<float>
                            Set the trailing-stop limit ratio [default: 0.01]
    --stop-loss-limit=<float>
                            Set the stop-loss limit ratio [default: 0.01]
    --max-spread=<float>    Set the max spread ratio [default: 0.01]
    --fast-ema-span=<int>   Set the fast EMA span [default: 12]
    --slow-ema-span=<int>   Set the slow EMA span [default: 26]
    --macd-ema-span=<int>   Set the MACD EMA span [default: 9]

Commands:
    close                   Close positions (if not <instrument>, close all)
    trade                   Trade currencies

Arguments:
    <instrument>            Forex instrumnt such as EUR_USD and USD_JPY
"""

import logging
import os

import v20
from docopt import docopt
from oandacli.call.order import close_positions
from oandacli.util.logger import set_log_config

from . import __version__
from .trader import AutoTrader


def main():
    args = docopt(__doc__, version=f'macdf {__version__}')
    set_log_config(debug=args['--debug'], info=args['--info'])
    logger = logging.getLogger(__name__)
    logger.debug(f'args:{os.linesep}{args}')
    oanda_account_id = (args['--oanda-account'] or os.getenv('OANDA_ACCOUNT'))
    oanda_api_token = (args['--oanda-token'] or os.getenv('OANDA_TOKEN'))
    if args.get('close'):
        close_positions(
            api=_create_oanda_api(
                api_token=oanda_api_token, environment=args['--oanda-env']
            ),
            account_id=oanda_account_id, instruments=args['<instrument>']
        )
    elif args.get('trade'):
        logger.info('Autonomous trading')
        AutoTrader(
            oanda_account_id=oanda_account_id, oanda_api_token=oanda_api_token,
            oanda_environment=args['--oanda-env'],
            instruments=args['<instrument>'],
            granularities=args['--granularity'].split(','),
            betting_system=args['--betting-system'],
            scanned_transaction_count=int(args['--scanned-transaction-count']),
            feature_type=args['--feature-type'],
            unit_margin_ratio=float(args['--unit-margin']),
            preserved_margin_ratio=float(args['--preserved-margin']),
            take_profit_limit_ratio=float(args['--take-profit-limit']),
            trailing_stop_limit_ratio=float(args['--trailing-stop-limit']),
            stop_loss_limit_ratio=float(args['--stop-loss-limit']),
            max_spread_ratio=float(args['--max-spread']),
            fast_ema_span=float(args['--fast-ema-span']),
            slow_ema_span=float(args['--slow-ema-span']),
            macd_ema_span=float(args['--macd-ema-span']),
            log_dir_path=None, quiet=args['--quiet'], dry_run=args['--dry-run']
        ).invoke()


def _create_oanda_api(api_token, environment='trade', stream=False, **kwargs):
    return v20.Context(
        hostname='{0}-fx{1}.oanda.com'.format(
            ('stream' if stream else 'api'), environment
        ),
        token=api_token, **kwargs
    )
