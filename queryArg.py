import sys
import json
import logging
import pandas
import azure.mgmt.resourcegraph
from azure.identity import DefaultAzureCredential
from argparse import ArgumentParser

# Create logger
def create_logger():
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]

    # create logger configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers = handlers
    )

# Create Resource Graph request
def resource_request(subscription_ids,query,page_token=None):
    logging.info("Creating query option and query request...")

    # Configure query options
    queryoption = azure.mgmt.resourcegraph.models.QueryRequestOptions(
        skip_token = page_token
    )

    # Configure query request
    queryrequest = azure.mgmt.resourcegraph.models.QueryRequest(
        subscriptions = subscription_ids,
        query = query,
        options = queryoption
    )
    return queryrequest

# Main function
def main():
    try:
        create_logger()
        logging.info("Starting script...")

        parser = ArgumentParser()
        parser.add_argument('--params', type=str, help='JSON file with required parameters', required=True)
        args = parser.parse_args()

        # Load JSON file with parameters
        with open(args.params) as params_json:
            config = json.load(params_json)
        
        # Check for required parameters
        if 'subscription_ids' not in config:
            logging.error("Missing subscription_ids parameter")
            sys.exit(1)
        if 'query' not in config:
            logging.error("Missing query parameter")
            sys.exit(1)
        if 'export_file_path' not in config:
            logging.error("Missing export_file_path parameter")
            sys.exit(1)

        # Create DefaultAzureCredential object
        logging.info("Creating Azure credential object...")
        credential = DefaultAzureCredential()

        # Setup the Resource Graph connection and issue the query
        client = azure.mgmt.resourcegraph.ResourceGraphClient(credential)

        logging.info("querying Azure Resource Graph...")
        result = client.resources(
            query=resource_request(subscription_ids=config['subscription_ids'],query=config['query']),
        )

        # Create DataFrame to store results
        df_results = pandas.DataFrame(result.data)
        result_count = result.count
        logging.info("Retrieved " + str(result_count) + " records")


        # Get all pages of results
        while result.skip_token != None:
            logging.info("Retrieving " + str(result.count) + " paged records")
            result = client.resources(
                query=resource_request(subscription_ids=config['subscription_ids'],query=config['query'],page_token=result.skip_token)
            )
            # Append new records to DataFrame
            df_results = pandas.concat([df_results, pandas.DataFrame(result.data)], ignore_index = True)
            result_count += result.count
        df_results.to_json(orient='records')

        # save to .csv file
        df_results.to_csv(config['export_file_path'], index=False)

    except Exception as e:
        logging.error(e)
        sys.exit(1)
       
# Run main function
if __name__ == "__main__":
    main()