# Depositing Data into the COGS Archive

This guide explains how to deposit a dataset into the **COGS Data Archive** using the
provided publication script. You do **not** need to understand Zenodo, APIs, or Python
internals to follow these steps.

If you can prepare a clean dataset directory and run one command, you can deposit data.

---

## What this does (high level)

When you deposit a dataset:

- Your data are archived on **Zenodo**
- A **DOI** (permanent identifier) is created
- The dataset becomes publicly accessible
- The dataset is indexed in the COGS registry for reproducibility

You will receive a DOI that you can cite in papers.

---

## Important note on permissions and approval (read this first)

COGS datasets are published to a **curated Zenodo community**. This means:

- Students **do not need** permission to make data public on their own
- Students **do not receive** curator privileges
- All submissions to the COGS community are **reviewed and approved by a curator**

There are two common workflows:

1. **Curator-published (default)**
   - Students prepare the dataset and ZIP file
   - A curator runs the deposit command and publishes the dataset

2. **Student-submitted, curator-approved**
   - Students have their own Zenodo accounts
   - Students are added as *members* of the COGS community
   - Students run the deposit command using their own Zenodo token
   - The dataset appears as *pending* until a curator approves it

In all cases, **nothing becomes public without curator approval**.

If you are unsure which workflow applies to you, ask a COGS curator before proceeding.

---

## What you need before starting

You must have:

1. A directory containing your dataset
2. A `README.md` inside that directory
3. All files you want to archive (e.g. CSVs)
4. Access to the `dev-cogs-archive` repository
5. Permission from a COGS curator to publish or submit

You **do not** need:
- Curator privileges on Zenodo
- To share or receive anyone else’s Zenodo token
- To edit Python source code

---

## Example dataset: QCEW 2024

In this example, the dataset consists of:

```
datasets/qcew/
├── README.md
└── qcew_2024_bea409_counties.csv
```

This directory has already been prepared and reviewed.

---

## Step 1: Zip your dataset directory

From the root of the repository (`dev-cogs-archive`):

```
cd dev-cogs-archive
```

Create a ZIP file that contains the **directory**, not just the files inside it:

```
zip -r datasets/qcew_v1.0.0.zip datasets/qcew/
```

After this step, you should have:

```
datasets/qcew_v1.0.0.zip
```

---

## Step 2: Check that the ZIP file exists

```
ls -lh datasets/qcew_v1.0.0.zip
```

You should see the file size (around 90–100 MB in this example).

---

## Step 3: Run the deposit script

From the **root of the repository**, run:

```
python scripts/publish_qcew.py   --dataset-id qcew_2024_bea409   --version 1.0.0   --zip datasets/qcew_v1.0.0.zip
```

Important:
- Always run this command from the `dev-cogs-archive` directory
- Do not rename flags or add extra arguments
- If this command fails, copy the error message and send it to a curator

---

## Step 4: Confirm success

If the deposit is successful, you will see output like:

```
SUCCESS
Dataset ID: qcew_2024_bea409
DOI: 10.5281/zenodo.18407869
Concept DOI: 10.5281/zenodo.18407868
Record ID: 18407869
```

This means:

- Your dataset has been deposited on Zenodo
- A permanent DOI has been created
- The dataset is either public (if curator-published) or pending approval
- The dataset is registered with COGS

---

## Step 5: Save the DOI (very important)

Copy and save the **DOI**:

```
10.5281/zenodo.18407869
```

You will use this DOI in:
- papers
- theses
- dissertations
- presentations
- data availability statements

If the dataset is pending approval, do not cite the DOI until a curator confirms approval.

---

## Step 6: Verify the dataset (optional but recommended)

Once approved, open a web browser and go to:

```
https://zenodo.org/record/18407869
```

Check that:
- The dataset title is correct
- The ZIP file is present
- The license is correct
- The dataset belongs to the **COGS** community

---

## Versioning rules

- `1.0.0` → first public release
- `1.1.0` → additional data or small corrections
- `2.0.0` → major changes or restructuring

Once a version is published, it **cannot be changed**.

---

## Common mistakes to avoid

- Uploading individual files instead of a ZIP
- Forgetting to include a `README.md`
- Running the script from the wrong directory
- Renaming or editing the script
- Sharing Zenodo tokens
- Committing ZIP files to git

---

## If something goes wrong

Do **not** try to fix it yourself.

Instead, send the curator:
- The command you ran
- The full error message
- The name of your ZIP file

They will help you resolve it.

---

## Summary

1. Prepare dataset directory  
2. Include a `README.md`  
3. Zip the directory  
4. Run **one command**  
5. Save the DOI and wait for approval if required  

That’s it.
