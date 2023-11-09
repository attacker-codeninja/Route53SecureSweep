import os
import boto3
import json
import multiprocessing
import dns.resolver
import dns


def fetch_route53_data():
    route53 = boto3.client('route53')

    try:
        # Retrieve the list of hosted zones
        route53_paginator = route53.get_paginator('list_hosted_zones')
        route53_zone_loop = route53_paginator.paginate()
        zones_found = False
        for page in route53_zone_loop:
            aws_zone = page["HostedZones"]
            for zone in aws_zone:
                zones_found = True
                zone_type = zone["Config"]['PrivateZone']
                if not zone_type:  # Public Zone
                    try:
                        # Retrieve the resource record sets for the hosted zone
                        page_records = route53.get_paginator('list_resource_record_sets')
                        zone_records = page_records.paginate(HostedZoneId=zone['Id'])
                        for records in zone_records:
                            for sub in records["ResourceRecordSets"]:
                                # Save Route53 subdomains
                                with open("route53_results/route53_subdomains.txt", "a") as route53_subdomains:
                                    route53_subdomains.write(f'{sub["Name"]}\n')
                        # Sort route53 results
                        os.system("sort -u route53_results/route53_subdomains.txt > route53_results/sorted_route53_subdomains.txt")
                    except Exception as error:
                        with open("error/r53_error_log.txt", "a") as error_log:
                            error_log.write(str(error))
                        raise error
        if not zones_found:
            print("No zones found in the AWS account")
            with open("error/r53_error_log.txt", "a") as error_log:
                error_log.write("No zones found in the AWS account")
            with open("route53_results/sorted_route53_subdomains.txt", "w") as route53_subdomains:
                # Create an empty file
                pass  

        # Call resolve_dns_records function
        resolve_dns_records("route53_results/sorted_route53_subdomains.txt")

    except Exception as error:
        with open("error/r53_error_log.txt", "a") as error_log:
            error_log.write(str(error))
        raise error
    
def resolve_dns_records(subdomain_file):
    with open(subdomain_file, "r") as f:
        subdomains = f.read().splitlines()

    for sub in subdomains:
        # Resolve A records
        try:
            result = dns.resolver.resolve(sub, 'A')
            with open("route53_results/unsorted_ips.txt", "a") as resolved_ips:
                for val in result:
                    resolved_ips.write(f'{val}\n')
            # Sort A records
            os.system("sort -u route53_results/unsorted_ips.txt > route53_results/sorted_ips.txt")

        except dns.resolver.NXDOMAIN:
            # Save NXDOMAIN subdomains
            with open("route53_results/unsorted_nxdomains.txt", "a") as nxdomain_subdomains:
                nxdomain_subdomains.write(f'{sub}\n')
            # Sort NXDOMAIN subdomains
            os.system("sort -u route53_results/unsorted_nxdomains.txt > route53_results/sorted_nxdomains.txt")


        except dns.resolver.NoAnswer:
            # Save NoAnswer subdomains
            with open("route53_results/unsorted_noanswer_subdomains.txt", "a") as no_dns_subdomains:
                no_dns_subdomains.write(f'{sub}\n')
            # Sort NoAnswer subdomains
            os.system("sort -u route53_results/unsorted_noanswer_subdomains.txt > route53_results/sorted_noanswer_subdomains.txt")

        # Resolve CNAME records
        try:
            cname_result = dns.resolver.resolve(sub, 'CNAME')
            with open("route53_results/unsorted_cname_records.txt", "a") as cname_records:
                for val in cname_result:
                    cname_records.write(f'{val}\n')
            # Sort CNAME records
            os.system("sort -u route53_results/unsorted_cname_records.txt > route53_results/sorted_cname_records.txt")

        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass

        # Resolve AAAA records
        try:
            aaaa_result = dns.resolver.resolve(sub, 'AAAA')
            with open("route53_results/unsorted_aaaa_records.txt", "a") as aaaa_records:
                for val in aaaa_result:
                    aaaa_records.write(f'{val}\n')
            # Sort AAAA records
            os.system("sort -u route53_results/unsorted_aaaa_records.txt > route53_results/sorted_aaaa_records.txt")

        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass

        # Resolve TXT records
        try:
            txt_result = dns.resolver.resolve(sub, 'TXT')
            with open("route53_results/unsorted_txt_records.txt", "a") as txt_records:
                for val in txt_result:
                    txt_records.write(f'{val}\n')
            # Sort TXT records
            os.system("sort -u route53_results/unsorted_txt_records.txt > route53_results/sorted_txt_records.txt")

        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass

        # Resolve MX records
        # Resolve MX records
        try:
            mx_result = dns.resolver.resolve(sub, 'MX')
            with open("route53_results/unsorted_mx_records.txt", "a") as mx_records:
                for val in mx_result:
                    mx_records.write(f'{val}\n')
            # Sort MX records
            os.system("sort -u route53_results/unsorted_mx_records.txt > route53_results/sorted_mx_records.txt")

        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass

def remove_unsorted_files():
    unsorted_files = [
        "route53_results/route53_subdomains.txt",
        "route53_results/unsorted_ips.txt",
        "route53_results/unsorted_nxdomains.txt",
        "route53_results/unsorted_noanswer_subdomains.txt",
        "route53_results/unsorted_cname_records.txt",
        "route53_results/unsorted_aaaa_records.txt",
        "route53_results/unsorted_txt_records.txt",
        "route53_results/unsorted_mx_records.txt"
    ]
    for file in unsorted_files:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    # Call the function
    fetch_route53_data()

    # Fetch Name from records
    #extract_names_from_json("route53_results/zone_records.json", "route53_results/zone_records.txt")

    # Remove unsorted filesz
    remove_unsorted_files()



