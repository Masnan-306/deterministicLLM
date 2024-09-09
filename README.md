## Prerequisites

- Azure Command Line (CLI)
- Terraform
- Docker
- Helm
- An ACR repo

## How to Run the Pipeline

1. **Source the Commands**

   Run the following command to deploy the LLM service in a single pod single node:

   ```bash
   source ./commands.sh
   ```

2. **Check the Service Endpoint**

   After deployment, you can view the endpoint with the following command:

   ```bash
   kubectl get svc
   ```

3. **Configure and Run the Test Script**

   - Based on the public IP address retrieved, update the configuration at the top of the `tests/send_requests.py` file.
   - Run the test script from the root directory:

     ```bash
     python test/send_requests.py
     ```
   - This will save a TSV file in the `outputs` directory where the file name should contain the relevant metadata like location and IP.
   
4. **Modify Parameters and Rerun the Pipeline**

   You can modify the location or other parameters and rerun the pipeline to generate multiple TSV outputs.

5. **Compare the Outputs**

   Use the following command to ensure the outputs are identical:



   ```bash
   python test/compare_tsv.py outputs/file1.tsv outputs/file2.tsv
   ```