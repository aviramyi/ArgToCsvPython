# Arg to CSV

This is python script is used to query Azure Resource Graph for security assessments, and store the results in a CSV file.

## Prerequisites

1. Install python and the relevant dependencies listed under queryArg.py
2. Make sure you are logged in to Azure using the Azure CLI
3. Execute the script using the following command:

```bash
python queryArg.py --params ./parameters.json
```

## Parameters

The parameters.json file should contain the following parameters:
{
    "subscription_ids": a list of subscription ids,
    "query": the query to be executed, currently set to fetch security assessments just like the CSV export button in the Azure portal,
    "export_file_path": the path where the CSV file will be stored
}

## Output

The script will generate a CSV file with the results of the query.