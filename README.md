## Kraken Data and Trading Indicator Stream
** Not Financial advice and none of the included indicators should be taken as actionable market indicators. DO NOT USE THIS.

### Add Kraken API Keys
- Add `.env` file to route of directory based on requirements from .env.template.
- below start scripts should install all deps from the `reqs.txt` file

#### Strategies
- `./start-convergence-tape.sh` - this script runs a peak/valley indicator on several HOLC data timeframes and feedbacks the latest signal. It also combines it with the `MACD` to give some confirmation and gut check, the indicator
- `./start-bot-server.sh` buys/sells asset amounts according to the `src/strategies/pv_wave.py` class constructed in the `server.py` file.
- `./start-flask.sh` starts up some primitive api endpoints of restructured account data from your kraken account and strategies you may want feedback from. `WIP`

#### Research `R&D/`
 - Aside from basic indicators like `EMA/MACD/Volume/Vol` stuff, the big one that's giving some true alpha is `R&D/claude_denoise.ipynb` file for peak/valley identification. It uses some denoising from [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) lib and combos that with [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html) peak/valley finding to see trend reversals. Pretty cool....
