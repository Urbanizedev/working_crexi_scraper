# CrexiScraper — Setup & Run

This scraper uses Selenium with `undetected-chromedriver` to export filtered land listings from Crexi.

The script will:

- Log into your Crexi account and save cookies to avoid logging in again.
- Search listings by county  
- Apply dynamic acreage filters  
- Export listings (under 1000 results per search)

## Setup & Run

1. **Install required packages**

In your virtual environment:
```
pip install -r requirements.txt
```

2. **Set your export folder**

You can change this by modifying the `download_dir` variable inside of `run_scraper()`.

----------

In `convert_xlsx_to_csv` you can modify the `xlsx_dir`, `csv_dir`, and `merged_csv_path` variables according to your computer.

3. **Enter counties**

Insert the names of the counties you want to scrape into the "counties" list. 
Do not include "county" at the end of the name, it will be appended automatically. 

4. **Minimum Acres**

Set the minimum acres you want to filter by modifying the `min_acres` variable
inside `scrape_county()`

5. **Run the script**

Click the run button in your ide or

```bash
python crexi_scraper.py
```

On first run it will log in, afterwards the cookies should save and logging in after running each time won't be necessary.

6. **Merge the output files**

Modify the `xlsx_dir` variable in `convert_xlsx_to_csv.py` to match the directory your output files are in.

Modify the `csv_dir` variable to name the destination folder for the newly converted CSVs .

Modify `merged_csv_path` to change where you final merged result will save to.

Then execute the script.