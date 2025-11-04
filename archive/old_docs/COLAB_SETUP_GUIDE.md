========================================
  GOOGLE COLAB TRAINING SETUP GUIDE
========================================

STEP 1: Get Google Colab Pro
-----------------------------
1. Go to: https://colab.research.google.com/
2. Click "Subscribe" or "Upgrade"
3. Choose: Colab Pro ($9.99/month)
4. Sign up with your Google account

You can cancel after this month if you don't need it.


STEP 2: Upload Your Corpus to Google Drive
-------------------------------------------
1. Open Google Drive: https://drive.google.com
2. Create a new folder (optional, for organization)
3. Upload this file:
   ~/Repos/AI Project/Data/Historical_Embeddings/EEBO_1595-1700/eebo_cleaned_corpus.txt

   File size: 7.6 GB (will take 10-20 minutes to upload)

4. Note the path where you uploaded it
   Example: "MyDrive/eebo_cleaned_corpus.txt"


STEP 3: Upload the Notebook to Colab
-------------------------------------
1. Go to: https://colab.research.google.com/
2. Click: File → Upload notebook
3. Upload: ~/Repos/AI Project/colab_bert_training.ipynb
   (I just created this file for you)


STEP 4: Configure GPU
---------------------
1. In Colab, click: Runtime → Change runtime type
2. Hardware accelerator: Select "GPU"
3. GPU type: T4 (or V100 if available)
4. Click: Save


STEP 5: Update the Corpus Path
-------------------------------
In the notebook, find Cell 4 (Training Configuration)

Change this line:
CORPUS_PATH = "/content/drive/MyDrive/eebo_cleaned_corpus.txt"

To match where YOU uploaded it in Google Drive.


STEP 6: Run All Cells
----------------------
1. Click: Runtime → Run all
2. When prompted, allow Colab to access Google Drive
3. Training will start automatically

The notebook will:
- Install dependencies (2 min)
- Load corpus (5 min)
- Tokenize (20-30 min)
- Train (6-8 hours)
- Save model automatically


STEP 7: Monitor Progress
-------------------------
You can:
- Close the tab (training continues)
- Check back periodically
- Download model when done

Colab will show progress bars and ETA.


STEP 8: Get Your Trained Model
-------------------------------
When training completes:

Option A: Download from Colab
- Run the final cell (Download Model)
- Model downloads as .zip file
- Unzip on your Mac

Option B: Get from Google Drive
- Model auto-saves to: MyDrive/eebo_bert_finetuned/
- Download from Drive to your Mac


STEP 9: Use the Model Locally
------------------------------
Once downloaded, move to:
~/Repos/AI Project/Data/Historical_Embeddings/EEBO_1595-1700/eebo_bert_finetuned/

Then you can use it for poem analysis!


========================================
  COST BREAKDOWN
========================================

Google Colab Pro: $9.99/month
- Can cancel immediately after training
- Total cost for this project: ~$10

Compared to:
- MacBook Max upgrade: $2,000+
- Your Air would take: 40-50 hours


========================================
  TROUBLESHOOTING
========================================

"Runtime disconnected"
→ Colab free has time limits
→ With Pro, this shouldn't happen
→ If it does, just "Run all" again

"Out of memory error"
→ Reduce BATCH_SIZE from 8 to 4
→ In Cell 4, change: BATCH_SIZE = 4

"Can't find corpus file"
→ Check CORPUS_PATH in Cell 4
→ Must match Google Drive location

Upload taking forever?
→ 7.6GB upload can take 15-20 min
→ Make sure good internet connection


========================================
  NEED HELP?
========================================

Just ask me! I can help with:
- Fixing errors
- Adjusting settings
- Downloading the model
- Using it for analysis

Let me know when you get to each step.


========================================
