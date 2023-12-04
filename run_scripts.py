import os
import shutil
from tqdm import tqdm
from route53 import fetch_route53_data, remove_unsorted_files
import subprocess
from datetime import datetime

# Set the URL and directory for nuclei templates repository
TEMPLATES_REPO_URL = "https://github.com/projectdiscovery/nuclei-templates.git"
TEMPLATES_REPO_DIR = "nuclei-templates"
nxdomains_file = 'route53_results/sorted_nxdomains.txt'
# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')




# Directory path
dir_path = 'final_results'


# Check if the directory exists
if not os.path.exists(dir_path):
    # If the directory does not exist, create it using mkdir
    os.makedirs(dir_path)
else:
    # If the directory exists, check if it is empty
    if os.listdir(dir_path):
        # If the directory is not empty, delete it and recreate it
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)
        
# Function to check if Go is installed and working
def check_go_installed():
    try:
        subprocess.run(["go", "version"], check=True, capture_output=True)
        print("✅ Go is installed and operational.")
    except FileNotFoundError:
        raise Exception("❌ Go is not detected. Please install Go and retry.")
    except subprocess.CalledProcessError:
        raise Exception("❌ Go is installed but not functioning correctly. Please verify the installation and retry.")



# Function to check if Nuclei is installed and working
def check_nuclei_installed():
    try:
        completed_process = subprocess.run(["nuclei", "-version"], check=True, capture_output=True, text=True)
        if "Nuclei Engine Version" in str(completed_process):
            print("Nuclei is installed and working.")
        else:
            raise Exception("Nuclei is installed but not working properly.")
    except FileNotFoundError:
        raise Exception("Nuclei is not installed. Please install Nuclei and try again.")
    except subprocess.CalledProcessError:
        raise Exception("Nuclei is installed but not working. Please check the installation and try again.")


# Function to check if Anew is installed and working
def check_anew_installed():
    try:
        result = subprocess.run(["anew", "-h"], check=True, capture_output=True, text=True)
        if "Usage of anew" in str(result):
            print("Anew is installed and working.")
        else:
            raise Exception("Anew is installed but not working. Please check the installation and try again.")
    except FileNotFoundError:
        raise Exception("Anew is not installed. Please install anew and try again.")
    except subprocess.CalledProcessError:
        raise Exception("An error occurred while checking the status of anew.")


# Function to check if Notify is installed and working
def check_notify_installed():
    try:
        subprocess.run(["notify", "-version"], check=True, capture_output=True)
        print("Notify is installed and working.")
    except FileNotFoundError:
        raise Exception("Notify is not installed. Please install Notify and try again.")
    except subprocess.CalledProcessError:
        raise Exception("Notify is installed but not working. Please check the installation and try again.")


# Function to check if Httpx is installed and working
def check_httpx_installed():
    try:
        result = subprocess.run(["httpx", "-version"], check=True, capture_output=True, text=True)
        if "Current Version" in str(result):
            print("Httpx is installed and working.")
        else:
            raise Exception("Httpx is installed but not working. Please check the installation and try again.")
    except FileNotFoundError:
        raise Exception("Httpx is not installed. Please install Httpx and try again.")
    except subprocess.CalledProcessError:
        raise Exception("An error occurred while checking the status of Httpx.")


# Function to clone the nuclei templates repository
def clone_templates_repo():
    # Check if the templates repository directory exists
    if os.path.exists(TEMPLATES_REPO_DIR):
        shutil.rmtree(TEMPLATES_REPO_DIR)

    try:
        print("Cloning nuclei-templates repository...")
        subprocess.run(["git", "clone", TEMPLATES_REPO_URL])
        print("Cloning completed successfully.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred while cloning nuclei-templates repository: {str(e)}")


# Function to check if the nuclei templates repository exists and clone it if not
def check_templates_repo():
    # Check if the templates repository directory exists
    if not os.path.exists(TEMPLATES_REPO_DIR):
        clone_templates_repo()
    else:
        print("nuclei-templates repository already exists. Skipping cloning.")


# Function to run additional scripts
def run_additional_scripts():
    try:
        # Execute apigateway_stages.sh
        subprocess.run(['bash', 'checks/apigateway_stages.sh'])

        # Execute eip_script.sh
        subprocess.run(['bash', 'checks/eip_script.sh'])

        # Execute elasticsearch.sh
        subprocess.run(['bash', 'checks/elasticsearch.sh'])

        # Execute lightsail.sh
        subprocess.run(['bash', 'checks/lightsail.sh'])

        # Execute neptunedb.sh
        subprocess.run(['bash', 'checks/neptunedb.sh'])

        # Execute rds.sh
        subprocess.run(['bash', 'checks/rds.sh'])

        # Execute cloudfront.sh
        subprocess.run(['bash', 'checks/cloudfront.sh'])

        # Execute elasticbeanstalk.sh
        subprocess.run(['bash', 'checks/elasticbeanstalk.sh'])

        # Execute globalaccelerator.sh
        subprocess.run(['bash', 'checks/globalaccelerator.sh'])

        # Execute loadbalancer.sh
        subprocess.run(['bash', 'checks/loadbalancer.sh'])

        # Execute publicip.sh
        subprocess.run(['bash', 'checks/publicip.sh'])

        # Execute redshift.sh
        subprocess.run(['bash', 'checks/redshift.sh'])
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred while running additional scripts: {str(e)}")


# Function to run Nuclei subdomain check
def run_nuclei_subdomain_check():
    try:
        run_nuclei_scan = "cat route53_results/sorted_route53_subdomains.txt | httpx -silent | nuclei -t nuclei-templates/http/takeovers -silent -o final_results/subdomain_takeover.txt"
        os.system(run_nuclei_scan)
        subprocess.run("cat route53_results/sorted_route53_subdomains.txt | httpx -silent > final_results/route53_subdomains.txt", shell=True, capture_output=True, text=True)

    except Exception as error:
        with open("error/r53_error_log.txt", "a") as error_log:
            error_log.write(str(error))
        raise error
    


#results/subdomain_fulldb_sorted.txt

# Function to process the assets and notify
def process_assets():
    try:
        # Notify with the current date
        subprocess.run(f"echo 'Date: {current_date}' | notify -silent -provider-config provider-config.yaml", shell=True)
        
        # Concatenate files and redirect output to subdomain_fulldb.txt
        subprocess.run("cat results/accelerator_ips.txt results/cf_domains.txt results/eb_domain.txt results/public_eips.txt results/public_ips.txt results/neptune_endpoints.txt results/public_ips.txt results/rds_domains.txt results/elasticsearch_endpoints.txt results/redshift_endpoints.txt results/http_apis.txt results/rest_apis.txt results/lightsail_ips.txt results/stale_eip.txt results/lb_domains.txt results/websocket_apis.txt route53_results/sorted_route53_subdomains.txt | anew subdomain_data.txt > results/subdomain_fulldb_sorted.txt && sort -u results/subdomain_fulldb_sorted.txt > final_results/subdomain_fulldb.txt", shell=True)

        # Notify separator line
        subprocess.run("echo '-------------Daily Route53 Scan Initiated--------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about total new assets
        subprocess.run("echo '------------------------Total Number of New AWS Assets Discovered:----------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True, capture_output=True, text=True)

        # Notify about total number of new assets discovered
        subprocess.run("echo 'Number of newly discovered assets in the AWS account today: '; wc -l < final_results/subdomain_fulldb.txt | awk '{$1=$1};1' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about subdomain data
        subprocess.run("cat final_results/subdomain_fulldb.txt | notify -silent -bulk -provider-config provider-config.yaml", shell=True)

        # Notify separator line
        subprocess.run("echo '------------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)
        subprocess.run("echo '------------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about total Subdomain takeovers
        subprocess.run("echo '-----------------------------Total Subdomain Takeovers-------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about total Subdomain takeovers
        subprocess.run("echo 'Number of Subdomain Takeovers Detected in AWS Account: '; wc -l < final_results/subdomain_takeover.txt | awk '{$1=$1};1' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about subdomain takeover data
        subprocess.run("cat final_results/subdomain_takeover.txt | notify -silent -bulk -provider-config provider-config.yaml", shell=True)

        # Notify separator line
        subprocess.run("echo '------------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)
        subprocess.run("echo '------------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about total NxDomains
        #file is part of exception, is created in case of nxdomain exception
        subprocess.run("echo '---------------------------Total Nxdomains--------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        if os.path.exists(nxdomains_file):
                # Notify about total NxDomains if file exists
            subprocess.run(f"echo 'Number of NxDomains Detected in AWS Account '; wc -l < {nxdomains_file} | awk '{{print $1}}' | notify -silent -provider-config provider-config.yaml", shell=True)
            subprocess.run(f"cat {nxdomains_file} | notify -silent -bulk -provider-config provider-config.yaml", shell=True)
        else:
            # If the file does not exist, pass word count as 0
            subprocess.run("echo 'Number of NxDomains Detected in AWS Account 0' | notify -silent -provider-config provider-config.yaml", shell=True)
        # If the file does not exist, ignore the cat command
        # You can optionally notify that the file was not found if needed
        # subprocess.run("echo 'sorted_nxdomains.txt file not found.' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify separator line
        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        subprocess.run("echo '----------Full Subdomains List----------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Notify about aws subdomain data via route53
        subprocess.run("cat final_results/subdomain_fulldb.txt | notify -silent -provider-config provider-config.yaml", shell=True)

        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)
        subprocess.run("echo -n '------------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

    except Exception as error:
        # Write the error to the error log file
        with open("error/r53_error_log.txt", "a") as error_log:
            error_log.write(str(error))
        raise error


# Function to run Nuclei full scan
def run_nuclei_full_scan():
    try:
        # Notify about starting the Nuclei full scan
        subprocess.run("echo '------------------------Starting Nuclei Full Scan-------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Perform Nuclei full scan
        #currently set to http in template to reduce the time, in reality run_nuclei_aws_scan scans for domains - cname & a record from route53, this includes all
        subprocess.run("cat final_results/subdomain_fulldb.txt | httpx -silent -ports 1-10000 -t 1000 -rate-limit 500 | nuclei -t nuclei-templates/http/ -silent -o final_results/subdomain_fullscan.txt", shell=True)

        # Notify about subdomain full scan
        subprocess.run("cat final_results/subdomain_fullscan.txt | notify -silent -bulk -provider-config provider-config.yaml", shell=True)

        # Notify separator line
        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)
        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

    except Exception as error:
        # Save the error to the error log
        with open("error/r53_error_log.txt", "a") as error_log:
            error_log.write(str(error))
        raise error

# Function to run Nuclei aws route53 public endpoint check
def run_nuclei_aws_scan():
    try:
        subprocess.run("echo '------------------------Starting Nuclei AWS Public Endpoint Scan-------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

        # Perform Nuclei full scan
        subprocess.run("cat final_results/route53_subdomains.txt | httpx -silent -ports 1-10000 -t 1000 -rate-limit 500 | nuclei -t nuclei-templates/http/ -silent -o final_results/aws_services_fulldb_scan.txt", shell=True)

        # Notify about subdomain full scan
        subprocess.run("cat final_results/aws_services_fulldb_scan.txt | notify -silent -bulk -provider-config provider-config.yaml", shell=True)

        # Notify separator line
        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)
        subprocess.run("echo '-----------------------------------------------------------------------------------------------------' | notify -silent -provider-config provider-config.yaml", shell=True)

    except Exception as error:
        with open("error/r53_error_log.txt", "a") as error_log:
            error_log.write(str(error))
        raise error
    

# Function to run the necessary scripts
def run_scripts():
    # Check if 'results' folder exists and delete it if present
    if os.path.exists("results"):
        shutil.rmtree("results")

    # Create the 'results' folder
    os.makedirs("results")

    # Check if 'route53_results' folder exists and delete it if present
    if os.path.exists("route53_results"):
        shutil.rmtree("route53_results")

    # Create the 'route53_results' folder
    os.makedirs("route53_results")

    # Create the 'error' folder if it doesn't exist
    if not os.path.exists("error"):
        os.makedirs("error")

    # Get the total number of steps for the progress bar
    total_steps = 13

    # Create a progress bar object
    progress_bar = tqdm(total=total_steps, unit="step")

    try:
        # Call the function to check if dependencies are installed
        check_go_installed()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to check if dependencies are installed
        check_nuclei_installed()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to check if dependencies are installed
        check_anew_installed()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to check if dependencies are installed
        check_notify_installed()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to check if dependencies are installed
        check_httpx_installed()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to fetch nuclei template data
        print("Fetching latest nuclei template.")
        check_templates_repo()
        # Update the progress bar
        progress_bar.update(1)

        # Call the function to fetch Route53 data
        print("Fetching route53 data.")
        fetch_route53_data()
        # Update the progress bar
        progress_bar.update(1)

        # Remove unsorted files
        remove_unsorted_files()
        # Update the progress bar
        progress_bar.update(1)

        # Run additional scripts
        print("Fetching all possible public endpoints from AWS.")
        run_additional_scripts()
        # Update the progress bar
        progress_bar.update(1)

        # Run Nuclei subdomain check
        print("Performing subdomain takeover scan via Nuclei")
        run_nuclei_subdomain_check()
        # Update the progress bar
        progress_bar.update(1)

        # Process assets and notify
        print("Sending results to Slack")
        process_assets()
        # Update the progress bar
        progress_bar.update(1)

        # Run Nuclei full scan
        print("Performing Nuclei public aws services scan")
        run_nuclei_aws_scan()
        # Update the progress bar
        progress_bar.update(1)
        

        # Run Nuclei full scan
        print("Performing Nuclei full scan")
        run_nuclei_full_scan()
        # Update the progress bar
        progress_bar.update(1)

    except Exception as error:
        # Print the error message
        print(f"An error occurred: {str(error)}")
        # Create an error log file
        with open("error/error_log.txt", "a") as error_log:
            error_log.write(str(error))

    finally:
        # Close the progress bar
        progress_bar.close()


# Call the function to run the scripts
if __name__ == "__main__":
    run_scripts()
