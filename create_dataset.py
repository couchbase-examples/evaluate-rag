example_questions = [
    "What is Couchbase Autonomous Operator?",
    "How can I connect to Couchbase Capella using the Python SDK?",
    "I get an UnambiguousTimeoutError when trying to connect to Couchbase Capella. What could be the issue?",
    "How can I perform Vector Search in Python?",
    "How can I whitelist an IP in Capella?",
    "What are the new additions to SQL++ in Couchbase Server 7.6?",
    "What does setting a collection’s maxTTL to -1 do?",
    "How can I create a Capella cluster programmatically?",
    "How can I create a Vector Search index quickly in Capella?",
    "How can I import CSV documents into my Couchbase cluster?",
]

ground_truth_answers = [
    "Couchbase Autonmous Operator is an integration of Couchbase Server with open source Kubernetes and Red Hat OpenShift thatenables you to automate the management of common Couchbase tasks such as the configuration, creation, scaling, and recovery of Couchbase clusters",
    """To connect to Couchbase Capella, be sure to get the correct endpoint as well as user, password, and bucket name. The certificate for connecting to Capella is included in the 4.1 Python SDK.
from datetime import timedelta

# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions)


# Update this to your cluster
endpoint = "--your-instance--.dp.cloud.couchbase.com"
username = "username"
password = "Password!123"
bucket_name = "travel-sample"
# User Input ends here.

# Connect options - authentication
auth = PasswordAuthenticator(username, password)

# get a reference to our cluster
options = ClusterOptions(auth)
# Sets a pre-configured profile called "wan_development" to help avoid latency issues
# when accessing Capella from a different Wide Area Network
# or Availability Zone(e.g. your laptop).
options.apply_profile('wan_development')
cluster = Cluster('couchbases://{}'.format(endpoint), options)

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))

# get a reference to our bucket
cb = cluster.bucket(bucket_name)

cb_coll = cb.scope("inventory").collection("airline")



def upsert_document(doc):
    print("\nUpsert CAS: ")
    try:
        # key will equal: "airline_8091"
        key = doc["type"] + "_" + str(doc["id"])
        result = cb_coll.upsert(key, doc)
        print(result.cas)
    except Exception as e:
        print(e)

# get document function


def get_airline_by_key(key):
    print("\nGet Result: ")
    try:
        result = cb_coll.get(key)
        print(result.content_as[str])
    except Exception as e:
        print(e)

# query for new document by callsign


def lookup_by_callsign(cs):
    print("\nLookup Result: ")
    try:
        inventory_scope = cb.scope('inventory')
        sql_query = 'SELECT VALUE name FROM airline WHERE callsign = $1'
        row_iter = inventory_scope.query(
            sql_query,
            QueryOptions(positional_parameters=[cs]))
        for row in row_iter:
            print(row)
    except Exception as e:
        print(e)


airline = {
    "type": "airline",
    "id": 8091,
    "callsign": "CBS",
    "iata": None,
    "icao": None,
    "name": "Couchbase Airways",
}

upsert_document(airline)

get_airline_by_key("airline_8091")

lookup_by_callsign("CBS")
""",
    "UnambiguousTimeout is raised when a timeout occurs and we are confident that the operation could not have succeeded. This normally would occur because we received confident failures from the server, or never managed to successfully dispatch the operation. It can occur due to network latencies, DNS issues, TLS configuration issues or Timeout settings in the SDK configuration. To diagnose the issue, it is recommended to run SDK Doctor.",
    """
In this first example we are performing a single vector query:
# NOTE: new imports needed for vector search
from couchbase.vector_search import VectorQuery, VectorSearch

vector_search = VectorSearch.from_vector_query(VectorQuery('vector_field',
                                                           query_vector))
request = search.SearchRequest.create(vector_search)
result = scope.search('vector-index', request)

Let’s break this down. We create a SearchRequest, which can contain a traditional FTS query SearchQuery and/or the new VectorSearch. Here we are just using the latter.

The VectorSearch allows us to perform one or more VectorQuery s.

The VectorQuery itself takes the name of the document field that contains embedded vectors ("vector_field" here), plus actual vector query in the form of a float[].

(Note that Couchbase itself is not involved in generating the vectors, and these will come from an external source such as an embeddings API.)

Finally we execute the SearchRequest against the FTS index "vector-index", which has previously been setup to vector index the "vector_field" field.

This happens to be a scoped index so we are using scope.search(). If it was a global index we would use cluster.search() instead - see Scoped vs Global Indexes.

It returns the same SearchResult detailed earlier.

""",
    """
Allowed IPs can be viewed and managed from the cluster maintenance page:

Select the project containing the cluster from the project list.

Select the cluster you wish to examine from the Operational Clusters screen.

Select the Settings tab, then Networking from the left-hand menu.
""",
    """
SQL++ language additions:

OFFSET clause added to the DELETE statement. See DELETE.

GROUP AS clause added to the GROUP BY clause. See GROUP BY Clause.

FORMALIZE() function. See FORMALIZE().

Multi-byte aware string functions. See String Functions.

Support for sequences. See Sequence Operators.

EXPLAIN FUNCTION statement. See EXPLAIN FUNCTION.
""",
    """Seting a collection’s maxTTL to -1 to prevent a bucket’s non-zero maxTTL setting from causing documents in the collection to expire automatically. This new setting is useful if you want most of the documents in a bucket to automatically expire, but want to prevent the documents in one or more collections from expiring by default.
""",
    """
In order to create a Capella cluster programmatically, you need to use the Capella Management API. You can call the following endpoint to create a cluster:
Create a POST request to the following endpoint https://cloudapi.cloud.couchbase.com/v4/organizations/{organizationId}/projects/{projectId}/clusters using the follwoing JSON payload:
{
  "name": "Test-Cluster-5",
  "description": "My first test GCP cluster.",
  "cloudProvider": {
    "type": "gcp",
    "region": "us-east1",
    "cidr": "10.1.30.0/23"
  },
  "couchbaseServer": {
    "version": "7.2"
  },
  "serviceGroups": [
    {
      "node": {
        "compute": {
          "cpu": 4,
          "ram": 16
        },
        "disk": {
          "storage": 64,
          "type": "pd-ssd"
        }
      },
      "numOfNodes": 3,
      "services": [
        "data",
        "query",
        "index",
        "search"
      ]
    }
  ],
  "availability": {
    "type": "single"
  },
  "support": {
    "plan": "basic",
    "timezone": "ET"
  }
}
""",
    """
To create a Vector Search index with Quick Mode in Capella:

On the Operational Clusters page, select the cluster where you want to create a Search index.

Go to Data Tools  Search.

Click Create Search Index.

By default, Quick Mode should be on.

In the Index Name field, enter a name for the Vector Search index.

Your index name must start with an alphabetic character (a-z or A-Z). It can only contain alphanumeric characters (a-z, A-Z, or 0-9), hyphens (-), or underscores (_).

For Couchbase Server version 7.6 and later, your index name must be unique inside your selected bucket and scope. You cannot have 2 indexes with the same name inside the same bucket and scope.

Under Type Mappings, in the Bucket list, select the bucket that contains the documents you want to include in your index.

In the Scope list, select the scope that contains these documents.

Expand the collection that contains these documents.

In your document schema, select the child field that contains your vector embeddings.

Configure the options for the child field as follows:

In the Type list, select one of the following:

If your child field contains vector embeddings as an array, click vector.

Vector embeddings formatted as arrays appear as {field-name} [ number ] in the Capella Quick Mode editor.

(Couchbase Server version 7.6.2 or later) If your child field contains vector embeddings formatted as a base64 encoded string, click vector_base64.

Vector embeddings formatted as base64 strings appear as {field-name} [ string ] in the Capella Quick Mode editor.

In the Dimension field, check that the value matches the total number of elements in your vector embeddings array.

The Search Service supports arrays up to 2048 elements. Capella automatically fills in the dimension value for your selected child field when you choose the vector or vector_base64 type.

In the Similarity metric list, choose the method to use to calculate the similarity between search term and Search index vectors.

For more information, see Quick Field Type Mapping Options.

In the Optimized for list, choose whether the Search Service should optimize Search queries for accuracy (recall) or speed (latency).

For more information, see Quick Field Type Mapping Options.

Select Index.

Click Submit.

(Optional) Add additional collections or child field type mappings to your index.

For example, you could add the text field that you used to generate your vector embeddings.

Click Create Index.

""",
    """
cbimport can be used to import CSV and other forms of separated value type data into Couchbase. By default data files should contain comma separated values, but if for example you are importing data that is tab separated you can use the --field-separator flag to specify that tabs are used instead of commas.

The cbimport command also supports custom key-generation for each document in the imported file. Key generation is done with a combination of pre-existing fields in a document and custom generator functions supplied by cbimport.
Usage
cbimport csv [--cluster <url>] [--bucket <bucket_name>] [--dataset <path>]
             [--username <username>] [--password <password>] [--client-cert <path>]
             [--client-cert-password <password>] [--client-key <path>]
             [--client-key-password <password>] [--generate-key <key_expr>]
             [--limit-rows <num>] [--skip-rows <num>] [--field-separator <char>]
             [--cacert <path>] [--no-ssl-verify] [--threads <num>]
             [--error-log <path>] [--log-file <path>] [--verbose]
             [--field-delimiter <char>] [--generator-delimiter <char>]
             [--ignore-fields <fields>]
             [--scope-collection-exp <scope_collection_expression>]
""",
]
