import pandas as pd
import argparse
import json
from collections import Counter


def empty_error(x):
    return len(x["result"]["error"]) == 0

parser = argparse.ArgumentParser("report stats")
parser.add_argument("file", help="csv file", type=str)
args = parser.parse_args()


df = pd.read_csv(args.file, sep='\t')

rule_implemented_count = df['rule_implemented'].value_counts()

processing_errors = df[~df['processingError'].isna()]
processing_errors_count = processing_errors['processingError'].value_counts()
deny_results = df[df['deny'] == True]
deny_results_no_rule = deny_results[deny_results['rule_implemented'] == '{}']
deny_results_no_rule['policyResult'] = deny_results_no_rule['policyResult'].apply(json.loads)
errors = []
for index, row in deny_results_no_rule.iterrows():
    errors += row['policyResult']["result"]["error"]
errors_count = Counter(errors)
deny_results_no_rule_no_error = deny_results_no_rule[deny_results_no_rule['policyResult'].apply(empty_error)]


print("--------------REPORT----------------")
print("File: ", args.file)
print("Total number of records: ", len(df.index))
print("Processing errors: ", processing_errors.shape[0])
print("Deny records (deny flag = true): ", deny_results.shape[0])
print("Deny records with no rule (error or policy gap): ", deny_results_no_rule.shape[0])
print("     Found errors (one record can have multiple errors): ")
for key,value in sorted(errors_count.items()):
    print("        ",key, value)
print("")

print("Deny records with no rule and no error (policy has a gap): ", deny_results_no_rule_no_error.shape[0])
print("    Users with policy gap: ")
print("\t"+(deny_results_no_rule_no_error["userId"].to_string(header=False,index=False).replace("\n","\t")))

print("")
print("Rule implemented: ")
print(rule_implemented_count.to_string(header=False))


print("")
print("Processing Errors: ")
for key,value in sorted(processing_errors_count.items()):
    print(key[:100], value)
    # print(key, value)

